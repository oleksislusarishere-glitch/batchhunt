# Onboarding interview

Goal: collect everything needed to search, filter and fill forms without asking again. Ask in **small groups** (3–5 questions per message), offer sensible defaults in brackets so terse answers work ("ok", "yes", "2"), and skip anything the CV already answers clearly. Use the AskUserQuestion tool for multiple-choice items when available.

## Step 1. CV
Ask the person to attach their CV (PDF/DOCX) or paste it, plus LinkedIn and portfolio links. Read it fully. Extract: name, contacts, location, every job (company, title, dates, location, what they did, numbers), education, skills, tools, languages, projects. Do not add anything that isn't there.

## Step 2. Questions (group them)

**Target**
1. Which roles? List 3–8 job titles they'd apply to (suggest titles that match their CV, e.g. "Brand Designer, Motion Designer, Art Director").
2. Seniority range (e.g. middle → director). For lead/director roles, what leadership have they really done (team size, years)?
3. Roles or fields to **skip** (e.g. UX/product, junior, sales, gambling).
4. Any companies they've already applied to or never want (do-not-apply list).

**Where**
5. Country and city of residence.
6. Work formats: fully remote? hybrid/on-site — in which cities only?
7. Remote scope they can legally work for: worldwide / EU / their country only / US? (Explain that many "remote" jobs are country-locked.)
8. Engagement types: full-time employee, contractor/B2B, freelance, part-time.

**Legal**
9. Work authorization: citizenship and residence/visa status; which countries they can work in without sponsorship; do they need sponsorship anywhere.
10. Can they invoice as a contractor (self-employed status) in their country? Open to Employer-of-Record?

**Money**
11. Salary floor and target, per market if different (e.g. "≥ €60k/yr foreign, ≥ €30k local"), currency, monthly or yearly, gross.
12. What to write when a form asks "expected salary": exact number or range? What to say for "current salary" if forced?

**Languages**
13. Languages and levels (CEFR, e.g. English C1). Which languages are they NOT able to work in?

**Standard answers**
14. Earliest start date / notice period.
15. Years of experience (as they want it stated).
16. Pronouns field: answer or "prefer not to say".
17. Portfolio link(s) to use by default; any per-company exceptions.
18. Phone, email to use on applications (the email replies will go to). Telegram/other handles if forms ask.
19. Anything sensitive to avoid claiming (tools, industries, team sizes they don't want overstated).

**Process**
20. Approve each batch before submitting? (Default yes; the skill always waits for approval.)
21. Daily automatic scan with a batch proposal? (Default: offer it.)
22. Job sites they already use or want checked first.

## Step 3. Write the files

1. `profile.md` from `templates/profile.template.md`: facts, criteria (as checkable rules), standard answers, honesty notes, do-not-apply list.
2. `cv.json` following `templates/cv.example.json`:
   - one entry per job with bullets that restate the CV (ids like `own`, `ds`, `ai`),
   - 2–4 **variants** matching their target role clusters (e.g. `brand`, `motion`, `lead`), each with a title, a 2–4 sentence summary and the bullet order per company,
   - only facts from the CV and the interview.
3. `search.json` from `templates/search.example.json`: title include/exclude regex built from target and skip roles; JobSpy terms and locations from their cities and remote scope; which optional sources to enable (Workable locations = their country + region; DOU only if they speak Ukrainian; Djinni/DOU only for Ukrainian-speaking market; crypto boards only if relevant).
4. `tracker.md` with the header row:
   `| # | Date | Company | Role (conditions) | Status | CV | Notes |`

## Step 4. Confirm
Show: target roles, criteria, salary, locations, languages, variants, and one sample CV (`build_cv.py sample <variant>`). Ask "all correct?" and fix before scanning.
