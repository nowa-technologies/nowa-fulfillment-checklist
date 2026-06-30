# AIKO Smart Toy — US Market Compliance Report

A single static page (`index.html`) listing all US-market compliance items for the
AIKO smart plush toy, for SBay & internal review.

- **Source of truth:** the consolidated Notion board
  *"[Resent to SBay] [All in one version] HQTS Compliance Report — AIKO — PML"*,
  which merges Tina's list and the HQTS compliance testing list.
- **Items:** 50 total — 38 committed (checked "to-do") · 12 HQTS-suggested.
  By type: 17 Mandatory · 13 Contingent · 17 Voluntary · 3 Confirming.

## Regenerate
The page is built from `data.json`:

```bash
python3 generate.py
```

Edit `data.json` (mirror of the Notion rows) and re-run to refresh `index.html`.

## Publish (GitHub Pages)
Served from the repo root, so the live URL is:
`https://nowa-technologies.github.io/nowa-fulfillment-checklist/`
