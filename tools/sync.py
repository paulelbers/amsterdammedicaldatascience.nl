"""Copies the stylesheet and the hidden symbols of the front page into the
C4I page, so that both pages look the same.

It also builds the CV page again, which takes the same stylesheet.

Run it after changing the styles, the emblem or the three crosses in
index.html:  python3 tools/sync.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTS = [r"<style>.*?</style>", r'<svg width="0" height="0".*?</svg>']


def main() -> None:
    front = (ROOT / "index.html").read_text(encoding="utf-8")
    path = ROOT / "c4i" / "index.html"
    page = path.read_text(encoding="utf-8")
    for pattern in PARTS:
        source = re.search(pattern, front, re.S).group(0)
        page, n = re.subn(pattern, lambda _match: source, page, count=1, flags=re.S)
        assert n == 1, f"c4i/index.html has no part that matches {pattern}"
    path.write_text(page, encoding="utf-8")
    print("c4i/index.html now has the stylesheet and the symbols of index.html.")
    # The CV page takes the stylesheet when it is built.
    import cv
    (ROOT / "paulelbers" / "index.html").write_text(cv.build(), encoding="utf-8")
    print("paulelbers/index.html is built again with it.")


if __name__ == "__main__":
    main()
