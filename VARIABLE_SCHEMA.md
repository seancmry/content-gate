# Variable schema

**System map:** `content/page.json` → Peec URL report or `fixtures/peec-urls.json` → compare on `url` → write `last_peec` → set `status`.

## Headline card

| Knob | Plain English |
| --- | --- |
| **`content_id`** | The page’s name inside this repo. |
| **`url`** | The public address Peec uses to point at the page. |
| **`locale`** | `de` or `en` of that same page. |
| **`PEEC_API_KEY`** | Peec password for `--live` only. |
| **`SUPABASE_URL`** | Address of the free Supabase project. |
| **`SUPABASE_SECRET_KEY`** | Password for that project. Server-side only. |
| **gate** | The rule that blocks publish when they disagree. |

## Inputs

| Name | Type | Required | Job | If wrong or missing |
| --- | --- | --- | --- | --- |
| `--locale` | `de` \| `en` | no (default `de`) | Which language row to check | Unknown locale exits |
| `--live` | flag | no | Call Peec instead of the fixture | Without a key, the page is blocked and the error is stored |
| `PEEC_API_KEY` | string | live only | `X-API-Key` header | Live call does not run |
| `PEEC_PROJECT_ID` | string | company-scoped keys | Sent as `project_id` | Wrong project, or Peec rejects the call |
| `SUPABASE_URL` | string | when using Supabase | Where the page rows live | Script cannot reach the project |
| `SUPABASE_SECRET_KEY` | string | when using Supabase | Lets the script write rows. `sb_secret_…` | A publishable key is rejected |
| `content/page.json` | file | yes | The page. System of record | Nothing to check |
| `fixtures/peec-urls.json` | file | fixture mode | Saved URL report | Fixture mode cannot run |

## Page fields

| Name | Type | Required | Job | If wrong or missing |
| --- | --- | --- | --- | --- |
| `content_id` | string | yes | Stable id across locales | A translation can be mistaken for a new page |
| `locales.<locale>.url` | string | yes | Join key | Peec row cannot attach |
| `locales.<locale>.body` | string | yes | Article text | Blocked: body is empty |
| `locales.<locale>.json_ld.url` | string | yes | Must equal `url` | Blocked: schema does not match |
| `locales.<locale>.status` | `draft` \| `published` \| `blocked` | yes | Gate result | A failed check can look live |
| `last_peec.citation_rate` | number | from Peec | Cited ÷ retrieved | Missing rate blocks |
| `last_peec.checked_at` | timestamp | written by the script | When the snapshot was taken | Empty if Peec had no row |

## Experiments

`python experiments.py` checks a fixed catalog against the fixture. It does not call Peec and does not change `content/page.json`.

| Name | Type | Required | Job | If wrong or missing |
| --- | --- | --- | --- | --- |
| `PAGES` | list | yes | The eight stored rows | The lab catalog shrinks |
| `BROKEN` | list | yes | Empty body, schema mismatch, a Peec error, and a missing schema. Not stored | Those blocks disappear |
| `fixtures/peec-urls.json` | file | yes | The saved URL report | Every URL looks absent |

**Headline card:** the catalog is the pages. The fixture is the Peec stand-in. The outcome is `published` or `blocked` plus the reason.

## Peec row we keep

`retrieval_count`, `citation_count`, `citation_rate`, `mentioned_brands`, plus our `checked_at`.
