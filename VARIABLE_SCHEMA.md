# Inputs

`gate.py` reads one page, finds that page's address in a naming report, and writes **can go live** or **held back**.

Peec is the live report. The page cannot know whether it was named. The saved sample needs no key.

## Knobs

| Name | Required | What it does |
| --- | --- | --- |
| `--locale` | no, default `de` | `de` or `en`. An unknown language stops the script. |
| `--live` | no | Use a real Peec report instead of `fixtures/peec-urls.json`. |
| `PEEC_API_KEY` | only for `--live` | Sent to Peec. Stays in `.env`. |
| `PEEC_PROJECT_ID` | only for some keys | Which Peec project to ask. |
| `SUPABASE_URL` | when using the database | Where the rows live. |
| `SUPABASE_SECRET_KEY` | when using the database | Writes rows. The public key is refused. |
| `content/page.json` | yes | The page `gate.py` checks. |
| `fixtures/peec-urls.json` | for the sample | The saved report. |

## Fields on a page

| Name | What it does |
| --- | --- |
| `content_id` | Same name for both languages of one article. |
| `locales.<locale>.url` | The address the report is matched on. |
| `locales.<locale>.body` | The words on the page. Empty text holds the page. |
| `locales.<locale>.json_ld.url` | Hidden label. Must equal the address. |
| `locales.<locale>.status` | `draft`, `published`, or `blocked`. |
| `last_peec.citation_rate` | Named divided by found. A missing number holds the page. |
| `last_peec.checked_at` | When the report row was read. Empty if the report had no row for this address. |

A report row also keeps how often the page was found, how often it was named, which brands were mentioned, and the time of the check.

## The fourteen-page run

`python experiments.py` checks a fixed set against the saved report. It does not call Peec and does not change `content/page.json`.

`PAGES` is that set, including the eight stored in the database. `BROKEN` is the held examples: empty text, a bad hidden label, a failed report, and a missing label. Those are not stored.

## Database function

`apply_check` is the same rule, stored next to the rows. It is not an Edge Function. It does not call Peec.

| Argument | What it does |
| --- | --- |
| `p_content_id` | Which page. Missing page: the function stops. |
| `p_locale` | Which language of that page. |
| `report_rows` | The saved report, one row per address. An empty report holds every page. |
