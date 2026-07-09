# nanoSpec Competitor Tracker

Automatically checks competitor websites every day and records any changes to
prices, products, or availability. Runs entirely on GitHub — no one's computer
needs to be on.

Three lists + per-competitor profiles, all from one daily run:

- **competitor_list.csv** — SERS-substrate competitors (business view; includes a
  nanoSpec reference row so we see our own live site alongside rivals)
- **pfas_competitor_list.csv** — PFAS rapid-screening competitors
- **technical_comparison.csv** — technical / science view (nanoparticles,
  platform, enhancement factor, patents)
- **profiles/** — one Markdown file per competitor, regenerated every run,
  showing everything the lists hold for that company in one place

## Where to look

| You want to... | Open this |
|---|---|
| What changed recently, in plain English | **CHANGELOG.md** (entries tagged [SERS]/[PFAS]/[TECH]) |
| Business overview of SERS competitors | **competitor_list.csv** |
| PFAS competitors | **pfas_competitor_list.csv** |
| Technical/science comparison | **technical_comparison.csv** |
| A single competitor, everything in one page | **profiles/<name>.md** |
| Exactly what changed on a page, line by line | Commit history (green Code button → Commits) |
| Which pages are monitored | **tracked_pages.json** |

## CSV columns

**Auto-updated daily** in every CSV: *Prices Seen on Page*, *Stock Alerts*
(sold out / discontinued / coming soon), *Last Change Detected*, *Last Checked*,
*Page Status*.

**Curated by hand** (edit with the pencil icon): all the business/technical
columns — pricing model, markets, distribution, funding, nanoparticles,
enhancement factor, patents, notes, etc.

## How it works

Every day at 06:00 UTC, GitHub Actions (`.github/workflows/daily-check.yml`)
runs `check_competitors.py`. For each competitor it opens the tracked page(s) in
a headless Chrome browser (JavaScript sites work), saves the visible text to
`snapshots/`, extracts prices and stock keywords, updates the three CSVs,
regenerates the `profiles/` files, and commits everything. Meaningful changes
are summarized in `CHANGELOG.md`.

## Maintenance (rarely needed)

- **Add/remove a competitor:** edit `tracked_pages.json` (set `"lists"` to any of
  `sers`, `pfas`, `tech`) and add/remove a matching row (same Company name) in
  each CSV it belongs to. Its profile file is created/removed automatically.
- **A page keeps failing:** the site moved — update its URL in `tracked_pages.json`.
- **"Scheduled workflow disabled" email:** Actions tab → Enable workflow.
- **Run a check now:** Actions tab → "Daily competitor check" → Run workflow.

Created July 2026. Contact: Ethan Lin (ethanlin0623@gmail.com) during internship;
repository owner thereafter.
