# Job sources: what works

Field notes from real searches. Add to this file whenever you test a new source (what it's good for, how to query it, whether it's fresh). Enable or disable sources per person in `search.json`.

## Best: query the employer's ATS directly
Most verifiable source. Use these to confirm a role is open and to read the location/eligibility line.
- Ashby: `https://api.ashbyhq.com/posting-api/job-board/<board>?includeCompensation=true`
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true` (EU boards too)
- Lever: `https://api.lever.co/v0/postings/<co>?mode=json` or `https://api.eu.lever.co/...`
- Recruitee: `https://<co>.recruitee.com/api/offers/` (common in NL/EU; returns remote/hybrid flags)
- Workable account: `POST https://apply.workable.com/api/v3/accounts/<slug>/jobs` with body `{"query":""}`
- Personio: `https://<co>.jobs.personio.com/xml`
- Teamtailor: `https://<co>.teamtailor.com/jobs` (HTML)
Finding the board: try the company slug on each API; or grep their careers page for an ATS host.

## Automated in `scripts/scan.py`
| Source | How | Notes |
|---|---|---|
| Workable global search | `jobs.workable.com/api/v1/jobs?query=..&location=<Country>` | Best for country-tagged remote roles ("TELECOMMUTE; Portugal"). |
| Himalayas | `himalayas.app/jobs/api` | Remote; has location restrictions field. Pages block scraping, so find the ATS. |
| We Work Remotely | category RSS | Few creative roles; region field. Job pages 403 to scripts. |
| Jobicy | `jobicy.com/api/v2/remote-jobs` | tag/geo params ignored; filter by `jobGeo`. |
| Real Work From Anywhere | `realworkfromanywhere.com/rss.xml` | Only truly location-free roles. |
| Dribbble Jobs | `dribbble.com/jobs?location=Anywhere` (HTML) | Fresh, design-only. Applying needs a Dribbble account. |
| Getro boards | `https://<board>/jobs?q=<term>`, parse `__NEXT_DATA__` → `props.pageProps.initialState.jobs.found` | VC portfolio boards (Atomico, Accel, Insight, General Catalyst, Seedcamp, Point Nine, Creandum, Speedinvest, HV, Cherry, Antler, Earlybird) and crypto ecosystems (jobs.solana.com, Dragonfly, Electric, Polychain, Avalanche, Variant, Framework). Noisy: mostly onsite London/Berlin/US. |
| DOU.ua | `jobs.dou.ua/vacancies/feeds/?category=Design&remote` + search feeds | Ukrainian product companies; good for motion/AI creative; pay often lower; applying needs a DOU login. Enable only for Ukrainian speakers. |
| Remotive / Remote OK | APIs | Thin for design; off by default. |
| LinkedIn + Indeed | JobSpy | Indeed is strong for local roles in many countries. LinkedIn rate-limits (HTTP 429): sleep 4s+; its "remote" filter is unreliable. |

## Worth checking by hand (browser)
- **LinkedIn guest API** for full job text: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<id>`; search: `.../jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=..&location=..&f_WT=2`.
- **Remote Rocketship**, **EU Remote Jobs**: show external apply links; good for EU-eligible remote.
- **Djinni** (Ukrainian market, remote): applying works from the person's logged-in account; category pages work, free-text filter doesn't; fetch job pages by full slug URL.
- **Contra**: freelance marketplace; public pages `contra.com/opportunity/<id>`; applying needs an account.
- **Consider-powered VC boards** (a16z, Balderton, Notion Capital, Sequoia, Lightspeed): POST `/api-boards/search-jobs` with a csrf token and `jobFunctions:["Design"]`; US-heavy.
- **Malt** (EU freelance): profile-based; the person creates an account and clients reach out.

## Market notes
- Many "remote" roles are locked to one country (US-only, "remotely in Germany", UK-only). Read the location line, not the badge.
- Germany, Austria, Netherlands: creative roles are mostly onsite/hybrid or require the local language; remote-first companies elsewhere in Europe pay off more.
- Big tech brand/motion roles cluster in US/London/Berlin; regional hubs usually hire engineering.
- Remote-first scale-ups (AI, fintech, crypto) hiring via EoR or contractors across the EU are the richest vein for remote creatives.

## Weak or dead (as of late 2026)
Working Nomads (tiny), JustRemote, Arc.dev (dev only), Authentic Jobs (stale), Krop, Working Not Working, School of Motion jobs, Pangian, crypto.jobs, remote3, web3.career (stale), cryptojobslist (403). Behind Cloudflare (browser only): The Dots, Creativepool, Coroflot, Europe Remotely, hiring.cafe, startup.jobs.
