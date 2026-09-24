#!/usr/bin/env python3
"""Run the publish gate against a small catalog and write a lab page.

Peec’s report is the second source: it says which addresses were named. This script uses the saved sample. It does not call Peec and does not change content/page.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from gate import decide, fixture_rows, row_for, snapshot

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUT_JSON = DOCS / "experiment-results.json"
OUT_HTML = DOCS / "lab.html"

# Pages we store. The two broken cases below are copies used only in the lab.
PAGES = [
    {
        "content_id": "cnt_file_taxes_berlin",
        "locale": "de",
        "url": "https://example.com/de/steuern-berlin",
        "body": "So reichst du die Steuererklärung in Berlin ein.",
        "json_ld": {"@type": "Article", "headline": "Steuererklärung in Berlin", "url": "https://example.com/de/steuern-berlin"},
    },
    {
        "content_id": "cnt_file_taxes_berlin",
        "locale": "en",
        "url": "https://example.com/en/taxes-berlin",
        "body": "How to file a tax return in Berlin.",
        "json_ld": {"@type": "Article", "headline": "Filing taxes in Berlin", "url": "https://example.com/en/taxes-berlin"},
    },
    {
        "content_id": "cnt_elster_deadline",
        "locale": "de",
        "url": "https://example.com/de/elster-frist",
        "body": "Die Frist für die Steuererklärung endet am 31. Juli.",
        "json_ld": {"@type": "Article", "headline": "Frist für die Steuererklärung", "url": "https://example.com/de/elster-frist"},
    },
    {
        "content_id": "cnt_elster_deadline",
        "locale": "en",
        "url": "https://example.com/en/filing-deadline",
        "body": "The filing deadline is 31 July.",
        "json_ld": {"@type": "Article", "headline": "Tax filing deadline", "url": "https://example.com/en/filing-deadline"},
    },
    {
        "content_id": "cnt_home_office",
        "locale": "de",
        "url": "https://example.com/de/homeoffice",
        "body": "Das Homeoffice kann in der Steuererklärung angesetzt werden.",
        "json_ld": {"@type": "Article", "headline": "Homeoffice", "url": "https://example.com/de/homeoffice"},
    },
    {
        "content_id": "cnt_home_office",
        "locale": "en",
        "url": "https://example.com/en/home-office",
        "body": "A home office can be claimed on the tax return.",
        "json_ld": {"@type": "Article", "headline": "Home office deduction", "url": "https://example.com/en/home-office"},
    },
    {
        "content_id": "cnt_church_tax",
        "locale": "de",
        "url": "https://example.com/de/kirchensteuer",
        "body": "Die Kirchensteuer steht auf dem Steuerbescheid.",
        "json_ld": {"@type": "Article", "headline": "Kirchensteuer", "url": "https://example.com/de/kirchensteuer"},
    },
    {
        "content_id": "cnt_moving_costs",
        "locale": "en",
        "url": "https://example.com/en/moving-costs",
        "body": "Moving costs can be work-related expenses.",
        "json_ld": {"@type": "Article", "headline": "Moving costs", "url": "https://example.com/en/moving-costs"},
    },
    {
        "content_id": "cnt_commute",
        "locale": "de",
        "url": "https://example.com/de/pendlerpauschale",
        "body": "Die Pendlerpauschale gilt pro Entfernungskilometer.",
        "json_ld": {"@type": "Article", "headline": "Pendlerpauschale", "url": "https://example.com/de/pendlerpauschale"},
        "note": "synthetic",
    },
    {
        "content_id": "cnt_special_expenses",
        "locale": "en",
        "url": "https://example.com/en/special-expenses",
        "body": "Special expenses are listed on the return.",
        "json_ld": {"@type": "Article", "headline": "Special expenses", "url": "https://example.com/en/special-expenses"},
        "note": "synthetic",
    },
]

# Not stored. They show the two checks that happen before Peec is consulted.
BROKEN = [
    {
        "content_id": "cnt_werbungskosten",
        "locale": "de",
        "url": "https://example.com/de/werbungskosten",
        "body": "   ",
        "json_ld": {"@type": "Article", "headline": "Werbungskosten", "url": "https://example.com/de/werbungskosten"},
        "note": "synthetic",
    },
    {
        "content_id": "cnt_moving_costs",
        "locale": "de",
        "url": "https://example.com/de/umzugskosten",
        "body": "Umzugskosten können Werbungskosten sein.",
        "json_ld": {"@type": "Article", "headline": "Umzugskosten", "url": "https://example.com/de/wrong-url"},
        "note": "synthetic",
    },
    {
        "content_id": "cnt_file_taxes_berlin",
        "locale": "de",
        "url": "https://example.com/de/steuern-berlin",
        "body": "So reichst du die Steuererklärung in Berlin ein.",
        "json_ld": {"@type": "Article", "headline": "Steuererklärung in Berlin", "url": "https://example.com/de/steuern-berlin"},
        "note": "synthetic",
        "peec_error": "Peec 503: report unavailable",
    },
    {
        "content_id": "cnt_allowances",
        "locale": "en",
        "url": "https://example.com/en/allowances",
        "body": "Allowances are claimed on the return.",
        "json_ld": {},
        "note": "synthetic",
    },
]


def run_cases() -> list[dict]:
    rows = fixture_rows()
    results = []
    for page in PAGES + BROKEN:
        peec = row_for(page["url"], rows)
        status, reason = decide(page, peec, page.get("peec_error"))
        shot = snapshot(peec)
        results.append(
            {
                "content_id": page["content_id"],
                "locale": page["locale"],
                "url": page["url"],
                "stored": page.get("note") != "synthetic",
                "status": status,
                "reason": reason,
                "citation_rate": None if shot is None else shot["citation_rate"],
                "retrieval_count": None if shot is None else shot["retrieval_count"],
                "citation_count": None if shot is None else shot["citation_count"],
            }
        )
    return results


def plain_reason(reason: str) -> str:
    known = {
        "url, schema, and Peec agree": "The page and the report match, so it can go live.",
        "url is absent from the Peec report": "This address is not in the report, so it stays held.",
        "citation_rate is missing": "The report lists the page, but not how often it was named, so it stays held.",
        "body is empty": "The page has no text, so it stays held.",
        "json_ld.url does not match the page url": "The hidden label does not match the address, so it stays held.",
        "Peec 503: report unavailable": "The report failed to load, so it stays held.",
    }
    return known.get(reason, reason)


def write_html(results: list[dict]) -> None:
    def cell(value: object) -> str:
        text = "—" if value is None else str(value)
        return text.replace("&", "&amp;").replace("<", "&lt;")

    catalog_rows = []
    result_rows = []
    for item in results:
        badge = "published" if item["status"] == "published" else "blocked"
        decision = "Can go live" if item["status"] == "published" else "Held back"
        catalog_rows.append(
            "<tr>"
            f"<td>{cell(item['content_id'])}</td>"
            f"<td>{cell(item['locale'])}</td>"
            f"<td>{cell(item['url'])}</td>"
            f"<td>{cell('In the database' if item['stored'] else 'Demo only')}</td>"
            f"<td>{cell(item['citation_rate'])}</td>"
            "</tr>"
        )
        result_rows.append(
            "<tr>"
            f"<td>{cell(item['locale'])}</td>"
            f"<td>{cell(item['url'].removeprefix('https://example.com'))}</td>"
            f"<td class='{badge}'>{cell(decision)}</td>"
            f"<td>{cell(plain_reason(item['reason']))}</td>"
            "</tr>"
        )
    published = sum(1 for item in results if item["status"] == "published")
    blocked = len(results) - published
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Content gate lab</title>
  <style>
    @font-face {{ font-family: Geist; src: url("fonts/Geist-Regular.woff2") format("woff2"); font-weight: 400; }}
    @font-face {{ font-family: Geist; src: url("fonts/Geist-SemiBold.woff2") format("woff2"); font-weight: 600; }}
    body {{ font-family: Geist, sans-serif; margin: 28px auto; max-width: 980px; color: #111; background: #fff; }}
    h1 {{ font-weight: 600; font-size: 28px; margin-bottom: 4px; color: #111; }}
    h2 {{ font-weight: 600; font-size: 20px; margin-top: 28px; color: #0052ff; }}
    p {{ line-height: 1.45; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ text-align: left; padding: 7px 10px; border-bottom: 1px solid #e6e6e6; font-size: 14px; }}
    th {{ background: #0052ff; color: white; font-weight: 600; }}
    .published {{ color: #067a3a; font-weight: 600; }}
    .blocked {{ color: #d01212; font-weight: 600; }}
    .tiles {{ display: flex; gap: 16px; margin: 16px 0 8px; }}
    .tile {{ background: #f5f8ff; padding: 16px 20px; min-width: 140px; border-top: 4px solid #0052ff; }}
    .tile b {{ display: block; font-size: 28px; }}
  </style>
</head>
<body>
  <h1>Can this page go live?</h1>
  <p>We checked {len(results)} pages against a saved sample report. {sum(1 for item in results if item['stored'])} of them are stored in the database. The rest are examples we only use in this demo.</p>
  <div class="tiles">
    <div class="tile"><b>{published}</b>can go live</div>
    <div class="tile"><b>{blocked}</b>held back</div>
  </div>
  <h2 id="catalog">The pages</h2>
  <table>
    <thead><tr><th>Page</th><th>Language</th><th>Address</th><th>Saved where</th><th>How often named</th></tr></thead>
    <tbody>
      {''.join(catalog_rows)}
    </tbody>
  </table>
  <h2 id="results">What we decided</h2>
  <table>
    <thead><tr><th>Language</th><th>Page</th><th>Decision</th><th>Why</th></tr></thead>
    <tbody>
      {''.join(result_rows)}
    </tbody>
  </table>
</body>
</html>
"""
    OUT_HTML.write_text(html)
    head = html.split("<body>")[0] + "<body>\n"
    catalog_html = html.split("<h2 id=\"results\">")[0] + "</body></html>\n"
    results_html = head + "<h2 id=\"results\">" + html.split("<h2 id=\"results\">")[1]
    (DOCS / "catalog.html").write_text(catalog_html)
    (DOCS / "results.html").write_text(results_html)


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    results = run_cases()
    OUT_JSON.write_text(json.dumps(results, indent=2) + "\n")
    write_html(results)
    for item in results:
        print(f"{item['status']:9}  {item['locale']}  {item['url']}  — {item['reason']}")


if __name__ == "__main__":
    main()
