#!/usr/bin/env python3
"""Daily competitor website checker for nanoSpec.

Fetches each page in tracked_pages.json with a headless browser (handles
JavaScript sites), saves the visible text to snapshots/, and when a snapshot
changed in a meaningful way (prices, stock, products) writes a plain-English
entry to CHANGELOG.md and refreshes competitor_list.csv.

Run by GitHub Actions (see .github/workflows/daily-check.yml).
"""
import csv, difflib, json, pathlib, re
from datetime import date, datetime, timezone

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
SNAP = ROOT / "snapshots"
SNAP.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Lines matching this are dropped before comparing (page noise).
NOISE = re.compile(
    r"cookie|consent|privacy|newsletter|©|all rights reserved|"
    r"skip to content|search for:|your cart|shopping cart", re.I)

# A changed line is "significant" if it looks price/stock/product related.
SIGNIFICANT = re.compile(
    r"€|\$|£|\bEUR\b|\bUSD\b|\bGBP\b|\d+[.,]\d{2}\b|"
    r"sold out|out of stock|in stock|back in stock|restock|discontinued|"
    r"price|launch|coming soon|no longer|pack of|per substrate", re.I)


def clean(text: str) -> str:
    lines, out = [], []
    for ln in text.splitlines():
        ln = re.sub(r"\s+", " ", ln).strip()
        if len(ln) >= 3 and not NOISE.search(ln):
            lines.append(ln)
    for ln in lines:                       # drop consecutive duplicates
        if not out or out[-1] != ln:
            out.append(ln)
    return "\n".join(out)


def fetch(page, url: str) -> str:
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(6000)            # give JavaScript time to render
    return page.inner_text("body")


def significant_diff(old: str, new: str) -> list[str]:
    sig = []
    for ln in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""):
        if ln[:1] in "+-" and not ln.startswith(("+++", "---")):
            if SIGNIFICANT.search(ln):
                sig.append(ln)
    return sig[:40]                        # cap very large diffs


def write_changelog(today: str, changes, failures) -> None:
    if not changes and not failures:
        return
    entry = [f"## {today}", ""]
    for name, url, sig in changes:
        entry.append(f"### {name} — page changed ({url})")
        entry.append("Lines starting with `-` were removed, `+` were added:")
        entry += [f"- `{ln}`" for ln in sig] or ["- (content changed; see commit diff for details)"]
        entry.append("")
    if failures:
        entry.append("### Fetch problems (page unreachable — possible outage, block, or site redesign)")
        entry += [f"- {f}" for f in failures]
        entry.append("")
    path = ROOT / "CHANGELOG.md"
    old = path.read_text(encoding="utf-8") if path.exists() else "# Competitor Change Log\n"
    head, _, rest = old.partition("\n")
    path.write_text(head + "\n\n" + "\n".join(entry) + rest, encoding="utf-8")


def update_csv(today: str, results: dict) -> None:
    path = ROOT / "competitor_list.csv"
    if not path.exists():
        return
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        res = results.get(r["Company"])
        if res:
            r["Last Checked"], r["Page Status"] = today, res
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    cfg = json.loads((ROOT / "tracked_pages.json").read_text(encoding="utf-8"))
    today = date.today().isoformat()
    changes, failures, results = [], [], {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=UA)
        for comp in cfg["companies"]:
            name, slug = comp["name"], comp["slug"]
            texts, ok = [], True
            for url in comp["urls"]:
                try:
                    texts.append(f"### {url}\n" + clean(fetch(page, url)))
                except Exception as e:
                    ok = False
                    failures.append(f"{name}: {url} ({type(e).__name__})")
            results[name] = "OK" if ok else "FETCH FAILED"
            if not texts:
                continue
            new = "\n\n".join(texts) + "\n"
            f = SNAP / f"{slug}.txt"
            if f.exists():
                old = f.read_text(encoding="utf-8")
                if old != new:
                    sig = significant_diff(old, new)
                    if sig:
                        changes.append((name, comp["urls"][0], sig))
                        results[name] += " — CHANGED"
                    else:
                        results[name] += " — minor edits"
            f.write_text(new, encoding="utf-8")
        browser.close()

    write_changelog(today, changes, failures)
    update_csv(today, results)
    (ROOT / "last_run.txt").write_text(
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") + "\n", encoding="utf-8")
    print(f"Checked {len(results)} companies: "
          f"{len(changes)} significant change(s), {len(failures)} fetch failure(s)")


if __name__ == "__main__":
    main()
