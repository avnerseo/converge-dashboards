"""Work out what an operator meant, so they never have to pick a search mode.

Someone investigating an incident types "when did the white car move" or
"David" or "a man in a white shirt". Three different engines answer those, and
choosing between them is our job, not theirs:

  * a name we have enrolled            -> face and appearance search, local
  * nothing but object words           -> object search, local
  * anything with a colour, an action,
    a relationship, a description      -> instruction search, via the model

The third case is the interesting one. "car" is an object the local detector
knows; "the white car moved" is not - colour and movement are not in its
vocabulary - so sending that to object search would quietly answer a different
question than the one that was asked.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .objects import COCO_CLASSES

# Words that carry no search meaning on their own.
STOPWORDS = {
    # Hebrew
    "מתי", "איפה", "האם", "יש", "היה", "היתה", "רואים", "לראות", "ראו", "תראה",
    "מצא", "תמצא", "למצוא", "את", "של", "כל", "עם", "בלי", "או", "וגם", "גם",
    "ה", "ב", "ל", "מ", "ו", "אני", "רוצה", "לי", "תגיד", "תראי", "בסרטון",
    "בהקלטה", "במצלמה", "מופיע", "מופיעה", "נמצא",
    # English
    "when", "where", "did", "does", "do", "is", "are", "was", "were", "the",
    "a", "an", "any", "show", "me", "find", "search", "for", "of", "in", "on",
    "at", "with", "without", "and", "or", "please", "someone", "something",
    "video", "footage", "camera", "appear", "appears", "there",
}

# Everyday words for the classes the local detector actually knows.
SYNONYMS: dict[str, str] = {
    # people
    "person": "person", "people": "person", "man": "person", "woman": "person",
    "men": "person", "women": "person", "child": "person", "kid": "person",
    "אדם": "person", "איש": "person", "אישה": "person", "אנשים": "person",
    "בנאדם": "person", "ילד": "person", "ילדה": "person", "אנשי": "person",
    # vehicles
    "car": "car", "cars": "car", "vehicle": "car", "רכב": "car", "מכונית": "car",
    "אוטו": "car", "רכבים": "car", "מכוניות": "car",
    "truck": "truck", "van": "truck", "משאית": "truck", "טנדר": "truck",
    "bus": "bus", "אוטובוס": "bus",
    "motorcycle": "motorcycle", "motorbike": "motorcycle", "scooter": "motorcycle",
    "אופנוע": "motorcycle", "קטנוע": "motorcycle",
    "bicycle": "bicycle", "bike": "bicycle", "אופניים": "bicycle",
    # carried things
    "bag": "handbag", "handbag": "handbag", "תיק": "handbag", "תיקים": "handbag",
    "backpack": "backpack", "תרמיל": "backpack", "ילקוט": "backpack",
    "suitcase": "suitcase", "מזוודה": "suitcase",
    "umbrella": "umbrella", "מטרייה": "umbrella",
    "phone": "cell phone", "טלפון": "cell phone", "נייד": "cell phone",
    "laptop": "laptop", "מחשב": "laptop",
    # animals
    "dog": "dog", "כלב": "dog", "cat": "cat", "חתול": "cat",
}
for _label in COCO_CLASSES:                     # every class answers to its own name
    SYNONYMS.setdefault(_label, _label)

# Words that mean the question is about description or change, not presence.
# The local detectors cannot answer these, whatever nouns sit beside them.
DESCRIPTIVE = {
    # colours
    "white", "black", "red", "blue", "green", "yellow", "grey", "gray", "silver",
    "לבן", "לבנה", "שחור", "שחורה", "אדום", "אדומה", "כחול", "כחולה", "ירוק",
    "צהוב", "אפור", "אפורה", "כסוף", "חום", "ורוד",
    # clothing and appearance
    "shirt", "jacket", "coat", "hat", "cap", "mask", "hood", "uniform", "suit",
    "חולצה", "מעיל", "ג'קט", "כובע", "מסכה", "קפוצ'ון", "מדים", "חליפה", "שמלה",
    # movement and events
    "moved", "moves", "moving", "left", "leaves", "leaving", "arrived", "arrives",
    "entered", "enters", "exit", "exits", "took", "takes", "carrying", "carries",
    "drops", "dropped", "running", "runs", "fell", "opened", "closed", "parked",
    "זז", "זזה", "נע", "נעה", "עזב", "עזבה", "הגיע", "הגיעה", "נכנס", "נכנסה",
    "יצא", "יצאה", "לקח", "לקחה", "נושא", "נושאת", "משאיר", "השאיר", "רץ",
    "נפל", "פתח", "סגר", "חונה", "החנה", "עצר", "עצרה", "נגע",
}

_TOKEN = re.compile(r"[\w'֐-׿]+", re.UNICODE)
# Hebrew glues its articles and prepositions onto the word: "הרכב" is "the car".
_HE_PREFIXES = ("ה", "ו", "ב", "ל", "מ", "ש", "כ", "וה", "שה", "כש")


def strip_prefix(word: str) -> list[str]:
    """The word itself, and what is left after a Hebrew article or preposition."""
    forms = [word]
    for prefix in _HE_PREFIXES:
        if word.startswith(prefix) and len(word) - len(prefix) >= 2:
            forms.append(word[len(prefix):])
    return forms


def _lookup(word: str, table) -> str | None:
    for form in strip_prefix(word):
        if form in table:
            return table[form] if isinstance(table, dict) else form
    return None


@dataclass
class Intent:
    """What we decided the operator meant, and why.

    `reason` is English prose for logs and the CLI. `reason_code` and
    `reason_word` are what a localised interface renders, so an operator
    working in Hebrew is not handed an English sentence.
    """
    mode: str                                   # 'person' | 'objects' | 'ask'
    query: str
    person_id: int | None = None
    person_name: str | None = None
    labels: list[str] = field(default_factory=list)
    reason: str = ""
    reason_code: str = ""
    reason_word: str = ""
    fallback: "Intent | None" = None            # nearest local search, for 'ask'

    def to_dict(self) -> dict:
        data = {"mode": self.mode, "query": self.query, "person_id": self.person_id,
                "person_name": self.person_name, "labels": self.labels,
                "reason": self.reason, "reason_code": self.reason_code,
                "reason_word": self.reason_word}
        data["fallback"] = self.fallback.to_dict() if self.fallback else None
        return data


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").strip().lower()
    return re.sub(r"\s+", " ", text)


def tokens_of(text: str) -> list[str]:
    out = []
    for tok in _TOKEN.findall(_normalise(text)):
        if tok in STOPWORDS or any(form in STOPWORDS for form in strip_prefix(tok)):
            continue
        out.append(tok)
    return out


def match_person(query: str, persons: list[tuple[int, str]]) -> tuple[int, str] | None:
    """An enrolled name mentioned in the query wins over everything else."""
    text = _normalise(query)
    best: tuple[int, str] | None = None
    for person_id, name in persons:
        clean = _normalise(name)
        if len(clean) < 2:
            continue
        if clean == text or re.search(rf"(?<!\w){re.escape(clean)}(?!\w)", text):
            if best is None or len(clean) > len(_normalise(best[1])):
                best = (person_id, name)        # prefer the most specific name
    return best


def resolve(query: str, persons: list[tuple[int, str]] | None = None) -> Intent:
    """Turn a sentence into the search that actually answers it."""
    persons = persons or []
    text = _normalise(query)
    if not text:
        return Intent("ask", query, reason="empty query")

    person = match_person(query, persons)
    if person is not None:
        return Intent("person", query, person_id=person[0], person_name=person[1],
                      reason=f"{person[1]} is enrolled, so this is a face search",
                      reason_code="person_enrolled", reason_word=person[1])

    words = tokens_of(query)
    labels: list[str] = []
    unknown: list[str] = []
    descriptive: list[str] = []
    for word in words:
        if _lookup(word, {d: d for d in DESCRIPTIVE}):
            descriptive.append(word)
            continue
        label = _lookup(word, SYNONYMS)
        if label:
            if label not in labels:
                labels.append(label)
        else:
            unknown.append(word)

    if labels and not descriptive and not unknown:
        return Intent("objects", query, labels=labels,
                      reason=f"looking for {', '.join(labels)} - the detector "
                             "knows these directly",
                      reason_code="objects_known", reason_word=", ".join(labels))

    why = "describes something the local detectors cannot measure"
    code, word = "not_measurable", ""
    if descriptive:
        word = descriptive[0]
        code = "descriptive_word"
        why = f"'{word}' describes appearance or movement, not an object"
    elif unknown:
        word = unknown[0]
        code = "unknown_word"
        why = f"'{word}' is not something the local detectors know"

    fallback = None
    if labels:
        fallback = Intent("objects", query, labels=labels,
                          reason=f"every {', '.join(labels)} in the footage, "
                                 "without the rest of the description",
                          reason_code="objects_known",
                          reason_word=", ".join(labels))
    return Intent("ask", query, reason=why, reason_code=code, reason_word=word,
                  fallback=fallback)
