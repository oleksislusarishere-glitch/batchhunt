#!/usr/bin/env python3
"""Build a tailored, ATS-friendly CV PDF from cv.json.

Usage:
  build_cv.py <slug> <variant> ["Headline"] [--portfolio URL] [--cv path/to/cv.json]
  build_cv.py sample <variant>            # quick preview during onboarding

Reads $BATCHHUNT_HOME/cv.json (default ~/batchhunt-data). Writes
$BATCHHUNT_HOME/apps/<slug>/<file_name> (plus the .html next to it).
PDF rendering: headless Chrome/Chromium if found, else Python Playwright.
Only standard library is required for the HTML step.
"""
import argparse, html, json, os, shutil, subprocess, sys, tempfile

HOME = os.path.expanduser(os.environ.get("BATCHHUNT_HOME", "~/batchhunt-data"))
E = lambda s: html.escape(str(s or ""))

CSS = """
@page { size: A4; margin: 14mm 15mm; }
* { box-sizing: border-box; }
body { font-variant-ligatures: none; font-feature-settings: "liga" 0; font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1a1a1a; font-size: 10pt; line-height: 1.42; margin: 0; }
h1 { font-size: 21pt; margin: 0; letter-spacing: -0.3px; }
.headline { font-size: 11.5pt; color: #333; margin: 2px 0 6px; font-weight: 600; }
.contact { font-size: 9pt; color: #444; }
.contact a { color: #444; text-decoration: none; }
h2 { font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #ccc; padding-bottom: 2px; margin: 14px 0 6px; }
.job { margin: 0 0 8px; break-inside: avoid; }
.job-head { display: flex; justify-content: space-between; gap: 12px; }
.job-head b { font-size: 10.5pt; }
.meta { color: #555; font-size: 9pt; white-space: nowrap; }
.ctx { color: #555; font-size: 9pt; }
ul { margin: 3px 0 0 16px; padding: 0; }
li { margin: 0 0 2px; }
.comp { font-size: 9.5pt; }
.skills p { margin: 0 0 3px; }
"""

def render(cv, variant_key, headline=None, portfolio=None):
    v = cv["variants"][variant_key]
    c = dict(cv["candidate"])
    links = list(c.get("links", []))
    if portfolio:
        links = [l for l in links if l.get("label", "").lower() != "portfolio"]
        links.insert(0, {"label": "Portfolio", "url": portfolio})
    contact = " · ".join([E(c.get("location")), E(c.get("email")), E(c.get("phone"))] +
                         [f'<a href="{E(l["url"])}">{E(l["url"].replace("https://", "").replace("http://", ""))}</a>' for l in links])
    out = [f"<h1>{E(c['name'])}</h1>", f'<div class="headline">{E(headline or v["title"])}</div>', f'<div class="contact">{contact}</div>']
    out.append(f'<h2>Summary</h2><p>{E(v["summary"])}</p>')
    if v.get("competencies"):
        out.append(f'<h2>Core competencies</h2><p class="comp">{" · ".join(E(x) for x in v["competencies"])}</p>')
    out.append("<h2>Experience</h2>")
    order = v.get("order", {})
    for job in cv["experience"]:
        b = job.get("bullets", {})
        if isinstance(b, list):
            items = b
        else:
            keys = order.get(job["company"]) or list(b.keys())
            items = [b[k] for k in keys if k in b]
        place = " · ".join(x for x in [job.get("location"), job.get("dates")] if x)
        out.append(f'<div class="job"><div class="job-head"><span><b>{E(job["role"])}</b>, {E(job["company"])}'
                   + (f' <span class="ctx">({E(job["context"])})</span>' if job.get("context") else "")
                   + f'</span><span class="meta">{E(place)}</span></div>'
                   + ("<ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>" if items else "") + "</div>")
    if cv.get("projects"):
        out.append("<h2>Projects</h2><ul>" + "".join(
            f'<li><b>{E(p["name"])}</b>' + (f' (<a href="{E(p["url"])}">{E(p["url"].replace("https://", ""))}</a>)' if p.get("url") else "")
            + f': {E(p.get("description"))}</li>' for p in cv["projects"]) + "</ul>")
    if cv.get("skills"):
        out.append('<h2>Skills</h2><div class="skills">' + "".join(
            f'<p><b>{E(s["category"])}:</b> {E(s["items"])}</p>' for s in cv["skills"]) + "</div>")
    if cv.get("education"):
        out.append("<h2>Education</h2>" + "".join(
            f'<p><b>{E(e["title"])}</b>, {E(e.get("org"))}' + (f' · {E(e["year"])}' if e.get("year") else "") + "</p>" for e in cv["education"]))
    if cv.get("languages"):
        out.append(f'<h2>Languages</h2><p>{E(cv["languages"])}</p>')
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{E(c["name"])} CV</title><style>{CSS}</style></head><body>{"".join(out)}</body></html>'

def find_chrome():
    for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]:
        if os.path.exists(p): return p
    for n in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "chrome"]:
        if shutil.which(n): return shutil.which(n)
    return None

def to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if chrome:
        with tempfile.TemporaryDirectory() as prof:
            r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={prof}",
                                f"--print-to-pdf={pdf_path}", "file://" + os.path.abspath(html_path)], capture_output=True, text=True, timeout=120)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0: return True
        print(r.stderr[-500:], file=sys.stderr)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(); pg.goto("file://" + os.path.abspath(html_path))
            pg.pdf(path=pdf_path, format="A4", print_background=True); b.close()
        return True
    except Exception as e:
        print("No Chrome found and Playwright unavailable:", e, "\nInstall Chrome, or: pip install playwright && playwright install chromium", file=sys.stderr)
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("variant"); ap.add_argument("headline", nargs="?")
    ap.add_argument("--portfolio"); ap.add_argument("--cv", default=os.path.join(HOME, "cv.json"))
    a = ap.parse_args()
    cv = json.load(open(a.cv, encoding="utf-8"))
    if a.variant not in cv.get("variants", {}):
        sys.exit(f"Unknown variant '{a.variant}'. Available: {', '.join(cv.get('variants', {}))}")
    d = os.path.join(HOME, "apps", a.slug); os.makedirs(d, exist_ok=True)
    name = cv.get("file_name") or (cv["candidate"]["name"].replace(" ", "_") + "_CV.pdf")
    h = os.path.join(d, name.replace(".pdf", ".html")); p = os.path.join(d, name)
    open(h, "w", encoding="utf-8").write(render(cv, a.variant, a.headline, a.portfolio))
    print(p if to_pdf(h, p) else h)

if __name__ == "__main__":
    main()
