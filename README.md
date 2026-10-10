# amsterdammedicaldatascience.nl

The website of Amsterdam Medical Data Science and
[AmsterdamUMCdb](https://github.com/AmsterdamUMC/AmsterdamUMCdb): what the
database holds, how to request access, the Data and Pizza meetups, and who is
behind it.

It is one page. There are no scripts, and nothing is loaded from another
site: no fonts, no trackers, no cookies.

## What is where

```
index.html        the whole page: text, styles and the opening drawing
404.html          shown for an address that does not exist
images/           logos and portraits
                  amds-emblem.png is the stethoscope cut out of the AMDS logo
                  (amdslogonew.png), without the white behind it; the full
                  logo is still the picture shown when the site is shared
press/            the press release of November 2019, in six languages
tools/skyline.py  draws the opening picture (see below)
tools/check.py    looks for missing files and broken links on the page
.nojekyll         tells GitHub to publish the files exactly as they are
```

## Changing the site

Edit `index.html` and propose the change as a pull request. Merging into
`main` publishes it; GitHub Pages takes about a minute.

To look at a change before proposing it, open `index.html` in a browser. The
images and PDFs load because their paths are relative.

Every proposal is checked by `tools/check.py`: a picture or PDF the page
refers to must be in the repository, and a link to a place on the page must
have that place. Run it yourself with `python3 tools/check.py`.

## Facts on the page, and where they come from

Check these when something changes, so the page does not go stale again.

| On the page | Source |
| --- | --- |
| Admissions, patients, years, observations, format, version | The README of [AmsterdamUMC/AmsterdamUMCdb](https://github.com/AmsterdamUMC/AmsterdamUMCdb) |
| How to cite | PubMed, [doi:10.1097/CCM.0000000000004916](https://doi.org/10.1097/CCM.0000000000004916) |
| What an applicant needs, and the steps | The access portal at `access.amsterdammedicaldatascience.nl`; the two must say the same |
| Number of meetup members | [Meetup.com](https://www.meetup.com/amsterdam-medical-data-science/), October 2026 |
| COVID-19 data warehouse figures | The previous version of this site; not re-checked |

## The opening picture

The line that starts as a heartbeat and becomes a row of canal houses is
drawn by `tools/skyline.py`. To change the houses, edit the list at the top
of that file, run

```
python3 tools/skyline.py
```

and paste what it prints over the `<svg>` inside `<div class="skyline">` in
`index.html`.

The three crosses are those of the flag of Amsterdam, side by side as on the
flag. They are not the logo of the municipality, which stacks them.

## How it is published

GitHub Pages serves the `main` branch of this repository. Its address is
`amsterdammedicaldatascience.nl` once the domain points to GitHub; until then
it is `paulelbers.github.io/amsterdammedicaldatascience.nl`.

Only the website lives here. Email for the domain and the access portal run
elsewhere and have their own DNS records.
