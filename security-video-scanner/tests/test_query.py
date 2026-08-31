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
    ("מתי הרכב הלבן זז", ["car"]),
    ("when did the white car move", ["car"]),
    ("איש עם חולצה לבנה", ["person"]),
    ("a man in a white shirt", ["person"]),
    ("מישהו משאיר תיק ליד הכניסה", ["handbag"]),
])
def test_a_description_or_an_action_needs_the_model(query, fallback):
    """'car' is an object; 'the white car moved' is not - colour and movement
    are not in the detector's vocabulary."""
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
