#!/usr/bin/env python3
"""
Reproduces the BiDi measurement behind the .ltr rule in scene.css.

Renders each string in a real RTL block and reads back the *visual* left-to-
right order of every glyph from its bounding box. Eyeballing a screenshot is
not enough: "−9.75%" and "9.75%−" look similar at a glance and mean different
things to a viewer.

    python3 checks/bidi_check.py
"""
import os
import sys

CHROME = os.environ.get(
    "CONVERGE_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
)

CASES = [
    ("naive, U+2212 minus",      "−9.75%",                       False),
    ("naive, ASCII hyphen",      "-9.75%",                            False),
    ("naive, price + change",    "המחיר: $89.66 −0.13%", False),
    ("isolated (.ltr)",          "−9.75%",                       True),
    ("isolated (.ltr)",          "$89.66 −0.13%",                True),
]

HTML = """<!doctype html><meta charset=utf-8>
<body style="font-family:sans-serif;font-size:40px"><div id=t></div><script>
window.build = (cases) => {
  const out = document.getElementById('t'); out.textContent='';
  for (const [name, txt, iso] of cases) {
    const d = document.createElement('div'); d.dir = 'rtl'; d.dataset.name = name;
    if (iso) { const s=document.createElement('span'); s.dir='ltr';
      s.style.unicodeBidi='isolate'; s.style.display='inline-block';
      s.textContent=txt; d.appendChild(s); }
    else d.textContent = txt;
    out.appendChild(d);
  }
};
window.probe = () => [...document.getElementById('t').children].map(d => {
  const w = document.createTreeWalker(d, NodeFilter.SHOW_TEXT);
  const nodes = []; let n; while (n = w.nextNode()) nodes.push(n);
  const glyphs = [];
  for (const node of nodes) for (let i = 0; i < node.data.length; i++) {
    const r = document.createRange(); r.setStart(node, i); r.setEnd(node, i + 1);
    const b = r.getBoundingClientRect();
    if (b.width || b.height) glyphs.push([b.left, node.data[i]]);
  }
  glyphs.sort((a, b) => a[0] - b[0]);
  return { name: d.dataset.name, logical: d.textContent,
           visual: glyphs.map(g => g[1]).join('') };
});
</script></body>"""


def main():
    from playwright.sync_api import sync_playwright
    bad = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.set_content(HTML)
        pg.evaluate("(c) => window.build(c)", CASES)
        for r in pg.evaluate("window.probe()"):
            ok = r["logical"] == r["visual"]
            bad += 0 if ok else 1
            print(f"{'ok  ' if ok else 'BAD '} {r['name']:26} "
                  f"logical={r['logical']!r}  visual={r['visual']!r}")
        b.close()
    print(f"\n{bad} of 5 cases render in the wrong visual order without .ltr isolation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
