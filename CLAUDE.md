# Working on this site

The website of Amsterdam Medical Data Science, AmsterdamUMCdb, the Center for
Critical Care Computational Intelligence (C4I) and the CV of Paul Elbers,
published by GitHub Pages at https://amsterdammedicaldatascience.nl.
README.md explains what is where; read it first. This file holds the working
agreements on top of it.

## How changes are made

- Every change goes through a pull request. Paul Elbers merges; never push to
  `main`. Merging publishes the site within a minute or two.
- One topic per pull request, on a branch named `claude/<topic>`.
- Before adding to an open pull request, check that it has not been merged in
  the meantime. If it has, start a new branch from an up-to-date `main`.
- Before every commit: `python3 tools/check.py` (links, anchors, external
  links, shared stylesheet, CV page). It also runs on every pull request.
- After changing the styles, the emblem or the three crosses in `index.html`:
  `python3 tools/sync.py`. It copies them to the C4I page and rebuilds the CV
  page.
- Look at what you changed: a screenshot at 1280 px and at 390 px, and in dark
  mode when colours are involved. No page may scroll sideways at 320 px.
- The pull request says what changed and what Paul should check. Ask about
  anything you could not confirm instead of guessing.

## The pages

- Each page is one HTML file. No scripts, nothing loaded from other sites: no
  fonts, no trackers, no cookies. The CV page carries a block of structured
  data for search engines; that is data, nothing runs.
- Links to other sites open in a new tab: `target="_blank" rel="noopener"`.
  Links within the site do not.
- Images go in `images/`, as small as they can be while sharp: faces are
  square, about 200 px.
- `paulelbers/index.html` is built: never edit it. Change
  `paulelbers/profile.toml` (or `tools/cv.py`), then
  `python3 tools/cv.py build`. "The CV page of Paul Elbers" in README.md
  has the procedure and the rules for keeping it current.

## Writing

- English, plain and short. No marketing words, no exclamation marks.
- The center is the Center for Critical Care Computational Intelligence
  (C4I), never "Laboratory for".
- Paul writes in Dutch or English; answer him in the language of his message.

## People

- The faces on the front page are the current people of C4I. Someone who
  leaves moves to the alumni on the C4I page and off the front page.
- Alumni are former PhD candidates, postdocs and staff, in order of the year
  they left. A PhD graduate shows "PhD <year>" and a link to the thesis;
  others their role and years ("Postdoc, 2020–2021"). Without a photo, their
  initials.
- Paul Elbers and Patrick Thoral founded AmsterdamUMCdb; Laurens Biesheuvel
  created the Van Gogh version.
- About PhD candidates, publish only names, links Paul gave or that are
  public, completion and the year of the PhD.

## What does not go on the site

- The AmsterdamUMCdb governance document and the Van Gogh report.
- Grant applications that have not been awarded, and the content of the Vici
  application beyond the published editorial in Intensive Care Medicine
  (2026).
- "agendo", the name of the group in the Vici application.
- Pacmed as a partner.
- Anything private about Paul or others: date of birth, home address, family,
  health, phone numbers.

## AmsterdamUMCdb versions

- The original release is called Rembrandt (also known as v1.0.2). It is the
  only version at DANS for now: https://doi.org/10.17026/dans-22u-f8vd.
- Rembrandt OMOP (1.5) is, for now, available only to close collaborators.
- Van Gogh is the coming version.
- Access is requested through the portal, https://access.amsterdammedicaldatascience.nl
  (repository `paulelbers/amsterdamumcdb-access-portal`); only after approval
  there do people ask for the files at DANS.

## Commits and pull requests

End commit messages with the attribution lines the session gives, and pull
request descriptions with the generated-by line. The site check only runs
once a pull request exists, so open the pull request before waiting for it.
