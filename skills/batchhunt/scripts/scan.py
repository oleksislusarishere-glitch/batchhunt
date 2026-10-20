#!/usr/bin/env python3
"""Scan job sources for NEW roles matching search.json, minus anything in tracker.md.

Usage: scan.py [--days 14] [--no-jobspy]
Reads $BATCHHUNT_HOME/search.json (default ~/batchhunt-data). Needs `requests`;
LinkedIn/Indeed need `python-jobspy` (run scripts/setup.sh). Writes
$BATCHHUNT_HOME/scans/<date>-candidates.json and prints a compact table.

Every source is public and read-only (APIs, RSS, server-rendered pages).
Results are leads, not verdicts: verify each one on the employer's own page.
"""
import argparse, datetime, html, json, os, re, sys, time
import requests

HOME = os.path.expanduser(os.environ.get("BATCHHUNT_HOME", "~/batchhunt-data"))
UA = {"User-Agent": "Mozilla/5.0 (BatchHunt job scanner; personal use)"}
ap = argparse.ArgumentParser(); ap.add_argument("--days", type=int, default=14); ap.add_argument("--no-jobspy", action="store_true")
args = ap.parse_args()
cfg = json.load(open(os.path.join(HOME, "search.json"), encoding="utf-8"))
SRC = cfg.get("sources", {})
INC = re.compile(cfg["include_titles"], re.I)
EXC = re.compile(cfg.get("exclude_titles") or r"$^", re.I)
rows = []

def clean(s): return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html.unescape(s or ""))).strip()
def add(src, title, company, loc, url, salary="", date=""):
    title = clean(title)
    if title and INC.search(title) and not EXC.search(title):
        rows.append(dict(src=src, title=title, company=clean(company), loc=clean(str(loc or ""))[:90], url=url, salary=str(salary or ""), date=str(date or "")[:10]))
def get(url, **kw):
    r = requests.get(url, headers=UA, timeout=40, **kw); r.raise_for_status(); return r
def rss_items(text):
    for it in re.findall(r"<item>(.*?)</item>", text, re.S):
        yield lambda k, it=it: html.unescape((re.search(f"<{k}>(.*?)</{k}>", it, re.S) or [None, ""])[1]).replace("<![CDATA[", "").replace("]]>", "")
def source(name):
    def deco(fn):
        if SRC.get(name, False) or (name == "getro" and SRC.get("getro_boards")) or (name == "workable" and cfg.get("workable")):
            try: fn()
            except Exception as e: print(f"[{name}] {str(e)[:120]}", file=sys.stderr)
        return fn
    return deco

@source("himalayas")
def _():
    for off in range(0, 400, 20):
        jobs = get(f"https://himalayas.app/jobs/api?limit=20&offset={off}").json().get("jobs", [])
        for j in jobs:
            sal = f"{j.get('minSalary')}-{j.get('maxSalary')} {j.get('currency','')}" if j.get("minSalary") else ""
            add("himalayas", j.get("title"), j.get("companyName"), ", ".join(j.get("locationRestrictions") or []) or "Worldwide", j.get("applicationLink") or j.get("guid"), sal, j.get("pubDate"))
        if not jobs: break
        time.sleep(0.5)

@source("weworkremotely")
def _():
    for feed in ["remote-design-jobs", "remote-sales-and-marketing-jobs"]:
        for g in rss_items(get(f"https://weworkremotely.com/categories/{feed}.rss").text):
            comp, _, title = g("title").partition(": ")
            add("wwr", title or comp, comp, g("region"), g("link"), "", g("pubDate"))

@source("remotive")
def _():
    for j in get("https://remotive.com/api/remote-jobs?category=design").json().get("jobs", []):
        add("remotive", j["title"], j["company_name"], j.get("candidate_required_location"), j["url"], j.get("salary"), j.get("publication_date"))

@source("remoteok")
def _():
    for j in get("https://remoteok.com/api").json()[1:]:
        add("remoteok", j.get("position"), j.get("company"), j.get("location"), j.get("url"), "", j.get("date"))

@source("jobicy")
def _():
    for j in get("https://jobicy.com/api/v2/remote-jobs?count=50&industry=design-multimedia").json().get("jobs", []):
        add("jobicy", j.get("jobTitle"), j.get("companyName"), j.get("jobGeo"), j.get("url"), "", j.get("pubDate"))

@source("realworkfromanywhere")
def _():
    for g in rss_items(get("https://www.realworkfromanywhere.com/rss.xml").text):
        title, _, comp = g("title").partition(" at ")
        add("rwfa", title, comp, "Anywhere", g("link"), "", g("pubDate"))

@source("dribbble")
def _():
    parts = get("https://dribbble.com/jobs?location=Anywhere").text.split('job-board-job-company">')
    for k in range(1, len(parts)):
        href = re.findall(r'href="(/jobs/\d+-[^"?]+)', parts[k - 1])
        ti = re.search(r'job-board-job-title">([^<]+)', parts[k]); lo = re.search(r'location[^>]*>([^<]+)', parts[k])
        if href and ti: add("dribbble", ti.group(1), parts[k].split("<")[0], (lo.group(1) if lo else "") or "Remote (check)", "https://dribbble.com" + href[-1])

@source("getro")
def _():
    terms = cfg.get("getro_terms") or ["designer", "creative", "brand", "motion"]
    for board in SRC.get("getro_boards", []):
        for q in terms:
            t = get(f"https://{board}/jobs", params={"q": q}).text
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
            if not m: break
            for j in json.loads(m.group(1))["props"]["pageProps"]["initialState"]["jobs"]["found"]:
                loc = ", ".join(j.get("searchableLocations") or []) + (f" | {j['workMode']}" if j.get("workMode") else "")
                lo, hi = j.get("compensationAmountMinCents"), j.get("compensationAmountMaxCents")
                add(board.split(".")[1] if board.count(".") > 1 else board, j.get("title"), (j.get("organization") or {}).get("name"), loc, j.get("url"),
                    f"{(lo or 0)//100}-{(hi or 0)//100}" if lo else "", time.strftime("%Y-%m-%d", time.gmtime(j.get("createdAt") or 0)))
            time.sleep(1)

@source("workable")
def _():
    w = cfg["workable"]; terms = w.get("terms") or cfg.get("jobspy", {}).get("terms", [])
    for q in terms:
        for loc in w.get("locations", []):
            for j in get("https://jobs.workable.com/api/v1/jobs", params={"query": q, "location": loc}).json().get("jobs", []):
                if loc in w.get("remote_only_for", []) and j.get("workplace") != "remote": continue
                add("workable", j.get("title"), (j.get("company") or {}).get("title"), "; ".join(j.get("locations") or []) + f" | {j.get('workplace')}", j.get("url"), "", j.get("created"))
            time.sleep(0.5)

@source("dou_ua")
def _():
    for qs in ["category=Design&remote", "search=motion&remote", "search=brand&remote", "search=art+director&remote", "search=creative&remote"]:
        for g in rss_items(get(f"https://jobs.dou.ua/vacancies/feeds/?{qs}").text):
            m = re.match(r"(.*) в (.*?), (.*)$", g("title"))
            t, c, l = m.groups() if m else (g("title"), "", "")
            add("dou", t, c, l, g("link").split("?")[0], "", g("pubDate"))
        time.sleep(0.5)

# LinkedIn + Indeed via JobSpy (optional)
js = cfg.get("jobspy")
if js and not args.no_jobspy:
    try:
        from jobspy import scrape_jobs
        for term in js.get("terms", []):
            for s in js.get("searches", []):
                try:
                    kw = dict(site_name=[s["site"]], search_term=term, location=s["location"], results_wanted=30, hours_old=24 * js.get("days", args.days))
                    if s.get("country_indeed"): kw["country_indeed"] = s["country_indeed"]
                    if s.get("remote"): kw["is_remote"] = True
                    for _, j in scrape_jobs(**kw).iterrows(): add(s["site"], j.title, j.company, j.location, j.job_url)
                except Exception as e: print(f"[jobspy {s['site']}] {str(e)[:80]}", file=sys.stderr)
                time.sleep(4)
    except ImportError:
        print("[jobspy] not installed; run scripts/setup.sh (skipping LinkedIn/Indeed)", file=sys.stderr)

# dedupe, drop tracked companies
seen, out = set(), []
trk = ""
tp = os.path.join(HOME, "tracker.md")
if os.path.exists(tp): trk = open(tp, encoding="utf-8").read().lower()
for r in rows:
    k = (r["company"].lower(), r["title"].lower())
    if k in seen: continue
    seen.add(k)
    if r["company"] and f"| {r['company'].lower()} |" in trk: continue
    out.append(r)
os.makedirs(os.path.join(HOME, "scans"), exist_ok=True)
fp = os.path.join(HOME, "scans", f"{datetime.date.today()}-candidates.json")
json.dump(out, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(out)} new candidates -> {fp}")
for r in out:
    print(f"{r['src'][:10]:10} | {r['title'][:55]:55} | {r['company'][:24]:24} | {r['loc'][:40]:40} | {r['url']}")
