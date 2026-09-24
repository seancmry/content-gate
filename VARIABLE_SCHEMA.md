# Variable schema

**System map:** `content/page.json` → Peec URL report or `fixtures/peec-urls.json` → compare on `url` → write `last_peec` → set `status`.

## Headline card

| Knob | Plain English |
| --- | --- |
| **`content_id`** | The page’s name inside this repo. |
| **`url`** | The public address Peec uses to point at the page. |
| **`locale`** | `de` or `en` of that same page. |
| **`PEEC_API_KEY`** | Peec password for `--live` only. |
| **gate** | The rule that blocks publish when they disagree. |

## Inputs

| Name | Type | Required | Job | If wrong or missing |
| --- | --- | --- | --- | --- |
| `--locale` | `de` \| `en` | no (default `de`) | Which language row to check | Unknown locale exits |
| `--live` | flag | no | Call Peec instead of the fixture | Without a key, the page is blocked and the error is stored |
| `PEEC_API_KEY` | string | live only | `X-API-Key` header | Live call does not run |
| `PEEC_PROJECT_ID` | string | company-scoped keys | Sent as `project_id` | Wrong project, or Peec rejects the call |
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

## Peec row we keep

`retrieval_count`, `citation_count`, `citation_rate`, `mentioned_brands`, plus our `checked_at`.
