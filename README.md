# amsterdammedicaldatascience.nl

The website of Amsterdam Medical Data Science and
[AmsterdamUMCdb](https://github.com/AmsterdamUMC/AmsterdamUMCdb): what the
database holds, how to request access, the Data and Pizza meetups, and who is
behind it. A second page is about the Center for Critical Care Computational
Intelligence (C4I), the research group behind the database.

Each page is one file. There are no scripts, and nothing is loaded from
another site: no fonts, no trackers, no cookies. The CV page carries a block
of structured data for search engines (`application/ld+json`); it is data,
nothing runs.

## What is where

```
index.html        the front page: text, styles, the emblem and the opening drawing
c4i/index.html    the page of the Center for Critical Care Computational
                  Intelligence, at /c4i/
paulelbers/       the CV page of Paul Elbers, at /paulelbers/ (see below):
                  index.html is built from profile.toml and publications.json
404.html          shown for an address that does not exist
images/           logos and portraits
                  amdslogonew.png, the full AMDS logo, is the picture shown
                  when the site is shared
press/            the press release of November 2019, in six languages
tools/skyline.py  draws the opening picture (see below)
tools/emblem.py   draws the emblem (see below)
tools/pulse.py    draws the opening picture of the C4I page: ones and zeros
                  that become a heartbeat
tools/sync.py     copies the styles and symbols of the front page into the
                  C4I page
tools/cv.py       collects the publications for the CV page and builds it
tools/check.py    looks for missing files and broken links on the page, and
                  checks that the two drawings are what the scripts draw
sitemap.xml       the pages, for search engines; add a page here when it is new
robots.txt        tells search engines where the sitemap is
.nojekyll         tells GitHub to publish the files exactly as they are
```

## Changing the site

Edit `index.html` and propose the change as a pull request. Merging into
`main` publishes it; GitHub Pages takes about a minute.

To look at a change before proposing it, open `index.html` in a browser. The
images and PDFs load because their paths are relative.

The C4I page carries a copy of the stylesheet of the front page, followed by
a few rules of its own. After changing the styles in `index.html`, run
`python3 tools/sync.py` to copy them over; the check fails if you forget.

Every proposal is checked by `tools/check.py`: a picture or PDF the page
refers to must be in the repository, and a link to a place on the page must
have that place. Run it yourself with `python3 tools/check.py`.

## Facts on the page, and where they come from

Check these when something changes, so the page does not go stale again.

| On the page | Source |
| --- | --- |
| Van Gogh: locations, years, vocabularies, and the four rounded figures | The administrators. The figures are provisional: replace them with the final ones, and "In preparation" with "Available", on the day Van Gogh is released |
| Rembrandt: admissions, patients, years, medication records, and the release months of 1.0.2 and 1.5.0. Its number of observations is left out on purpose: Van Gogh is less granular, and the two totals would be compared | The README of [AmsterdamUMC/AmsterdamUMCdb](https://github.com/AmsterdamUMC/AmsterdamUMCdb) |
| The names Van Gogh and Rembrandt | The administrators. The earlier versions keep their numbers as "also known as" |
| One request covers every version | The administrators; the access portal must not say otherwise |
| Who reviewed privacy and ethics | The reviews of the Rembrandt versions; add those of Van Gogh at its release |
| How to cite | PubMed, [doi:10.1097/CCM.0000000000004916](https://doi.org/10.1097/CCM.0000000000004916) |
| What an applicant needs, and the steps | The access portal at `access.amsterdammedicaldatascience.nl`; the two must say the same |
| Number of meetup members | [Meetup.com](https://www.meetup.com/amsterdam-medical-data-science/), October 2026 |
| COVID-19 data warehouse figures | The previous version of this site; not re-checked |
| C4I: mission, how it works, who it brings together, collaborations, funders | The academic profile that Paul Elbers supplied, and the center's vacancy of May 2025 |
| C4I: what each study found | The abstracts on PubMed of the papers under "Selected publications" |
| C4I: twelve hospitals in ICUdata, seven hospitals using the discharge support | Supplied by Paul Elbers in 2026; these numbers grow, so check them once a year |
| C4I: people | Paul Elbers, October 2026: the PhD candidates he supervises (current and completing their PhD in one list), alumni, postdoc and colleague. First names as on their papers. LinkedIn addresses and institutional pages found by web search (only where they clearly matched); photos from Paul, October 2026 (cropped square, at most 400 × 400); the missing links to come from Paul |

## The CV page of Paul Elbers

`/paulelbers/` is a living CV. It is kept current by a person or by a
scheduled AI task, always through a pull request that Paul Elbers merges.

| File | What it holds | Who changes it |
| --- | --- | --- |
| `paulelbers/profile.toml` | bio, positions, boards and committees, education, grants, the h-index, the selected papers, works the sources miss | by hand |
| `paulelbers/publications.json` | every paper in PubMed and arXiv | `python3 tools/cv.py collect` only |
| `paulelbers/index.html` | the page | `python3 tools/cv.py build` only |

To bring the page up to date:

1. `python3 tools/cv.py collect`. It asks PubMed (the query `Elbers p` from
   1994 on: every hit is his) and arXiv, rewrites `publications.json`, and
   says what is new or gone. It also lists works that ORCID and OpenAlex know
   but the page does not. It never adds those itself.
2. Judge that list. A real work of his that is worth listing goes into
   `[[extra]]` in `profile.toml`; anything else into `not_listed`, so it is
   not mentioned again. When in doubt, leave it out and ask in the pull request.
3. Look for changes in his roles: new positions, committees, grants or
   prizes, in public sources such as society and Amsterdam UMC pages and
   news. Propose them in `profile.toml`, each with the address where it was
   found, in the pull request.
4. `python3 tools/cv.py build`, then `python3 tools/check.py`.
5. Propose it as one pull request that lists every change and its source.
   When nothing changed, propose nothing.

Rules for whoever does this, a person or an AI:

- Nothing goes live without Paul Elbers merging it.
- Only what a public source says, or what he said himself. No guesses, no
  inflated titles, no other person's work.
- Nothing private: no date of birth, home address, family or health.
- The h-index comes from Google Scholar, which a program cannot read. Ask
  him for the current figure every three months, in the pull request; never
  replace it with another source's figure.
- Pending grant applications are not listed until they are awarded.

## The opening picture

The line that starts as a heartbeat and becomes a row of canal houses is
drawn by `tools/skyline.py`. To change the houses, edit the list at the top
of that file, run

```
python3 tools/skyline.py
```

and paste what it prints over the `<svg>` inside `<div class="skyline">` in
`index.html`.

The windows on the upper floors are ones and zeros. Read from left to right,
floor by floor and house by house, they spell "AmsterdamUMCdb" in eight-bit
ASCII. The text is `MESSAGE` at the top of the script.

## The emblem

The stethoscope around a figure of ones and zeros is the emblem of the AMDS
logo, redrawn by `tools/emblem.py` so that its two parts can have their own
colour: the stethoscope in the orange of the logo, the same as the heartbeat,
and the figure in the colour of the text, like the houses. On a dark screen
the figure turns light with the text.

The script prints two symbols, the figure and the stethoscope. They stand in
the hidden `<svg>` at the top of `<body>`, after the three crosses. The bar at
the top of the page shows the stethoscope alone; the opening shows both.

The three crosses are those of the flag of Amsterdam, side by side as on the
flag. They are not the logo of the municipality, which stacks them.

## How it is published

GitHub Pages serves the `main` branch of this repository. Its address is
`amsterdammedicaldatascience.nl` once the domain points to GitHub; until then
it is `paulelbers.github.io/amsterdammedicaldatascience.nl`.

Only the website lives here. Email for the domain and the access portal run
elsewhere and have their own DNS records.
