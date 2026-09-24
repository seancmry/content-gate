# What each input does

The check reads a page, finds that page’s address in a report, and marks the page as allowed to go live or held back.

## In one line

| Name | What you would call it |
| --- | --- |
| **Page name** | The short name of the article. |
| **Address** | The public link. This is how the page and the report are matched. |
| **Language** | German or English. |
| **Peec key** | The password for a live report. Only needed for a real call. Stays in `.env`. Peec is the system that knows whether an address was named. The page does not know that on its own. |
| **Database address** | Where the free Supabase project lives. |
| **Database password** | Lets a script write rows. Never put this in the repo or in chat. |
| **The check** | Holds the page back when the page and the report do not agree. |

## Knobs

| Name | Type | Required | What it does | If it is wrong or missing |
| --- | --- | --- | --- | --- |
| `--locale` | `de` or `en` | no (default German) | Which language to check | An unknown language stops the script |
| `--live` | on/off | no | Use a real Peec report instead of the saved sample | With no password, the page is held back and the error is saved |
| `PEEC_API_KEY` | text | only for a live call | Sent as the Peec password | The live call does not run |
| `PEEC_PROJECT_ID` | text | only for some keys | Which Peec project to ask | The wrong project, or Peec refuses the call |
| `SUPABASE_URL` | text | when using the database | Where the rows live | The script cannot reach the project |
| `SUPABASE_SECRET_KEY` | text | when using the database | Password for writing rows. Starts with `sb_secret_` | The public key is refused |
| `content/page.json` | file | yes | The page we check | There is nothing to check |
| `fixtures/peec-urls.json` | file | for the sample | The saved report | The sample check cannot run |

## Fields on a page

| Name | Type | Required | What it does | If it is wrong or missing |
| --- | --- | --- | --- | --- |
| `content_id` | text | yes | Same name for both languages of one article | A translation can look like a new page |
| `locales.<locale>.url` | text | yes | The address we match on | The report row cannot attach |
| `locales.<locale>.body` | text | yes | The words on the page | Held back: the page has no text |
| `locales.<locale>.json_ld.url` | text | yes | The hidden label. Must equal the address | Held back: the label does not match |
| `locales.<locale>.status` | draft, published, or blocked | yes | The decision | A failed check can look as if it went live |
| `last_peec.citation_rate` | number | from the report | How often the page was named, divided by how often it was found | A missing number holds the page back |
| `last_peec.checked_at` | time | written by the script | When we looked | Empty if the report had no row for this address |

## The demo script

`python experiments.py` checks a fixed set of pages against the saved report. It does not call Peec and does not change `content/page.json`.

| Name | Type | Required | What it does | If it is wrong or missing |
| --- | --- | --- | --- | --- |
| `PAGES` | list | yes | The pages, including the eight stored in the database | The list of pages gets shorter |
| `BROKEN` | list | yes | Empty text, a bad hidden label, a failed report, and a missing label. Not stored | Those held-back examples disappear |
| `fixtures/peec-urls.json` | file | yes | The saved report | Every address looks missing |

The pages go in. The saved report stands in for Peec. Each page comes out as “can go live” or “held back”, with a reason.

## The database function

`apply_check` is the same rule, stored next to the rows. It is not an Edge Function. It does not call Peec.

| Name | Type | Required | What it does | If it is wrong or missing |
| --- | --- | --- | --- | --- |
| `p_content_id` | text | yes | Which page | The function stops: no such page |
| `p_locale` | text | yes | Which language of that page | The function stops: no such page |
| `report_rows` | table | yes | The saved report, one row per address | Every address looks missing, so every page stays held |

## What we keep from a report row

How often the page was found, how often it was named, the rate of those two, which brands were mentioned, and the time we checked.
