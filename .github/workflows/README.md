# nanoSpec Competitor Tracker

Automatically checks 17 competitor websites every day and records any changes to
prices, products, or availability. Runs entirely on GitHub — no one's computer
needs to be on.

Two lists, one system:

- **competitor_list.csv** — SERS-substrate competitors (14 companies)
- **pfas_competitor_list.csv** — PFAS rapid-screening competitors (5 companies)

Nikalyte and Silmeco appear on both (substrate makers active in PFAS).

## Where to look

| You want to... | Open this |
|---|---|
| See what changed recently, in plain English | **CHANGELOG.md** — entries tagged [SERS] / [PFAS] |
| Current SERS competitor overview | **competitor_list.csv** (opens in Excel) |
| Current PFAS competitor overview | **pfas_competitor_list.csv** |
| Exactly what changed on a page, line by line | Commit history ("Commits" under the green Code button) |
| See/edit which pages are monitored | **tracked_pages.json** |
| Yesterday's saved copy of each page | **snapshots/** folder |

## CSV columns

**Auto-updated daily by the script:**

- *Prices Seen on Page* — every price the script finds on the tracked page
- *Stock Alerts* — flags like "sold out", "discontinued", "coming soon" seen on the page
- *Last Change Detected* — date the page last meaningfully changed
- *Last Checked* / *Page Status* — fetch result of the latest run

**Curated by hand** (edit with the pencil icon when research updates): pricing
model & MOQ, markets, distribution, funding, certifications, USP, notes.

## How it works

Every day at 06:00 UTC, GitHub Actions (`.github/workflows/daily-check.yml`)
runs `check_competitors.py`. The script opens each page in a headless Chrome
browser (JavaScript sites work), saves the visible text into `snapshots/`,
extracts prices and stock keywords, and commits the result. Meaningful changes
are summarized in `CHANGELOG.md`.

## Maintenance (rarely needed)

- **Add/remove a competitor:** edit `tracked_pages.json` (set `"lists"` to
  `["sers"]`, `["pfas"]`, or both) and add/remove the matching row (same
  Company name) in the corresponding CSV.
- **A page keeps failing:** the site probably moved. Update its URL in
  `tracked_pages.json`.
- **GitHub emails "scheduled workflow disabled":** Actions tab → Enable workflow.
- **Run a check right now:** Actions tab → "Daily competitor check" → Run workflow.

Created July 2026. Contact: Ethan Lin (ethanlin0623@gmail.com) during internship;
repository owner thereafter.
