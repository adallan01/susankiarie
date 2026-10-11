#!/usr/bin/env python3
"""Build Susan Njeri Kiarie's website.

    python3 build.py

Reads src/content.json (all copy and figures), src/map.json (pre-projected map paths),
src/styles.css, src/main.js and src/index.html.j2, and writes:

    dist/index.html      the deployable site (static; host anywhere, e.g. Vercel or Netlify)
    dist/404.html        branded not-found page
    .artifact/index.html the same page without the <html>/<head> wrapper, for Claude artifact previews

Only dependency: Jinja2 (pip install jinja2).
"""
import datetime as dt
import json
import pathlib
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
ART = ROOT / ".artifact"

c = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
m = json.loads((SRC / "map.json").read_text(encoding="utf-8"))
today = dt.date.today()
now_year = round(today.year + (today.month - 1) / 12 + today.day / 365, 2)

# ---- Map: attach categories and label positions -------------------------------------------
cats = {x["name"]: x for x in c["regions"]["countries"]}
label_names = {"Central African Rep.": "C.A.R."}
label_nudge = {  # (dx, dy) in map units so labels do not collide
    "Kenya": (14, -22), "Uganda": (-6, 2), "Tanzania": (6, 10), "Burundi": (-58, 6),
    "Mozambique": (18, 10), "Zambia": (0, 6), "Ethiopia": (0, 0), "Sudan": (0, 24),
    "Central African Rep.": (0, 4),
}
for ct in m["countries"]:
    info = cats.get(ct["name"])
    ct["cat"] = info["cat"] if info else ""
    dx, dy = label_nudge.get(ct["name"], (0, 0))
    ct["lx"], ct["ly"] = round(ct["c"][0] + dx, 1), round(ct["c"][1] + dy, 1)
    ct["label"] = label_names.get(ct["name"], ct["name"])
missing = set(cats) - {ct["name"] for ct in m["countries"]}
assert not missing, f"countries missing from map: {missing}"

# ---- Portrait panel step line: one equal step per full-time role start ---------------------
starts = sorted(r["start"] for r in c["career"] if r["type"] == "full")
steps, y = [], 448
for s in starts:
    y -= 15
    x = 30 + (s - 2005) / 22 * 340
    steps.append({"x": round(x, 1), "y": y})

# ---- Background "business network" pattern (deterministic) -----------------------------------
import random
rnd = random.Random(7)
pts = []
for gx in range(0, 600, 75):
    for gy in range(0, 420, 70):
        if rnd.random() < 0.55:
            pts.append((gx + rnd.randint(-20, 20), gy + rnd.randint(-18, 18)))
edges = []
for i, a in enumerate(pts):
    near = sorted(pts[:i] + pts[i + 1:], key=lambda b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)[:2]
    for b2 in near:
        e = tuple(sorted([a, b2]))
        if e not in edges:
            edges.append(e)
network = {
    "nodes": [(x, y, rnd.choice([1.2, 1.6, 2.2]), rnd.choice([0.5, 0.8, 1])) for x, y in pts],
    "edges": [(a[0], a[1], b2[0], b2[1]) for a, b2 in edges],
}

# ---- Structured data -----------------------------------------------------------------------
p = c["person"]
jsonld = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": p["name"],
    "givenName": "Susan",
    "additionalName": "Njeri",
    "familyName": "Kiarie",
    "jobTitle": p["currentRole"],
    "worksFor": {"@type": "Organization", "name": p["currentEmployer"]},
    "address": {"@type": "PostalAddress", "addressLocality": "Nairobi", "addressCountry": "KE"},
    "email": f"mailto:{p['email']}",
    "telephone": p["phone"].replace(" ", ""),
    "sameAs": [p["linkedin"]],
    "alumniOf": [
        {"@type": "CollegeOrUniversity", "name": "Daystar University"},
        {"@type": "CollegeOrUniversity", "name": "Limkokwing University of Creative Technology"},
        {"@type": "EducationalOrganization", "name": "Graffins College"},
    ],
    "hasCredential": [{"@type": "EducationalOccupationalCredential", "name": e["award"]} for e in c["education"][:2]],
    "knowsAbout": [x["t"].replace("&", "and") for x in c["about"]["pillars"]],
    "description": c["seo"]["description"],
}
if c["seo"]["canonical"]:
    jsonld["url"] = c["seo"]["canonical"]
jsonld_str = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")

canon = c["seo"]["canonical"].rstrip("/")
og_image = f"{canon}/{c['seo']['ogImage']}" if canon else c["seo"]["ogImage"]

env = Environment(loader=FileSystemLoader(str(SRC)), autoescape=select_autoescape(["html", "j2"]),
                  trim_blocks=False, lstrip_blocks=False)
tpl = env.get_template("index.html.j2")
ctx = dict(
    c=c, map=m, steps=steps, network=network, now_year=now_year, year=today.year, og_image=og_image,
    css=Markup((SRC / "styles.css").read_text(encoding="utf-8")),
    js=Markup((SRC / "main.js").read_text(encoding="utf-8")),
    jsonld=Markup(jsonld_str),
)

DIST.mkdir(exist_ok=True)
(DIST / "assets").mkdir(exist_ok=True)
ART.mkdir(exist_ok=True)
(DIST / "index.html").write_text(tpl.render(full=True, page_title="", **ctx), encoding="utf-8")
(ART / "index.html").write_text(tpl.render(full=False, page_title="Susan Kiarie Portfolio", **ctx), encoding="utf-8")

# ---- 404 page --------------------------------------------------------------------------------
css = (SRC / "styles.css").read_text(encoding="utf-8")
page404 = f"""<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Page not found · {p['name']}</title><meta name="robots" content="noindex">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Hanken+Grotesk:wght@500;600;700&display=swap">
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-grotesk@400,500,600,700&display=swap">
<style>{css}
.nf {{ min-height: 100vh; display: grid; align-content: center; padding-block: 64px; }}
.nf h1 {{ font-family: var(--serif); font-size: var(--t-display); line-height: .95; margin-top: 28px; }}
.nf p.t {{ margin-top: 24px; color: var(--on-navy-2); max-width: 40ch; font-size: var(--step-1); }}
.nf .hero-cta {{ margin-top: 32px; }}
</style></head>
<body class="s-navy"><main class="nf s-navy grain hero"><div class="wrap">
<p class="kicker">Error 404</p>
<h1>This page isn’t <span class="em">on the map.</span></h1>
<p class="t">The link may be out of date. Everything about Susan’s work is on the home page.</p>
<div class="hero-cta"><a class="btn btn-solid" href="/">Go to the home page</a><a class="btn btn-line" href="/#contact">Contact Susan</a></div>
</div></main></body></html>
"""
(DIST / "404.html").write_text(page404, encoding="utf-8")

# Copy static assets into the artifact preview folder
if (DIST / "assets").exists():
    shutil.copytree(DIST / "assets", ART / "assets", dirs_exist_ok=True)

print(f"Built dist/index.html ({(DIST / 'index.html').stat().st_size // 1024} KB), dist/404.html, .artifact/index.html")
