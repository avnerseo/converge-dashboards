"""Reading the operator's intent - the difference between answering their
question and quietly answering a different one."""
from __future__ import annotations

import pytest

from vscan.query import resolve

PEOPLE = [(1, "דוד"), (2, "Courier"), (3, "Anna Lee")]


@pytest.mark.parametrize("query,labels", [
    ("car", ["car"]),
    ("רכב", ["car"]),
    ("הרכב", ["car"]),                       # Hebrew glues the article on
    ("מתי רואים רכב", ["car"]),
    ("dog", ["dog"]),
    ("person and car", ["person", "car"]),
])
def test_plain_object_words_go_to_the_local_detector(query, labels):
    intent = resolve(query, PEOPLE)
    assert intent.mode == "objects"
    assert intent.labels == labels


@pytest.mark.parametrize("query,fallback", [
    ("מישהו משאיר תיק ליד הכניסה", ["handbag"]),
    ("איש עם כובע", ["person"]),
    ("a person carrying a ladder", ["person"]),
])
def test_what_the_detectors_cannot_measure_needs_the_model(query, fallback):
    """Colour and movement are measured at index time and stay local. What is
    left - relationships, actions, clothing we do not measure - needs a look at
    the frames, and offers the nearest local search as a stopgap."""
    intent = resolve(query, PEOPLE)
    assert intent.mode == "ask", intent.reason
    assert intent.fallback is not None and intent.fallback.labels == fallback


@pytest.mark.parametrize("query,name", [
    ("דוד", "דוד"),
    ("מתי דוד הגיע", "דוד"),
    ("Courier", "Courier"),
    ("where is Anna Lee", "Anna Lee"),
])
def test_an_enrolled_name_wins(query, name):
    intent = resolve(query, PEOPLE)
    assert intent.mode == "person" and intent.person_name == name


def test_a_name_that_is_not_enrolled_is_not_a_person_search():
    assert resolve("מתי משה הגיע", PEOPLE).mode == "ask"


def test_the_most_specific_name_wins():
    people = [(1, "Anna"), (2, "Anna Lee")]
    assert resolve("Anna Lee at the gate", people).person_name == "Anna Lee"


def test_empty_query_is_not_a_crash():
    assert resolve("   ", PEOPLE).mode == "ask"


def test_every_intent_explains_itself():
    for query in ("car", "דוד", "מתי הרכב הלבן זז"):
        assert resolve(query, PEOPLE).reason, f"{query} came back with no reason"


@pytest.mark.parametrize("query,labels,colours,moving", [
    ("מתי הרכב הלבן זז", ["car"], ["white"], True),
    ("when did the white car move", ["car"], ["white"], True),
    ("איש עם חולצה לבנה", ["person"], ["white"], None),
    ("a man in a white shirt", ["person"], ["white"], None),
    ("רכב חונה", ["car"], [], False),
    ("אדם עם תיק שחור", ["person", "handbag"], ["black"], None),
])
def test_colour_and_movement_stay_local(query, labels, colours, moving):
    """Colour and movement are measured while indexing, so questions about
    them are answered locally - not by paying for a look at the frames."""
    intent = resolve(query, PEOPLE)
    assert intent.mode == "objects", intent.reason
    assert intent.labels == labels
    assert intent.colours == colours
    assert intent.moving is moving


def test_what_is_genuinely_beyond_the_detectors_still_goes_to_the_model():
    for query in ("מישהו משאיר תיק ליד הכניסה", "איש עם כובע",
                  "someone acting suspiciously"):
        assert resolve(query, PEOPLE).mode == "ask", query
