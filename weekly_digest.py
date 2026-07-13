#!/usr/bin/env python3
"""Build the weekly competitor digest email (HTML) for nanoSpec.

Reads the three CSVs and CHANGELOG.md, then writes digest.html with:
  Part 1 — Currently Tracking: every list and every competitor, in tables.
  Part 2 — Updates This Week: changes the tracker detected in the last 7 days.

Run weekly by GitHub Actions (see .github/workflows/weekly-email.yml), which
then emails digest.html.
"""
import csv, html, pathlib, re
from datetime import date, datetime, timedelta

ROOT = pathlib.Path(__file__).parent
LISTS = [
    ("Business — SERS substrates", "competitor_list.csv"),
    ("PFAS rapid screening", "pfas_competitor_list.csv"),
    ("Technical / science comparison", "technical_comparison.csv"),
]
# Columns shown in the summary tables (kept short for email readability).
SUMMARY_COLS = {
    "competitor_list.csv": ["Company", "Product / Brand", "Pricing (baseline Jul 2026)",
                             "Prices Seen on Page", "Stock Alerts", "Last Change Detected"],
    "pfas_competitor_list.csv": ["Company", "Product / Method", "Stage",
                                  "Prices Seen on Page", "Stock Alerts", "Last Change Detected"],
    "technical_comparison.csv": ["Company", "Platform Type", "Enhancement Factor (EF)",
                                 "Price per Substrate (EUR)", "Last Change Detected"],
}
DAYS = 7


def esc(s: str) -> str:
    return html.escape(s or "")


def read_csv(fname):
    p = ROOT / fname
    return list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []


def table_html(fname) -> tuple[str, int]:
    rows = read_csv(fname)
    cols = [c for c in SUMMARY_COLS[fname] if rows and c in rows[0]]
    th = "".join(f"<th style='padding:6px 10px;border:1px solid #ccc;background:#1F4E79;"
                 f"color:#fff;text-align:left;font-size:13px'>{esc(c)}</th>" for c in cols)
    trs = []
    for r in rows:
        tds = "".join(f"<td style='padding:6px 10px;border:1px solid #ccc;font-size:13px'>"
                      f"{esc(r.get(c,''))}</td>" for c in cols)
        trs.append(f"<tr>{tds}</tr>")
    tbl = (f"<table style='border-collapse:collapse;width:100%;margin:8px 0 20px'>"
           f"<tr>{th}</tr>{''.join(trs)}</table>")
    return tbl, len(rows)


def parse_changelog(days=DAYS):
    """Return list of (date_str, block_text) for entries within the window."""
    p = ROOT / "CHANGELOG.md"
    if not p.exists():
        return []
    cutoff = date.today() - timedelta(days=days)
    out = []
    for block in re.split(r"\n(?=## )", p.read_text(encoding="utf-8")):
        m = re.match(r"## (\d{4}-\d{2}-\d{2})", block.strip())
        if not m:
            continue
        try:
            d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= cutoff:
            out.append((m.group(1), block.strip()))
    return out


def changelog_html(entries) -> str:
    if not entries:
        return ("<p style='font-size:14px;color:#333'>No competitor changes were "
                "detected in the past week. All tracked pages were checked and are "
                "unchanged.</p>")
    parts = []
    for dstr, block in entries:
        body = block.split("\n", 1)[1] if "\n" in block else ""
        # Convert the simple markdown to light HTML.
        h = []
        for ln in body.splitlines():
            ln = ln.rstrip()
            if ln.startswith("### "):
                h.append(f"<p style='margin:12px 0 2px;font-weight:bold;font-size:14px'>"
                         f"{esc(ln[4:])}</p>")
            elif ln.startswith("- "):
                txt = esc(ln[2:].strip("`"))
                colr = "#0a7d00" if ln.lstrip("- ").startswith("`+") else \
                       "#c0392b" if ln.lstrip("- ").startswith("`-") else "#333"
                h.append(f"<div style='font-size:13px;color:{colr};margin-left:14px'>{txt}</div>")
            elif ln.strip():
                h.append(f"<div style='font-size:13px;color:#555'>{esc(ln)}</div>")
        parts.append(f"<h3 style='color:#1F4E79;font-size:15px;margin:18px 0 4px'>"
                     f"{esc(dstr)}</h3>{''.join(h)}")
    return "".join(parts)


def main() -> None:
    today = date.today().isoformat()
    entries = parse_changelog()

    tables = ""
    total = 0
    for title, fname in LISTS:
        tbl, n = table_html(fname)
        total += n
        tables += (f"<h3 style='color:#1F4E79;font-size:16px;margin:22px 0 4px'>"
                   f"{esc(title)} &mdash; {n} companies</h3>{tbl}")

    changed_flag = ("<span style='color:#c0392b;font-weight:bold'>"
                    f"{len(entries)} day(s) with changes</span>") if entries else \
                   "<span style='color:#0a7d00;font-weight:bold'>no changes</span>"

    doc = f"""<!DOCTYPE html><html><body style="font-family:Arial,Helvetica,sans-serif;
color:#222;max-width:820px;margin:0 auto;padding:16px">
<h1 style="color:#1F4E79;font-size:22px;margin-bottom:2px">nanoSpec Competitor Tracker — Weekly Digest</h1>
<p style="color:#666;font-size:13px;margin-top:0">Week of {today} &nbsp;·&nbsp; {total} company-entries across 3 lists &nbsp;·&nbsp; {changed_flag}</p>
<hr style="border:none;border-top:2px solid #1F4E79">

<h2 style="color:#222;font-size:18px">Part 1 — Currently tracking</h2>
<p style="font-size:13px;color:#555">Every list and every competitor being monitored. Prices and stock alerts are read automatically from each site; the other columns are curated.</p>
{tables}

<hr style="border:none;border-top:2px solid #1F4E79">
<h2 style="color:#222;font-size:18px">Part 2 — Updates this week</h2>
<p style="font-size:13px;color:#555">Changes detected on competitor pages in the last {DAYS} days — new or removed products, price changes, stock/availability changes, discontinuations. Red = removed from the page, green = added.</p>
{changelog_html(entries)}

<hr style="border:none;border-top:1px solid #ccc;margin-top:24px">
<p style="font-size:12px;color:#999">Automated by the nanoSpec Competitor Tracker on GitHub. Full detail and history: open the repository. To change who receives this email, edit the RECIPIENTS secret in the repository settings.</p>
</body></html>"""

    (ROOT / "digest.html").write_text(doc, encoding="utf-8")
    print(f"digest.html written: {total} entries, {len(entries)} change-day(s) in last {DAYS} days")


if __name__ == "__main__":
    main()
