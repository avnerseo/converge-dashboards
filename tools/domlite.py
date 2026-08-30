"""Minimal HTML DOM for the Converge dashboards.

The dashboards are generated markup, not arbitrary web pages, so a small
tolerant parser is enough and keeps the toolchain dependency-free (matters for
CI, where `pip install` is a failure mode we do not want in the daily run).
"""

from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = parent

    # -- access -------------------------------------------------------
    def get(self, name, default=""):
        return self.attrs.get(name, default)

    @property
    def classes(self):
        return self.get("class", "").split()

    def matches(self, tag=None, cls=None, id=None, **attrs):
        if tag and self.tag != tag:
            return False
        if cls and cls not in self.classes:
            return False
        if id and self.get("id") != id:
            return False
        return all(self.get(k) == v for k, v in attrs.items())

    def find_all(self, tag=None, cls=None, id=None, **attrs):
        out = []
        for c in self.children:
            if isinstance(c, Node):
                if c.matches(tag, cls, id, **attrs):
                    out.append(c)
                out.extend(c.find_all(tag, cls, id, **attrs))
        return out

    def find(self, tag=None, cls=None, id=None, **attrs):
        found = self.find_all(tag, cls, id, **attrs)
        return found[0] if found else None

    def kids(self, tag=None, cls=None):
        """Direct children only."""
        return [c for c in self.children
                if isinstance(c, Node) and c.matches(tag, cls)]

    # -- text ---------------------------------------------------------
    @property
    def text(self):
        parts = []
        for c in self.children:
            parts.append(c if isinstance(c, str) else c.text)
        return "".join(parts)

    def clean_text(self):
        return " ".join(self.text.split())


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        if data.strip():
            self.cur.children.append(data)


def parse(html):
    b = _Builder()
    b.feed(html)
    b.close()
    return b.root
