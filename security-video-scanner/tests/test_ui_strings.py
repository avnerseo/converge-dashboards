"""The Hebrew and English dictionaries must stay in step.

A string added to one and forgotten in the other shows up as an English
sentence in the middle of a Hebrew screen - which is exactly what a customer
notices first, and exactly what a passing test suite should not allow.
"""
from __future__ import annotations

import re
from pathlib import Path

APP_JS = Path(__file__).resolve().parent.parent / "vscan_server" / "static" / "app.js"


def _block(source: str, lang: str) -> str:
    start = source.index(f"  {lang}: {{")
    depth, i = 0, start
    while True:
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
        i += 1


# A key starts an entry: it follows the opening brace or a comma, never a
# space inside a sentence - Hebrew values happily contain colons of their own.
_KEY = re.compile(r"[{,]\s*(\w+):\s*'")


def _keys(source: str, lang: str) -> set[str]:
    return set(_KEY.findall(_block(source, lang)))


def test_every_string_exists_in_both_languages():
    source = APP_JS.read_text(encoding="utf-8")
    hebrew, english = _keys(source, "he"), _keys(source, "en")
    assert hebrew, "could not parse the Hebrew strings"
    assert not english - hebrew, f"missing from Hebrew: {sorted(english - hebrew)}"
    assert not hebrew - english, f"missing from English: {sorted(hebrew - english)}"


def test_every_used_string_is_defined():
    source = APP_JS.read_text(encoding="utf-8")
    defined = _keys(source, "en")
    used = set(re.findall(r"\bt\('(\w+)'\)", source))
    assert not used - defined, f"used but never defined: {sorted(used - defined)}"
