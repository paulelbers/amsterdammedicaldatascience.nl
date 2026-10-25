"""Checks the site before a change is merged.

- every picture, PDF and page that a page refers to is in the repository;
- every link to a place on a page ("#access", "../#access") has that place;
- every link to another website opens in a new tab;
- the drawings on the pages are what the scripts in tools/ draw;
- the C4I page has the same stylesheet and the same symbols as the front
  page, so the two cannot drift apart;
- the CV page is exactly what tools/cv.py builds from its two files.

Run it from the top of the repository:  python3 tools/check.py
"""
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "404.html", "c4i/index.html", "paulelbers/index.html"]
# script, page, what it draws
DRAWINGS = [
    ("skyline.py", "index.html", "opening picture"),
    ("emblem.py", "index.html", "emblem"),
    ("emblem.py", "c4i/index.html", "emblem"),
    ("pulse.py", "c4i/index.html", "opening picture"),
]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])


def read(name: str) -> Page:
    page = Page()
    page.feed((ROOT / name).read_text(encoding="utf-8"))
    return page


def problems_in(name: str) -> list[str]:
    page, found = read(name), []
    here = (ROOT / name).parent
    for link in page.links:
        if link.startswith(("http://", "https://", "mailto:", "data:")) or link == "/":
            continue
        path, _, place = link.partition("#")
        if not path:
            if place not in page.ids:
                found.append(f"{name}: links to {link}, but nothing on the page has that name")
            continue
        target = (ROOT / path.lstrip("/")) if path.startswith("/") else (here / path)
        target = target.resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file() or ROOT not in target.parents:
            found.append(f"{name}: refers to {link}, which is not in the repository")
        elif place and target.suffix == ".html" and place not in read(str(target.relative_to(ROOT))).ids:
            found.append(f"{name}: links to {link}, but nothing on that page has that name")
    return found


def same_tab(name: str) -> list[str]:
    """Links to other websites that would replace the page instead of opening a new tab."""
    text = (ROOT / name).read_text(encoding="utf-8")
    tags = re.findall(r'<a\b[^>]*\bhref="https?://[^"]*"[^>]*>', text)
    return [f"{name}: {re.search(r'href=\"([^\"]*)', tag).group(1)} should open in a new tab (target=\"_blank\" rel=\"noopener\")"
            for tag in tags if 'target="_blank"' not in tag or 'rel="noopener"' not in tag]


def squeeze(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def shared(name: str) -> tuple[str, str]:
    """The first stylesheet and the hidden block of symbols of a page."""
    text = (ROOT / name).read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", text, re.S)
    symbols = re.search(r'<svg width="0" height="0".*?</svg>', text, re.S)
    return (style.group(0) if style else "", symbols.group(0) if symbols else "")


def main() -> int:
    found = [problem for name in PAGES for problem in problems_in(name) + same_tab(name)]
    for script, name, what in DRAWINGS:
        drawn = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / script)], capture_output=True, text=True, check=True).stdout
        if squeeze(drawn) not in squeeze((ROOT / name).read_text(encoding="utf-8")):
            found.append(f"{name}: the {what} differs from what tools/{script} draws")
    front, center = shared("index.html"), shared("c4i/index.html")
    if not front[0] or front[0] != center[0]:
        found.append("c4i/index.html: its first stylesheet differs from the one in index.html; copy it over")
    if not front[1] or front[1] != center[1]:
        found.append("c4i/index.html: its hidden symbols differ from those in index.html; copy them over")
    sys.path.insert(0, str(ROOT / "tools"))
    import cv
    if cv.build() != (ROOT / "paulelbers" / "index.html").read_text(encoding="utf-8"):
        found.append("paulelbers/index.html: differs from what tools/cv.py builds; run python3 tools/cv.py build")
    for problem in found:
        print(problem)
    print("Nothing wrong found." if not found else f"{len(found)} problem(s).")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
