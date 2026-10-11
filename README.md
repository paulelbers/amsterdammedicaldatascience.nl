# amsterdammedicaldatascience.nl

The website of Amsterdam Medical Data Science and
[AmsterdamUMCdb](https://github.com/AmsterdamUMC/AmsterdamUMCdb): what the
database holds, how to request access, the Data and Pizza meetups, and who is
behind it. A second page is about the Center for Critical Care Computational
Intelligence (C4I), the research group behind the database.

Each page is one file. There are no scripts, and nothing is loaded from
another site: no fonts, no trackers, no cookies.

## What is where

```
index.html        the front page: text, styles, the emblem and the opening drawing
c4i/index.html    the page of the Center for Critical Care Computational
                  Intelligence, at /c4i/
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
tools/check.py    looks for missing files and broken links on the page, and
                  checks that the two drawings are what the scripts draw
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
| C4I: people | The director and the alumni named by Paul Elbers. Add current members when they agree to be listed |

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
