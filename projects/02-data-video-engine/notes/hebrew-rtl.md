# Hebrew in headless Chromium — what actually broke

The brief said to check this rather than assume it. Good call: one of the three
checks failed, and it failed silently in a way that changes what a number means.

Reproduce everything here with `python3 checks/bidi_check.py` and
`checks/hebrew-probe.html`.

## 1. Font embedding — fine, but do not rely on the host

The container ships DejaVu, FreeSans and Liberation, and all three cover Hebrew,
so Hebrew *renders* out of the box. That is a trap, not a result: which font wins
depends on the host's fontconfig, so the same HTML gives different line breaks
and different glyph widths on a different machine. A daily render that silently
reflows is not reproducible.

Fix: [Heebo](https://fonts.google.com/specimen/Heebo) (SIL OFL 1.1) is vendored
into `scene/fonts/` at four weights, ~44 KB each, and loaded from disk via
`@font-face`. The harness fails the run if Heebo is not in `document.fonts`
after load, so a missing font is a loud error rather than a quiet fallback.

## 2. Line breaking — fine

Hebrew wrapped correctly at a constrained width, broke on spaces, kept
Latin-script tokens (`Bigdata.com`, `BioCatch`) intact, and handled the Hebrew
punctuation the dashboard uses — geresh `׳`, gershayim `"` inside `ארה"ב`,
and the em dash. Nothing needed doing.

## 3. BiDi — this one was broken

`checks/bidi_check.py` renders a string inside a real RTL block and then reads
back the *visual* left-to-right order by measuring each glyph's bounding box.
Measured, because on a screenshot `−9.75%` and `9.75%−` look nearly the same
and mean different things.

| logical string | visual order, RTL block | |
|---|---|---|
| `−9.75%` (U+2212) | `9.75%−` | wrong |
| `-9.75%` (ASCII hyphen) | `9.75%-` | wrong |
| `המחיר: $89.66 −0.13%` | `0.13%− $89.66 :ריחמה` | wrong |
| `−9.75%` in `dir=ltr; unicode-bidi:isolate` | `−9.75%` | correct |

The cause: a leading minus has no preceding digit, so the BiDi algorithm treats
it as a neutral and resolves it to the paragraph direction — RTL — which parks
it on the far side of the number. Every daily loss in every card would have
shipped with its sign visually detached.

### The rule that fixes it

Every run of digits, currency, sign or Latin letters is its own LTR island:

```css
.ltr{direction:ltr;unicode-bidi:isolate;display:inline-block;
     font-variant-numeric:tabular-nums}
```

`scene.js` applies it in code, in `money()` / `pct()` / `ltr()`, so a customer's
feed cannot reintroduce the bug by putting a number in a Hebrew string. Layout
order comes from flexbox, never from letting BiDi reorder a mixed sentence.

`tabular-nums` is in the same rule for a different reason: proportional digits
change width as a counter animates, so a number would visibly jitter while
counting up.

### One gotcha this created

`.ltr` sets `display:inline-block`, which overrides `display:block` on any
element that also carries the class. The price and the change percentage were
both `<div>`s with `.ltr` and silently collapsed onto one line
(`$513.53+1.68%`). Fixed by making the wrapper a flex column — but worth
knowing before adding the next `.ltr` block element.
