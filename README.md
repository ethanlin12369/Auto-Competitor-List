# nanoSpec Competitor Tracker

Automatically checks 17 competitor websites every day and records any changes to
prices, products, or availability. Runs entirely on GitHub — no one's computer
needs to be on.

## Where to look

| You want to... | Open this |
|---|---|
| See what changed recently, in plain English | **CHANGELOG.md** |
| See the current competitor overview | **competitor_list.csv** (opens in Excel) |
| See exactly what changed on a page, line by line | The commit history ("Commits" under the green Code button) — red lines were removed from the page, green lines were added |
| See/edit which pages are monitored | **tracked_pages.json** |
| Yesterday's saved copy of each page | **snapshots/** folder |

## How it works

Every day at 06:00 UTC, GitHub Actions (see `.github/workflows/daily-check.yml`)
runs `check_competitors.py`. The script opens each competitor page in a headless
Chrome browser (so JavaScript-built pages work too), saves the visible text into
`snapshots/`, and commits the result. When a change involves prices, stock, or
products, it also writes a summary into `CHANGELOG.md`.

## Maintenance (rarely needed)

- **Add/remove a competitor:** edit `tracked_pages.json` (pencil icon on GitHub).
- **A page keeps failing:** the site probably moved or redesigned. Find the new
  product page URL and update it in `tracked_pages.json`.
- **GitHub emails "scheduled workflow disabled":** GitHub pauses schedules in
  inactive repositories after ~60 days. Open the Actions tab and click
  "Enable workflow". (The daily commits normally prevent this.)
- **Run a check right now:** Actions tab → "Daily competitor check" → Run workflow.

Created July 2026. Contact: Ethan Lin (ethanlin0623@gmail.com) during internship;
repository owner thereafter.
