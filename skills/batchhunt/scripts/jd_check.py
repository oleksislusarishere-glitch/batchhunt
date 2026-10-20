#!/usr/bin/env python3
"""Fetch a job posting from a public ATS and print what decides eligibility.

Usage: jd_check.py <url> [<url> ...]
Supports jobs.ashbyhq.com, (job-)boards(.eu).greenhouse.io, jobs(.eu).lever.co; any other URL falls back to page text.
Prints title, location(s), comp, and snippets about remote/location/language/salary/visa so you can judge fit.
"""
import sys, re, html, requests
H = {"User-Agent": "Mozilla/5.0 (BatchHunt)"}
KW = re.compile(r"[^.\n]{0,120}\b(remote|hybrid|on-?site|office|based in|located|time ?zone|CET|EST|PST|europe|EMEA|EU\b|worldwide|anywhere|salary|€|\$|£|compensation|contract|B2B|authori[sz]|visa|sponsor|German|French|Portuguese|Spanish|Dutch|Italian|Polish|fluent|native|language)\b[^.\n]{0,120}", re.I)
def text(h): return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html.unescape(h or "")))
for url in sys.argv[1:]:
    try:
        if "ashbyhq.com" in url:
            b, jid = re.search(r"ashbyhq\.com/([^/]+)/([0-9a-f-]{36})", url).groups()
            j = next((x for x in requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{b}?includeCompensation=true", headers=H, timeout=30).json()["jobs"] if x["id"] == jid), None)
            if not j: print("##", url, "CLOSED/NOT FOUND"); continue
            meta = f"{j['title']} | {j.get('location')} | +{[s.get('location') for s in j.get('secondaryLocations', [])][:10]} | {(j.get('compensation') or {}).get('compensationTierSummary')}"; t = j.get("descriptionPlain", "")
        elif "greenhouse.io" in url:
            b, jid = re.search(r"greenhouse\.io/(?:embed/job_app\?for=)?([^/&?]+)/?(?:jobs/|.*token=)(\d+)", url).groups()
            j = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs/{jid}", headers=H, timeout=30).json()
            if "title" not in j: print("##", url, "CLOSED/NOT FOUND"); continue
            meta = f"{j['title']} | {j.get('location', {}).get('name')}"; t = text(j.get("content"))
        elif "lever.co" in url:
            eu = ".eu." in url; b, jid = re.search(r"lever\.co/([^/]+)/([0-9a-f-]{36})", url).groups()
            j = requests.get(f"https://api{'.eu' if eu else ''}.lever.co/v0/postings/{b}/{jid}", headers=H, timeout=30).json()
            if "text" not in j: print("##", url, "CLOSED/NOT FOUND"); continue
            meta = f"{j['text']} | {j.get('categories')} | {j.get('workplaceType')} | {j.get('salaryRange')}"
            t = j.get("descriptionPlain", "") + " " + " ".join(text(l.get("content")) for l in j.get("lists", [])) + " " + j.get("additionalPlain", "")
        else:
            r = requests.get(url, headers=H, timeout=30); meta = r.status_code; t = text(r.text)
        print("##", meta, "\n  ", url)
        for m in list(KW.finditer(t))[:12]: print("   -", m.group(0).strip()[:230])
    except Exception as e: print("##", url, "ERR", e)
