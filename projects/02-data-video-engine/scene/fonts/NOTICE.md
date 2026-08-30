# Heebo

Vendored from Google Fonts on 2026-08-30, weights 400 / 500 / 700 / 900.

- Source: https://fonts.google.com/specimen/Heebo
- License: SIL Open Font License 1.1 — https://openfontlicense.org/

Vendored rather than fetched at render time on purpose: a render must not touch
the network (see `../../notes/determinism.md`), and the host's own Hebrew fonts
vary by machine (see `../../notes/hebrew-rtl.md`).
