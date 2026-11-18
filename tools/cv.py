"""The CV page of Paul Elbers, at /paulelbers/.

Two files feed the page:

  paulelbers/profile.toml       written by hand: bio, positions, roles,
                                education, grants, the h-index, the selected
                                papers, and works the sources below miss
  paulelbers/publications.json  collected by this script from PubMed and
                                arXiv; never edited by hand

    python3 tools/cv.py collect   asks PubMed and arXiv again, rewrites
                                  publications.json, and lists what changed.
                                  It also lists works that ORCID and OpenAlex
                                  know but the page does not, for a person to
                                  judge; it never adds those by itself.
    python3 tools/cv.py build     writes paulelbers/index.html from the two
                                  files and the stylesheet of the front page,
                                  and paulelbers/short.html, the short CV of
                                  two A4 pages
    python3 tools/cv.py pdf       prints short.html to
                                  paulelbers/paul-elbers-cv.pdf (needs
                                  Playwright with Chromium)

tools/check.py fails when index.html or short.html is not what "build" makes,
so the pages cannot be edited by hand and drift away from their sources. Run
"pdf" after every "build" that changed short.html.
"""
from __future__ import annotations

import datetime
import difflib
import html
import json
import pathlib
import re
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
FOLDER = ROOT / "paulelbers"
PROFILE = FOLDER / "profile.toml"
PUBLICATIONS = FOLDER / "publications.json"
PAGE = FOLDER / "index.html"
SHORT = FOLDER / "short.html"
PDF = FOLDER / "paul-elbers-cv.pdf"
SITE = "https://amsterdammedicaldatascience.nl/paulelbers/"

ORCID = "0000-0003-0447-6893"
# Every PubMed hit for "Elbers P" from 1994 on is his (he confirmed this);
# earlier ones are other people.
PUBMED_QUERY = "Elbers p AND 1994:3000[dp]"  # the same as the PubMed link on the page
ARXIV_QUERY = 'au:"Paul Elbers"'
MINE = re.compile(r"^Elbers P")
AGENT = "amsterdammedicaldatascience.nl CV page (info@amsterdammedicaldatascience.nl)"


# ---------------------------------------------------------------- collecting

def fetch(url: str, accept: str = "application/json", tries: int = 3):
    request = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": AGENT})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
            return json.loads(body) if "json" in accept else body
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(3 * (attempt + 1))


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def similar(a: str, b: str) -> bool:
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio() > 0.9


def full_range(pages: str) -> str:
    """1574-84 becomes 1574–1584; article numbers stay as they are."""
    match = re.fullmatch(r"([A-Za-z]*)(\d+)-([A-Za-z]*)(\d+)", pages)
    if not match:
        return pages
    pre, start, pre2, end = match.groups()
    if len(end) < len(start):
        end = start[: len(start) - len(end)] + end
    return f"{pre}{start}–{pre2 or pre}{end}"


def kind_of(types: list[str]) -> str | None:
    if "Published Erratum" in types or "Retraction of Publication" in types:
        return None
    if "Editorial" in types:
        return "Editorial"
    if "Letter" in types or ("Comment" in types and "Journal Article" not in types):
        return "Letter"
    if "Review" in types or "Systematic Review" in types:
        return "Review"
    if "Case Reports" in types:
        return "Case report"
    return "Article"


def pubmed() -> tuple[list[dict], int]:
    """The papers, and the number of PubMed records (corrections included)."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    term = urllib.parse.quote(PUBMED_QUERY)
    ids = fetch(f"{base}esearch.fcgi?db=pubmed&retmode=json&retmax=5000&term={term}")["esearchresult"]["idlist"]
    works = []
    for start in range(0, len(ids), 200):
        found = fetch(f"{base}esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids[start:start + 200])}")["result"]
        time.sleep(0.4)
        for uid in found["uids"]:
            record = found[uid]
            kind = kind_of(record.get("pubtype", []))
            if not kind:
                continue
            ids_ = {a["idtype"]: a["value"] for a in record.get("articleids", [])}
            doi = ids_.get("doi", "")
            pages = record.get("pages", "")
            if doi and len(pages) > 10 and doi.endswith(pages):
                pages = ""  # some journals give the end of the DOI as the page
            authors = [a["name"] for a in record.get("authors", []) if a.get("authtype") == "Author"]
            year = (record.get("pubdate") or record.get("epubdate") or record.get("sortpubdate", ""))[:4]
            works.append({
                "id": f"pmid:{uid}",
                "kind": kind,
                "year": int(year),
                "sort": record.get("sortpubdate", "")[:10].replace("/", "-"),
                "authors": authors,
                "consortium": not any(MINE.match(a) for a in authors),
                "title": record.get("title", "").strip(),
                "venue": record.get("source", ""),
                "volume": record.get("volume", ""),
                "issue": record.get("issue", ""),
                "pages": full_range(pages),
                "doi": doi,
                "pmid": uid,
            })
    return works, len(ids)


def initials(name: str) -> str:
    """'Paul W. G. Elbers' -> 'Elbers PWG', 'Harm-Jan de Grooth' -> 'de Grooth HJ'."""
    parts = name.replace(".", ". ").split()
    particles = {"van", "de", "der", "den", "ten", "ter", "von", "el", "le", "la", "da", "dos", "del"}
    cut = len(parts) - 1
    while cut > 0 and parts[cut - 1].lower() in particles:
        cut -= 1
    given, family = parts[:cut], " ".join(parts[cut:])
    letters = "".join(piece[0] for part in given for piece in part.split("-") if piece and piece[0].isalpha())
    return f"{family} {letters.upper()}".strip()


def arxiv() -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    query = urllib.parse.quote(ARXIV_QUERY)
    feed = ET.fromstring(fetch(f"https://export.arxiv.org/api/query?search_query={query}&max_results=200", accept="application/atom+xml"))
    works = []
    for entry in feed.findall("a:entry", ns):
        number = entry.find("a:id", ns).text.rsplit("/abs/", 1)[-1]
        number = re.sub(r"v\d+$", "", number)
        published = entry.find("a:published", ns).text[:10]
        authors = [initials(a.find("a:name", ns).text) for a in entry.findall("a:author", ns)]
        works.append({
            "id": f"arxiv:{number}",
            "kind": "Preprint",
            "year": int(published[:4]),
            "sort": published,
            "authors": authors,
            "consortium": False,
            "title": " ".join(entry.find("a:title", ns).text.split()),
            "venue": "arXiv",
            "volume": "", "issue": "", "pages": "",
            "doi": "",
            "arxiv": number,
        })
    return works


def candidates(known: list[dict], judged: list[str]) -> list[str]:
    """Works ORCID or OpenAlex list that are not on the page: for a person to judge.
    Titles in "judged" (profile.toml, not_listed) were judged before and stay quiet."""
    dois = {w["doi"].lower() for w in known if w.get("doi")}
    titles = [norm(w["title"]) for w in known] + [norm(t) for t in judged]
    lines = []

    def unseen(title: str, doi: str) -> bool:
        if doi and doi.lower() in dois:
            return False
        if norm(title).startswith("erratum"):
            return False
        mine = norm(title)
        # ORCID sometimes joins the English and Dutch titles of a paper
        return not any(similar(mine, t) or (len(t) > 25 and t in mine) for t in titles)

    try:
        groups = fetch(f"https://pub.orcid.org/v3.0/{ORCID}/works")["group"]
        for group in groups:
            work = group["work-summary"][0]
            title = work["title"]["title"]["value"]
            doi = next((e["external-id-value"] for e in group["external-ids"]["external-id"] if e["external-id-type"] == "doi"), "")
            if unseen(title, doi):
                year = ((work.get("publication-date") or {}).get("year") or {}).get("value", "")
                lines.append(f"ORCID     {year} {work['type']}: {title[:110]}")
    except Exception as error:  # a source being down must not stop the rest
        lines.append(f"ORCID could not be read ({error})")

    try:
        works, cursor = [], "*"
        while cursor:
            page = fetch(f"https://api.openalex.org/works?filter=author.orcid:{ORCID}&per-page=200&cursor={cursor}"
                         "&select=doi,title,publication_year,type")
            works += page["results"]
            cursor = page["meta"].get("next_cursor") if page["results"] else None
        for work in works:
            doi = (work.get("doi") or "").replace("https://doi.org/", "")
            if work.get("title") and (work.get("publication_year") or 0) >= 2006 and unseen(work["title"], doi):
                lines.append(f"OpenAlex  {work['publication_year']} {work['type']}: {work['title'][:110]}")
    except Exception as error:
        lines.append(f"OpenAlex could not be read ({error}); it allows a limited number of requests a day")
    return lines


def collect() -> None:
    before = json.loads(PUBLICATIONS.read_text(encoding="utf-8")) if PUBLICATIONS.exists() else {"works": []}
    from_pubmed, records = pubmed()
    from_arxiv = [w for w in arxiv() if not any(similar(w["title"], p["title"]) for p in from_pubmed)]
    works = sorted(from_pubmed + from_arxiv, key=lambda w: (w["year"], w["sort"], w["id"]), reverse=True)
    data = {
        "collected": datetime.date.today().isoformat(),
        "query": {"pubmed": PUBMED_QUERY, "arxiv": ARXIV_QUERY},
        "pubmed_records": records,  # what the PubMed link shows; corrections included
        "works": works,
    }
    PUBLICATIONS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    old = {w["id"]: w for w in before["works"]}
    new = {w["id"]: w for w in works}
    print(f"PubMed {len(from_pubmed)}, arXiv {len(from_arxiv)} not also in PubMed.")
    for key in new.keys() - old.keys():
        print(f"  new:     {new[key]['year']} {new[key]['title'][:100]}")
    for key in old.keys() - new.keys():
        print(f"  gone:    {old[key]['year']} {old[key]['title'][:100]}")
    profile = tomllib.loads(PROFILE.read_text(encoding="utf-8"))
    found = candidates(works + profile.get("extra", []), profile.get("not_listed", []))
    if found:
        print("\nKnown elsewhere but not on the page (add to [[extra]] in profile.toml only if it is his and worth listing):")
        print("\n".join(f"  {line}" for line in found))


# ------------------------------------------------------------------ building

def inline(text: str) -> str:
    """Escape text, then turn [words](address) into links. Links to other sites open in a new tab."""
    def link(match: re.Match) -> str:
        words, href = match.group(1), match.group(2)
        outside = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return f'<a href="{href}"{outside}>{words}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, html.escape(text, quote=False))


def outside(href: str, words: str) -> str:
    return f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{words}</a>'


def authors(names: list[str], consortium: bool) -> str:
    def show(name: str) -> str:
        return f"<b>{html.escape(name)}</b>" if MINE.match(name) else html.escape(name)
    if consortium:
        shown = ", ".join(show(n) for n in names[:3])
        return f"{shown}{', et al.' if len(names) > 3 else ''} Paul Elbers as a member of the study group."
    if len(names) <= 6:
        return ", ".join(show(n) for n in names) + "."
    me = next(i for i, n in enumerate(names) if MINE.match(n))
    if me < 3:
        return ", ".join(show(n) for n in names[:3]) + ", et al."
    if me == len(names) - 1:
        return ", ".join(show(n) for n in names[:3]) + ", … " + show(names[me]) + "."
    return ", ".join(show(n) for n in names[:3]) + ", … " + show(names[me]) + ", et al."


def citation(work: dict, label: bool = True) -> str:
    title = html.escape(work["title"].replace(" -- ", " – "))
    if title and title[-1] not in ".?!":
        title += "."
    kind = f'<span class="kind">{work["kind"]}</span> ' if label and work["kind"] != "Article" else ""
    if work["kind"] == "Preprint":
        where = f'<i>arXiv</i> {work["year"]}. {outside("https://arxiv.org/abs/" + work["arxiv"], "arXiv:" + work["arxiv"])}'
    elif work["kind"] in ("Book chapter", "Conference paper"):
        pages = f':{work["pages"]}' if work.get("pages") else ""
        where = f'In: <i>{html.escape(work["venue"])}</i>. {work["year"]}{pages}.'
    elif work["kind"] == "Book":
        where = f'{html.escape(work["venue"])}, {work["year"]}.'
        if work.get("isbn"):
            where += f' ISBN {html.escape(work["isbn"])}.'
    else:
        where = f'<i>{html.escape(work["venue"])}</i> {work["year"]}'
        if work.get("volume"):
            where += f';{html.escape(work["volume"])}'
            if work.get("issue"):
                where += f'({html.escape(work["issue"])})'
        if work.get("pages"):
            where += f':{html.escape(work["pages"])}'
        where += "."
    if work.get("doi"):
        where += " " + outside("https://doi.org/" + work["doi"], "doi:" + html.escape(work["doi"]))
    elif work.get("pmid"):
        where += " " + outside(f"https://pubmed.ncbi.nlm.nih.gov/{work['pmid']}/", "PubMed")
    elif work.get("arxiv") and work["kind"] != "Preprint":
        where += " " + outside("https://arxiv.org/abs/" + work["arxiv"], "arXiv:" + work["arxiv"])
    names = authors(work["authors"], work.get("consortium", False))
    if work.get("editors"):
        names = names.rstrip(".") + ", editors."
    return f"{kind}{names} {title} {where}"


def newest_first(item: dict) -> tuple:
    """Sort key, newest first. What is still going on ("2012–") comes first, by its
    first year; a period ("2025–2029") counts from its first year, a list of years
    ("2019, 2023") from its last. Rows without a year come last, in the order of
    profile.toml."""
    when = item.get("when", "").strip()
    years = [int(y) for y in re.findall(r"(?:19|20)\d\d", when)]
    if not years:
        return (2, 0)
    if "–" in when:
        return (0 if when.endswith("–") else 1, -years[0])
    return (1, -max(years))


def rows(items: list[dict]) -> str:
    out = []
    for item in sorted(items, key=newest_first):
        name = inline(item["title"])
        where = inline(item.get("where", ""))
        when = html.escape(item.get("when", ""))
        out.append(f'        <li><div><b>{name}</b>{f"<span>{where}</span>" if where else ""}</div>'
                   f'{f"<span class=\"when\">{when}</span>" if when else ""}</li>')
    return '      <ul class="rows">\n' + "\n".join(out) + "\n      </ul>"


def month(iso: str) -> str:
    return datetime.date.fromisoformat(iso + "-01" if len(iso) == 7 else iso).strftime("%B %Y")


def load() -> tuple[dict, dict, list[dict]]:
    """profile.toml, publications.json, and every work to show, newest first."""
    profile = tomllib.loads(PROFILE.read_text(encoding="utf-8"))
    collected = json.loads(PUBLICATIONS.read_text(encoding="utf-8"))
    hidden = set(profile.get("hide", []))
    extra = [dict(w, consortium=False) for w in profile.get("extra", [])]
    # A preprint that was published later is shown as published, with its arXiv link
    later = {p["id"]: p for p in profile.get("published", [])}
    works = [dict(w, **{k: v for k, v in later.get(w["id"], {}).items() if k != "id"})
             for w in collected["works"] + extra if w["id"] not in hidden]
    works.sort(key=lambda w: (w["year"], w.get("sort", "")), reverse=True)
    return profile, collected, works


def selected_works(profile: dict, works: list[dict]) -> list[dict]:
    by_doi = {w.get("doi", "").lower(): w for w in works if w.get("doi")}
    missing = [d for d in profile["selected"] if d.lower() not in by_doi]
    if missing:
        sys.exit(f"profile.toml selects papers that are not in the list: {', '.join(missing)}")
    return [by_doi[d.lower()] for d in profile["selected"]]


def build() -> str:
    profile, collected, works = load()

    front = (ROOT / "index.html").read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", front, re.S).group(0)
    icon = re.search(r'<link rel="icon"[^>]*>', front).group(0)

    in_pubmed = [w for w in works if w.get("pmid")]
    first_or_last = sum(1 for w in in_pubmed if not w["consortium"] and (MINE.match(w["authors"][0]) or MINE.match(w["authors"][-1])))
    corrections = collected.get("pubmed_records", len(in_pubmed)) - len(in_pubmed)
    h = profile["h_index"]

    selected = selected_works(profile, works)

    # Every paper, also those that name him as a member of a study group
    named = [w for w in works if w["kind"] not in ("Preprint", "Book chapter", "Book", "Conference paper")]
    years = sorted({w["year"] for w in named}, reverse=True)
    blocks = []
    for i, year in enumerate(years):
        these = [w for w in named if w["year"] == year]
        items = "\n".join(f"          <li>{citation(w)}</li>" for w in these)
        blocks.append(f'      <details{" open" if i == 0 else ""}>\n        <summary>{year} <span>{len(these)}</span></summary>\n'
                      f'        <ul class="pubs">\n{items}\n        </ul>\n      </details>')

    def group(title: str, these: list[dict], anchor: str) -> str:
        if not these:
            return ""
        items = "\n".join(f"          <li>{citation(w, label=False)}</li>" for w in these)
        return (f'      <details id="{anchor}">\n        <summary>{title} <span>{len(these)}</span></summary>\n'
                f'        <ul class="pubs">\n{items}\n        </ul>\n      </details>')

    others = "\n".join(filter(None, [
        group("Conference papers", [w for w in works if w["kind"] == "Conference paper"], "conferences"),
        group("Books", [w for w in works if w["kind"] == "Book"], "books"),
        group("Book chapters", [w for w in works if w["kind"] == "Book chapter"], "chapters"),
        group("Preprints", [w for w in works if w["kind"] == "Preprint"], "preprints"),
    ]))

    links = profile["links"]
    profiles = ", ".join(outside(l["url"], html.escape(l["name"])) for l in links)
    about = "\n".join(f"      <p>{inline(p)}</p>" for p in profile["about"])
    selected_items = "\n".join(f"        <li>{citation(w)}</li>" for w in selected)
    pubmed_link = "https://pubmed.ncbi.nlm.nih.gov/?term=Elbers+p&filter=years.1994-3000&sort=date"

    def part(key: str, heading: str = "") -> str:
        """Rows from profile.toml, under a heading when there is one; nothing when the list is empty."""
        if not profile.get(key):
            return ""
        return (f"      <h3>{heading}</h3>\n" if heading else "") + rows(profile[key])

    def joined(*parts: str) -> str:
        return "\n".join(p for p in parts if p)

    sections = [
        ("about", "About", about),
        ("positions", "Positions", joined(part("positions"), part("earlier", "Earlier positions"))),
        ("roles", "Roles", joined(part("roles"), part("former_roles", "Earlier roles"))),
        ("education", "Education", joined(part("education"), part("prizes", "Prizes"))),
        ("grants", "Grants", part("grants")),
        ("teaching", "Teaching", part("teaching")),
        ("lectures", "Lectures", part("lectures")),
    ]
    sections = [s for s in sections if s[2]]

    body = "\n\n".join(
        f'  <section id="{key}">\n    <h2>{title}</h2>\n    <div class="body">\n{content}\n    </div>\n  </section>'
        for key, title, content in sections)

    name, letters = profile["name"], profile["letters"]
    # For search engines: who this page is about, and the same person elsewhere.
    # Data only; nothing runs.
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "honorificSuffix": letters,
        "jobTitle": "Intensivist and associate professor of intensive care medicine",
        "worksFor": {"@type": "Organization", "name": "Amsterdam UMC", "url": "https://www.amsterdamumc.org/"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Amsterdam"},
        "url": "https://amsterdammedicaldatascience.nl/paulelbers/",
        "image": f"https://amsterdammedicaldatascience.nl/images/{profile['photo']}",
        "email": f"mailto:{profile['email']}",
        "knowsAbout": profile.get("keywords", []),
        "sameAs": [l["url"] for l in profile["links"] if l["name"] != "PubMed"],
    }
    structured = json.dumps(person, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}, {letters} | {html.escape(profile["short"])}</title>
<meta name="description" content="{html.escape(profile["description"])}">
<meta name="author" content="{name}">
<link rel="canonical" href="https://amsterdammedicaldatascience.nl/paulelbers/">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Amsterdam Medical Data Science">
<meta property="og:title" content="{name}, {letters}">
<meta property="og:description" content="{html.escape(profile["description"])}">
<meta property="og:url" content="https://amsterdammedicaldatascience.nl/paulelbers/">
<meta property="og:image" content="https://amsterdammedicaldatascience.nl/images/{profile["photo"]}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">
{structured}
</script>
{icon}
{style}
<style>
/* Only for this page. The stylesheet above is the one of the front page;
   tools/cv.py copies it in when it builds this page. */
.cv-top {{ display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 20px clamp(24px, 4vw, 48px); align-items: center; }}
.portrait {{ width: clamp(112px, 15vw, 176px); height: auto; aspect-ratio: 1; border-radius: 50%; object-fit: cover; background: var(--line); display: block; }}
.cv-top h1 {{ font-size: clamp(2.3rem, 5.6vw, 4rem); }}
.cv-top .letters {{ display: block; font-family: var(--body); font-size: 1rem; font-weight: 600; letter-spacing: .08em; color: var(--muted); margin-top: 10px; }}
.cv-top .lead {{ margin-top: 16px; }}
.profiles {{ margin-top: 18px; font-size: .97rem; color: var(--muted); }}
.experiment {{ margin-top: 12px; font-size: .9rem; color: var(--muted); max-width: 39rem; }}
.experiment .state {{ margin-right: 6px; font-size: .78rem; padding: 1px 8px; }}
.figures.three {{ grid-template-columns: repeat(3, minmax(min-content, 1fr)); margin-top: clamp(28px, 4vw, 44px); margin-bottom: 0; border-bottom: 0; }}
.rows {{ list-style: none; padding: 0; border-top: 1px solid var(--line-strong); }}
.rows li {{ display: grid; grid-template-columns: minmax(0, 1fr) max-content; gap: 2px 24px; align-items: baseline; padding-block: 12px; border-bottom: 1px solid var(--line); }}
.rows b {{ display: block; font-family: var(--display); font-size: 1.1rem; line-height: 1.3; }}
.rows span {{ display: block; font-size: .95rem; color: var(--muted); }}
.rows .when {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
.pubs {{ list-style: none; padding: 0; border-top: 1px solid var(--line-strong); }}
.pubs li {{ padding-block: 12px; border-bottom: 1px solid var(--line); font-size: .97rem; overflow-wrap: anywhere; }}
details .pubs {{ border-top: 0; }}
.kind {{ font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-right: 4px; }}
details {{ border-bottom: 1px solid var(--line-strong); }}
details:first-of-type {{ border-top: 1px solid var(--line-strong); }}
summary {{ cursor: pointer; padding-block: 12px; font-family: var(--display); font-weight: 600; font-size: 1.2rem; }}
summary span {{ font-family: var(--body); font-weight: 400; font-size: .9rem; color: var(--muted); margin-left: 6px; }}
summary:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 3px; border-radius: 3px; }}
@media (max-width: 760px) {{
  .cv-top {{ grid-template-columns: minmax(0, 1fr); }}
  .portrait {{ width: 112px; }}
  .rows li {{ grid-template-columns: minmax(0, 1fr); }}
}}
@media (max-width: 560px) {{
  .figures.three {{ grid-template-columns: minmax(0, 1fr); }}
  .figures.three div + div {{ border-left: 0; padding-left: 0; border-top: 1px solid var(--line); }}
}}
</style>
</head>
<body>
<a class="skip" href="#about">Skip to the text</a>

<header class="bar">
  <div class="page">
    <a class="wordmark" href="#top">{name}</a>
    <nav aria-label="On this page">
      <a href="#about">About</a>
      <a href="#positions">Positions</a>
      <a href="#roles">Roles</a>
      <a href="#education">Education</a>
      <a href="#grants">Grants</a>
      <a href="#publications">Publications</a>
      <a class="go" href="../c4i/">C4I</a>
    </nav>
  </div>
</header>

<main id="top">
<div class="page">

  <div class="opening">
    <div class="cv-top">
      <img class="portrait" src="../images/{profile["photo"]}" width="200" height="200" alt="Portrait of {name}">
      <div>
        <h1>{name}<span class="letters">{letters}</span></h1>
        <p class="lead">{inline(profile["lead"])}</p>
        <p class="profiles">Also on {profiles}. A short CV of two pages: <a href="paul-elbers-cv.pdf">PDF</a>.</p>
        <p class="experiment"><span class="state soon">Experiment</span> {inline(profile["experiment"])} <a href="#about-this-page">How it works</a></p>
      </div>
    </div>
    <dl class="figures three">
      <div><dt>papers in PubMed{f" ({len(in_pubmed) + corrections} records, {corrections} of them corrections)" if corrections else ""}</dt><dd>{len(in_pubmed)}</dd></div>
      <div><dt>of them as first or last author</dt><dd>{first_or_last}</dd></div>
      <div><dt>h-index, {html.escape(h["source"])}, {month(h["checked"])}</dt><dd>{h["value"]}</dd></div>
    </dl>
  </div>

{body}

  <section id="publications">
    <h2>Publications</h2>
    <div class="body">
      <h3>All papers, by year</h3>
      <p class="small">As listed in PubMed, including the papers that name him as a member of a study group, without corrections. The same list, always current, is on {outside(pubmed_link, "PubMed")}; citations are on {outside(next(l["url"] for l in links if l["name"] == "Google Scholar"), "Google Scholar")}.</p>
      <div>
{chr(10).join(blocks)}
      </div>
      <h3>Selected</h3>
      <ul class="pubs">
{selected_items}
      </ul>
      <h3>Other work</h3>
      <div>
{others}
      </div>
    </div>
  </section>

</div>
</main>

<footer id="contact">
  <div class="page">
    <h2>Contact</h2>
    <div class="body">
      <dl class="contact">
        <dt>Email</dt><dd><a href="mailto:{profile["email"]}">{profile["email"]}</a></dd>
        <dt>Address</dt><dd>{html.escape(profile["address"])}</dd>
      </dl>
      <p class="small" id="about-this-page">This page is a living CV and an experiment: it is kept up to date with the help of AI. The publications are collected from PubMed and arXiv, and other work and roles are looked up in public sources. Nothing changes here before Paul Elbers has checked it, but a machine can still miss something or get it slightly wrong. Corrections are welcome at <a href="mailto:{profile["email"]}">{profile["email"]}</a>. Publications last collected on {datetime.date.fromisoformat(collected["collected"]).strftime("%-d %B %Y")}.</p>
    </div>
  </div>
</footer>
</body>
</html>
"""


# ------------------------------------------------------------ the short CV

def plain(text: str) -> str:
    """Like inline(), for print: links become absolute and open nothing new."""
    def link(match: re.Match) -> str:
        return f'<a href="{urllib.parse.urljoin(SITE, match.group(2))}">{match.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, html.escape(text, quote=False))


def short_rows(items: list[dict]) -> str:
    out = []
    for item in sorted(items, key=newest_first):
        where = plain(item.get("short", item.get("where", "")))
        out.append(f'<li><span class="what"><b>{plain(item["title"])}</b>{f". {where}" if where else ""}</span>'
                   f'<span class="when">{html.escape(item.get("when", ""))}</span></li>')
    return '<ul class="rows">' + "".join(out) + "</ul>"


def short_citation(work: dict) -> str:
    names = work["authors"]
    me = next((i for i, n in enumerate(names) if MINE.match(n)), None)
    shown = [f"<b>{html.escape(n)}</b>" if MINE.match(n) else html.escape(n) for n in names]
    if len(names) <= 3:
        who = ", ".join(shown)
    elif me is not None and me >= 3:
        who = ", ".join(shown[:2]) + ", …, " + shown[me] + (", et al." if me < len(names) - 1 else "")
    else:
        who = ", ".join(shown[:3]) + ", et al."
    title = html.escape(work["title"].rstrip("."))
    stop = "" if title[-1:] in "?!" else "."
    if work.get("doi"):  # the title links to the paper; no room for the DOI itself
        title = f'<a href="https://doi.org/{html.escape(work["doi"])}">{title}</a>'
    where = f'<i>{html.escape(work["venue"])}</i> {work["year"]}'
    return f"{who.rstrip('.')}. {title}{stop} {where}."


def short() -> str:
    """The short CV: two A4 pages, printed to PDF by "pdf"."""
    profile, collected, works = load()
    cut = profile.get("print", {})
    h = profile["h_index"]
    in_pubmed = [w for w in works if w.get("pmid")]
    figures = [(str(len(in_pubmed)), "papers in PubMed"),
               (str(h["value"]), f'h-index, {h["source"]}, {month(h["checked"])}')]
    figures += [(f["value"], f["label"]) for f in cut.get("figures", [])]
    figure_html = "".join(f"<div><b>{html.escape(v)}</b><span>{html.escape(l)}</span></div>" for v, l in figures)
    papers = selected_works(profile, works)[: cut.get("publications", 10)]
    when = datetime.date.fromisoformat(collected["collected"]).strftime("%-d %B %Y")

    def section(title: str, body: str) -> str:
        return f'<section><h2>{title}</h2>{body}</section>' if body else ""

    def part(key: str, heading: str = "") -> str:
        if not profile.get(key):
            return ""
        return (f"<h3>{heading}</h3>" if heading else "") + short_rows(profile[key])

    body = "".join([
        section("Positions", part("positions") + part("earlier", "Earlier")),
        section("Education", part("education") + part("prizes", "Prizes")),
        section("Roles", part("roles") + part("former_roles", "Earlier")),
        section("Grants", part("grants")),
        section("Teaching", part("teaching")),
        section("Selected publications",
                "<ol class=\"pubs\">" + "".join(f"<li>{short_citation(w)}</li>" for w in papers) + "</ol>"),
    ])
    name, letters = profile["name"], profile["letters"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{name}, {letters}: curriculum vitae</title>
<meta name="robots" content="noindex">
<style>
@page {{ size: A4; margin: 15mm 17mm 16mm; }}
:root {{ --ink: #13232E; --muted: #566873; --line: #D5DEE3; --brand: #F57625;
  --display: "TeX Gyre Pagella", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
  --body: Inter, "Helvetica Neue", Arial, sans-serif; }}
* {{ box-sizing: border-box; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; color: var(--ink); background: #fff; font: 8.6pt/1.38 var(--body); }}
a {{ color: inherit; text-decoration: none; }}
header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 8mm;
  padding-bottom: 4mm; border-bottom: 1.4pt solid var(--brand); }}
h1 {{ font: 600 23pt/1.05 var(--display); margin: 0; letter-spacing: -.01em; }}
h1 span {{ font: 600 9pt var(--body); letter-spacing: .08em; color: var(--muted); margin-left: 3mm; }}
.title {{ margin: 2mm 0 0; font-size: 10pt; }}
.contact {{ text-align: right; color: var(--muted); font-size: 8.4pt; line-height: 1.55; white-space: nowrap; }}
.summary {{ margin: 3.5mm 0 0; font-size: 9.2pt; line-height: 1.45; }}
.figures {{ display: grid; grid-template-columns: repeat({len(figures)}, 1fr); margin: 4mm 0 1mm; border-top: .5pt solid var(--line); border-bottom: .5pt solid var(--line); }}
.figures div {{ padding: 2.2mm 3mm 2.2mm 0; }}
.figures div + div {{ padding-left: 3mm; border-left: .5pt solid var(--line); }}
.figures b {{ display: block; font: 600 15pt/1.1 var(--display); }}
.figures span {{ color: var(--muted); font-size: 7.6pt; }}
section {{ margin-top: 3.4mm; }}
h2 {{ font: 600 11.5pt var(--display); margin: 0 0 1.4mm; padding-bottom: 1mm; border-bottom: .5pt solid var(--line); break-after: avoid; }}
h3 {{ font: 600 7.6pt var(--body); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 2mm 0 .6mm; break-after: avoid; }}
.rows {{ list-style: none; margin: 0; padding: 0; }}
.rows li {{ display: grid; grid-template-columns: 1fr 19mm; gap: 3mm; padding: .35mm 0; break-inside: avoid; }}
.rows b {{ font-weight: 600; }}
.rows .when {{ text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }}
.pubs {{ margin: 0; padding-left: 5mm; }}
.pubs li {{ padding: .35mm 0; break-inside: avoid; }}
.pubs a {{ color: inherit; }}
.note {{ margin: 1.5mm 0 0; color: var(--muted); font-size: 8pt; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>{name}<span>{letters}</span></h1>
    <p class="title">{html.escape(cut.get("title", profile["short"]))}</p>
  </div>
  <div class="contact">
    <a href="mailto:{profile["email"]}">{profile["email"]}</a><br>
    <a href="{SITE}">{SITE.removeprefix("https://").rstrip("/")}</a><br>
    ORCID <a href="https://orcid.org/{ORCID}">{ORCID}</a>
  </div>
</header>
<p class="summary">{plain(cut.get("summary", profile["about"][0]))}</p>
<div class="figures">{figure_html}</div>
{body}
<p class="note">Short CV, {when}. The full CV, with all publications, books and chapters, is kept current at <a href="{SITE}">{SITE.removeprefix("https://")}</a></p>
</body>
</html>
"""


def pdf() -> None:
    from playwright.sync_api import sync_playwright  # only needed here
    with sync_playwright() as play:
        browser = play.chromium.launch()
        page = browser.new_page()
        page.goto(SHORT.resolve().as_uri())
        page.pdf(path=str(PDF), format="A4", prefer_css_page_size=True, print_background=True,
                 display_header_footer=True, header_template="<span></span>",
                 footer_template='<div style="width:100%;font:7pt Inter,Arial,sans-serif;color:#566873;'
                                 'padding:0 17mm;display:flex;justify-content:space-between">'
                                 '<span>Paul Elbers · curriculum vitae</span>'
                                 '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
        browser.close()
    print(f"{PDF.relative_to(ROOT)} is printed.")


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "collect":
        collect()
    elif command == "build":
        PAGE.write_text(build(), encoding="utf-8")
        SHORT.write_text(short(), encoding="utf-8")
        print("paulelbers/index.html and paulelbers/short.html are built.")
    elif command == "pdf":
        pdf()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
