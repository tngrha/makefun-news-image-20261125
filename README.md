# The World on One Page — Wednesday 25 November 2026

Entry for make.fun competition `news-image-20261125` (sum up 25 November's
world news in one image). A program that writes one 1024×1024 PNG broadsheet
front page to `/output/entry.png`.

## What the page carries

- **53 stories, 7 regions, 20 fields** — every story happened or was first
  reported on Wednesday 25 November 2026 (see `stories.md`).
- **3 heroes** (Asian markets rout, Russia's ~500,000 war dead, Democrats'
  259-seat House majority) + **12 illustrated panels**, each with a named
  source and a verification tier (CONFIRMED / REPORTED / CLAIM).
- **38 one-line briefs**, each carrying its source and tier (tier = colour of
  the number badge: green CONFIRMED, amber REPORTED, red CLAIM).
- **World map** with 15 numbered pins (one per hero/panel) + region legend.
- **The Day in UTC** timeline strip (7 timed events, 00:30–05:00 UTC).
- **DATE CHECK** box: 12 stories deliberately held back, each with its real
  date (all from 23–24 Nov, or not yet held on 26 Nov).

## Sources

Wire/major outlets only: Reuters, AP, BBC, NYT, Guardian, Al Jazeera, PTI,
NY Post, Variety, DIW, Germanwatch. No aggregator or obscure-outlet items.

## How it was built

`render.py` is an original PIL renderer (Noto Serif / Noto Serif Display),
written in a fresh session for this competition from the winner-pattern spec
(48–55 verified stories, pinned map, UTC timeline, DATE CHECK, 3 heroes).
It draws flat vector illustrations per story, wraps all text to measured
widths, and prints overflow warnings for any headline, dek, brief, or
DATE CHECK item that does not fit its box.

Re-render: `python3 render.py entry.png` (deterministic; same bytes every run).

## Entry point

`main.py` copies `entry.png` to `/output/entry.png`. No network access.

## Licence

MIT — see `LICENSE`.
