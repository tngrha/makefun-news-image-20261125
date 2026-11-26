# The World on One Page — Wednesday 25 November 2026 (full-day edition)

Entry for the make.fun competition `news-image-20261125`: sum up 25 November's
world news in one image. $100 pot, 50 paid places. Account @tngrha.

## The image

`entry.png` (1024x1024, under 1 MiB) is a serif broadsheet of the FULL 25
November 2026 UTC day (00:00-24:00 UTC), built after the day ended from
verified wire/major reporting:

- **53 stories** = 3 heroes + 12 picture panels + 38 briefs
- **7 regions** (N. America, S. America, Europe, Africa, Middle East, Asia,
  Oceania) and **20 fields**
- **15-pin schematic world map** (legend sums to 15), **UTC timeline**
  (9 events, 00:30-23:30), **DATE CHECK** (12 exclusions with real dates)
- Tier (CONFIRMED / REPORTED) + named source on every item

Heroes: two oil tankers hit by naval mines in the Strait of Hormuz; Wall
Street's Thanksgiving-eve whipsaw (Nasdaq -4.6% intraday, Dow closing +164 at
50,183); the FCC clearing SpaceX to fly 1 million satellites.

## Files

- `main.py` — entry program: copies `entry.png` to `/output/entry.png`
  (deterministic, offline).
- `render.py` — the original PIL renderer that drew `entry.png` from the
  story list (run it to regenerate the image).
- `stories.md` — all 53 stories with sources, tiers, counts and the date
  check.
- `entry.png` — the rendered broadsheet.
- `LICENSE` — MIT. `.makefun/owner.json` — payout wallet.

## Run

```sh
python3 main.py            # writes out/entry.png
MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

## Verification

Every story happened, or was first reported, on 25 November 2026
(sources: Reuters, AP, BBC, NYT, The Atlantic, Politico, Axios, UEFA, PTI,
Dow Jones, Covers, Sportradar, EuroLeague, eOption, WSJ). Items from other
dates (e.g. the Huawei verdict, Real Madrid 5-1 PSV, both 24 Nov) are
excluded to the DATE CHECK box only.
