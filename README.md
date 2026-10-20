# BatchHunt

**An honest job-hunting agent for Claude.** Tell it who you are once. It finds jobs that match *your* rules, tailors your CV for each one, and applies, but only in batches you approve, and only with answers that are true.

```
profile → scan → filter → batch → you approve → tailored CV → apply → track → hand over what needs you
```

## Why it's different
- **You set the rules, it enforces them.** Salary floor, cities, remote scope you can legally work for, languages, role types to skip, companies to avoid. Every role is checked against them, and against the employer's own page, before you see it.
- **Batches, not blasts.** You get a table: company, role, pay, conditions, which CV variant, and what you're missing. Nothing is submitted until you say yes.
- **Honest by design.** Real titles, real numbers, real answers ("no iGaming experience; closest is regulated fintech"). It never invents stories, metrics or employers. If a form needs a personal story, it asks you.
- **Knows when to stop.** Captchas, logins, account creation, video interviews, "no AI" policies, relocation choices: these go to your `TODO.md` with a link and the exact action, never worked around.
- **Field-tested.** It comes with notes on which job boards actually work, plus form-filling techniques for Ashby, Greenhouse, Lever, Workable, Recruitee, Teamtailor and more.
- **No lock-in.** Your data stays in a local folder as plain Markdown/JSON. CVs render to ATS-readable PDFs with headless Chrome.

## Install

**Claude Code (plugin):**
```
/plugin marketplace add oleksislusarishere-glitch/batchhunt
/plugin install batchhunt@batchhunt
```

**Claude Code (manual):** copy `skills/batchhunt` to `~/.claude/skills/batchhunt`.

**Claude apps (claude.ai / desktop):** zip the `skills/batchhunt` folder and upload it under Settings → Capabilities → Skills.

Then say: **"Find me a job"** (or "найди мне работу"). The first run interviews you and asks for your CV.

### Requirements
- Python 3.10+ (`bash skills/batchhunt/scripts/setup.sh` creates a venv with `requests`, `python-jobspy`, `pandas`, `pypdf`)
- Google Chrome or Chromium (for PDFs; Playwright works as a fallback)
- To submit applications: [Claude in Chrome](https://claude.ai/chrome), because the agent needs a browser that can upload files

## What it asks you (once)
Target roles and seniority · roles to skip · city and country · remote/hybrid rules · where you can legally work · contractor/EoR · salary floor and how to state it · languages · start date · default portfolio · what not to claim. Full list: [`skills/batchhunt/references/onboarding.md`](skills/batchhunt/references/onboarding.md).

## Your data folder (`$BATCHHUNT_HOME`, default `~/batchhunt-data`)
| File | What |
|---|---|
| `profile.md` | facts, criteria, standard answers, honesty notes |
| `cv.json` | structured CV + variants (e.g. `brand`, `motion`, `lead`) |
| `search.json` | title keywords, locations, enabled sources |
| `tracker.md` | every application and decision |
| `apps/<company>/` | the tailored CV PDF for that job |
| `TODO.md` | what only you can do |

## Everyday use
- "Check for new jobs": rescans the enabled sources and proposes a batch.
- "Look at this: <url>": evaluates one posting, or learns a new job site.
- "Yes / yes except 2 / all": applies the batch.
- "What's waiting on me?": shows `TODO.md`.
- Optional: a daily scheduled scan that only *proposes*, never submits.

## Scripts
| Script | Purpose |
|---|---|
| `scripts/build_cv.py <slug> <variant> "Headline"` | tailored ATS-friendly PDF from `cv.json` |
| `scripts/scan.py` | scan sources from `search.json`, drop already-tracked companies |
| `scripts/jd_check.py <url>` | pull a posting from Ashby/Greenhouse/Lever and print the lines that decide eligibility |
| `scripts/setup.sh` | create the data folder and Python venv |

## Responsible use
BatchHunt applies on your behalf, under your name. Keep it honest and targeted: a few well-matched applications beat a hundred generic ones, and recruiters are people too. Respect each site's terms; it never bypasses captchas, logins or bot protection.

## License
MIT
