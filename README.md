# Content gate

This is a small check that decides whether a page is allowed to go live.

A page has an address. A report says which addresses were named by answer engines. The page goes live only when three things agree: the address, a hidden label on the page, and the report.

![A page goes live only when the address, the hidden label, and the report agree](docs/images/overview.png)

The page lives in a file for this demo. The report is a saved sample, so you do not need an account to try it. Supabase is the database that can store the pages.

## Why Peec is here

The page can tell you its address and its text. It cannot tell you whether an answer engine named that address. That fact belongs to Peec, which reports how often each address was found and how often it was named.

Peec is in this demo so the check has a second owner. The page does not grade itself. It goes live only when its address is in Peec’s report and the score is actually there. A saved sample stands in for a live Peec account, so the check can be read without a key.

## What the words mean

| Word in the files | What it means |
| --- | --- |
| **Page name** | The short name we use for one article. |
| **Address** | The public link. The page and the report are matched on this. |
| **Language** | German (`de`) or English (`en`) of that same article. |
| **How often named** | Of the times the page was found, how often it was actually named. A low number does not stop the page. A missing number does. |
| **Hidden label** | A small note on the page that must repeat the same address. |
| **Can go live** | The page and the report match. |
| **Held back** | Something does not match, so the page stays unpublished. |

The check reads the page, looks it up in the report, and writes the decision back onto the page.

The full field list is in `VARIABLE_SCHEMA.md`.

## Try the one-page check

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gate.py --locale de
python gate.py --locale en
```

German is in the sample report, so that page can go live. English is not in the report, so it is held back. Both decisions are written into `content/page.json`.

A live Peec report needs a key in `.env`. Copy `.env.example` to `.env` first.

```bash
python gate.py --locale de --live
```

Some keys also need a project id. A key that already belongs to one project does not. Docs: https://docs.peec.ai/api-reference/reports/get-urls-report

## Save the database address and password

After the Supabase project exists, from this folder:

```bash
npm run keys
```

It asks for the project address, then the secret password. The password is hidden as you type. Both are saved in `.env`, which is not uploaded to GitHub. Do not paste the password into chat.

## The demo

`python experiments.py` checks fourteen pages against the saved sample report. It does not call Peec, and it does not change `content/page.json`.

Six can go live. Eight are held back. A low “how often named” score still lets a page go live. A missing score, a missing address, empty text, a mismatched hidden label, or a failed report holds the page back.

![The pages we checked](docs/images/catalog.png)

![What the check decided](docs/images/results.png)

The same pictures, with a short note, are in [docs/content-gate-lab.pdf](docs/content-gate-lab.pdf).

## The database

Eight of the pages are stored in a `pages` table on a free Supabase project in Frankfurt. The database keeps the pages. It does not create the report. The numbers still come from the saved sample, or from a Peec key if one exists later.

The check has been written back onto those eight rows. Open the table and the page itself says what happened. `published` means it can go live. `blocked` means it stays held, and `block_reason` says why. `last_peec` holds how often the page was found and named. Five of the eight can go live. Three stay held.

The same rule also lives in the database as a function, `apply_check`. You give it a page name and a language. It looks that page up, finds the address in `report_rows` (the saved sample), and writes the decision back onto the page. The SQL is in `supabase/apply_check.sql`. In the dashboard it appears under **Database → Functions**.
