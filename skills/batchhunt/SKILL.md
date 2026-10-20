---
name: batchhunt
description: Personal job-search agent for anyone. On first use it interviews the person (target roles, seniority, salary floor, locations and remote rules, languages, work authorization, honesty rules) and reads their CV, then finds matching jobs, filters them by those criteria, builds a tailored CV per job, and fills and submits applications after the person approves each batch. Use this whenever the user wants to find a job, shares a job link or job site, says "find me jobs", "check new vacancies", "apply", "batch", "найди работу", "проверь вакансии", "подавай", asks about their applications, tracker or CVs, or wants to set up their job-search profile, even if they don't name the skill.
---

# BatchHunt

A repeatable loop: **profile → scan → filter → batch for approval → tailored CV → apply → track → hand over what needs the human.**

Talk to the user in their language. Write applications in English unless the form or posting is in a language the user speaks and prefers.

## Working folder

`BATCHHUNT_HOME` (default `~/batchhunt-data`). It holds the person's data, never the skill folder:

```
profile.md      facts, criteria, standard answers, honesty rules (from onboarding)
cv.json         structured CV + CV variants (source of truth for every CV)
search.json     title keywords and locations the scanner uses
tracker.md      every application and decision
apps/<slug>/    tailored CV (PDF) and any drafted email per job
scans/          scan outputs
TODO.md         what the human must do (logins, captchas, personal answers)
```

If `profile.md` does not exist, run **Onboarding** first. Every other step reads `profile.md`.

## 0. Onboarding (first run, or "update my profile")

Read `references/onboarding.md` and follow it: ask the questions in small groups (not one giant form), read the attached CV, then create `profile.md` (from `templates/profile.template.md`), `cv.json` (schema in `templates/cv.example.json`), `search.json` (from `templates/search.example.json`) and an empty `tracker.md`. Show the person a short summary of their profile and 2–3 CV variants, build one sample PDF with `scripts/build_cv.py sample <variant>`, and ask them to confirm before any search.

Run `scripts/setup.sh` once per machine (Python venv for the scanner).

## Two entry points

**A. The user gives a URL or a site name**
1. Single posting: `$BATCHHUNT_HOME/.venv/bin/python -I scripts/jd_check.py <url>` (public ATS) or read the page, and judge fit against `profile.md`.
2. A job board or site: work out how it lists jobs (public API, JSON/RSS feed, ATS, or page text in the browser). Pull matching roles, verify each promising one on the real posting, and add what you learned about the source to `references/sources.md`.
3. Continue at **Filter and batch**.

**B. "Check for new jobs" (rescan known sources)**
1. `$BATCHHUNT_HOME/.venv/bin/python -I scripts/scan.py` (reads `search.json`, drops anything already in `tracker.md`).
2. For deeper sweeps, spawn parallel research subagents with a candidate summary built from `profile.md`, the criteria, the list of sources already used, and the exclusion list from `tracker.md`. Ask them for a verified table: apply URL (company ATS), quoted location/eligibility line, salary, language, GO/MAYBE/NO with a reason. Don't re-check sources the user said to skip.
3. Continue at **Filter and batch**.

## Filter and batch

Keep a role only if it passes the person's criteria in `profile.md`:
- location/remote rule (remote eligibility for their country of residence, or hybrid/on-site only in the cities they accept);
- no required language they don't speak;
- no work authorization they lack (e.g. US-only, "remote within Germany only");
- salary not clearly below their floor (unknown is fine, flag it);
- role type and seniority in their target list, not in their skip list;
- company not already in `tracker.md` (and not on their do-not-apply list).

Always verify on the company's own page or ATS before proposing; aggregator listings go stale.

Present one table per batch: company, role, salary, conditions, CV variant, caveats (anything they lack, honestly). Add a short "skipped and why" list. **Wait for an explicit yes** ("yes", "yes except 3", "all") before submitting anything. Approval covers only that batch.

## Apply

For each approved role:
1. Build the CV: `python3 scripts/build_cv.py <slug> <variant> "<headline matching the job title>"`. The headline may mirror the posting's wording but must not inflate the person's real level or titles.
2. Open the form in the browser that can upload files (Claude in Chrome), upload the PDF, fill fields using `references/forms.md` and the standard answers in `profile.md`, write short specific answers grounded only in facts from `profile.md` and `cv.json`, and submit.
3. Confirm success from the page (`Success`, `Thank you`, `?success`, `/thanks`, `applied=ok`), then append a row to `tracker.md`.
4. Hand over instead of submitting when: the form needs an account, login, captcha or email verification; the company bans AI-written answers or wants a video; a question needs a personal fact or story not in the profile; or a choice is really the person's (relocation, office city, salary below floor). Add each to `TODO.md` with the link, what's prefilled and the exact action needed.

At the end report: submitted (with confirmation), waiting on the user (exact action), skipped (reason), new sources added.

## Honesty rules (always)

Read `references/honesty.md`. In short: never invent employers, titles, dates, metrics, tools, industries or stories; reframe and emphasise, don't fabricate; answer "do you have X experience" truthfully and say what's adjacent; leave demographic questions blank or "prefer not to say"; never use someone else's account; never send email from an account that isn't the person's application address.

## Daily automation (optional)

If the person wants it, create a scheduled task that runs entry point B every morning and posts a batch for approval. It must never submit on its own.
