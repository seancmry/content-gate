#!/usr/bin/env python3
"""Decide whether one page can go live.

The saved sample needs no password. A live run calls Peec's report of page addresses.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
PAGE_PATH = ROOT / "content" / "page.json"
FIXTURE_PATH = ROOT / "fixtures" / "peec-urls.json"
PEEC_URL = "https://api.peec.ai/customer/v1/reports/urls"


def load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_page() -> dict:
    return json.loads(PAGE_PATH.read_text())


def save_page(page: dict) -> None:
    PAGE_PATH.write_text(json.dumps(page, indent=2) + "\n")


def fixture_rows() -> list[dict]:
    payload = json.loads(FIXTURE_PATH.read_text())
    return list(payload.get("data") or [])


def live_rows(url: str) -> list[dict]:
    key = os.environ.get("PEEC_API_KEY", "").strip()
    if not key:
        raise SystemExit("Live mode needs PEEC_API_KEY in .env. Fixture mode does not.")
    project_id = os.environ.get("PEEC_PROJECT_ID", "").strip()
    end = date.today()
    start = end - timedelta(days=28)
    body: dict = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "limit": 100,
        "filters": [{"field": "url", "operator": "in", "values": [url]}],
    }
    if project_id:
        body["project_id"] = project_id
    response = httpx.post(
        PEEC_URL,
        headers={"X-API-Key": key},
        json=body,
        timeout=30,
    )
    if response.status_code >= 400:
        raise SystemExit(f"Peec {response.status_code}: {response.text[:400]}")
    return list(response.json().get("data") or [])


def row_for(url: str, rows: list[dict]) -> dict | None:
    for row in rows:
        if row.get("url") == url:
            return row
    return None


def decide(locale_row: dict, peec_row: dict | None, peec_error: str | None) -> tuple[str, str]:
    url = locale_row.get("url") or ""
    body = (locale_row.get("body") or "").strip()
    json_ld = locale_row.get("json_ld") or {}
    if not body:
        return "blocked", "body is empty"
    if json_ld.get("url") != url:
        return "blocked", "json_ld.url does not match the page url"
    if peec_error:
        return "blocked", peec_error
    if peec_row is None:
        return "blocked", "url is absent from the Peec report"
    if peec_row.get("citation_rate") is None:
        return "blocked", "citation_rate is missing"
    return "published", "url, schema, and Peec agree"


def snapshot(peec_row: dict | None) -> dict | None:
    if peec_row is None:
        return None
    return {
        "retrieval_count": peec_row.get("retrieval_count"),
        "citation_count": peec_row.get("citation_count"),
        "citation_rate": peec_row.get("citation_rate"),
        "mentioned_brands": peec_row.get("mentioned_brands") or [],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def run(locale: str, live: bool) -> int:
    page = load_page()
    locales = page.get("locales") or {}
    if locale not in locales:
        raise SystemExit(f"Unknown locale {locale!r}. Have: {', '.join(locales)}")
    row = locales[locale]
    peec_error = None
    try:
        rows = live_rows(row["url"]) if live else fixture_rows()
    except SystemExit as exc:
        peec_error = str(exc)
        rows = []
    peec_row = None if peec_error else row_for(row["url"], rows)
    status, reason = decide(row, peec_row, peec_error)
    row["status"] = status
    row["last_peec"] = snapshot(peec_row)
    row["block_reason"] = None if status == "published" else reason
    save_page(page)
    print(f"{page['content_id']} {locale} → {status}")
    print(reason)
    return 0 if status == "published" else 1


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Publish gate for one locale of the page.")
    parser.add_argument("--locale", default="de", choices=["de", "en"])
    parser.add_argument("--live", action="store_true", help="Call Peec. Default is the fixture.")
    args = parser.parse_args()
    raise SystemExit(run(args.locale, args.live))


if __name__ == "__main__":
    main()
