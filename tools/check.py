"""Checks the site before a change is merged.

- every picture, PDF and page that index.html and 404.html refer to is in
  the repository;
- every link to a place on the page ("#access") has that place;
- the opening picture in index.html is what tools/skyline.py draws.

Run it from the top of the repository:  python3 tools/check.py
"""
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent


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


def problems_in(name: str) -> list[str]:
    page = Page()
    page.feed((ROOT / name).read_text(encoding="utf-8"))
    found = []
    for link in page.links:
        if link.startswith(("http://", "https://", "mailto:", "data:")) or link == "/":
            continue
        if link.startswith("#"):
            if link[1:] not in page.ids:
                found.append(f"{name}: links to {link}, but nothing on the page has that name")
        elif not (ROOT / link.split("#")[0].lstrip("/")).is_file():
            found.append(f"{name}: refers to {link}, which is not in the repository")
    return found


def main() -> int:
    found = problems_in("index.html") + problems_in("404.html")
    drawn = subprocess.run([sys.executable, str(ROOT / "tools" / "skyline.py")], capture_output=True, text=True, check=True).stdout
    squeeze = lambda text: re.sub(r"\s+", " ", text).strip()
    if squeeze(drawn) not in squeeze((ROOT / "index.html").read_text(encoding="utf-8")):
        found.append("index.html: the opening picture differs from what tools/skyline.py draws")
    for problem in found:
        print(problem)
    print("Nothing wrong found." if not found else f"{len(found)} problem(s).")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
