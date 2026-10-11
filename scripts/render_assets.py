#!/usr/bin/env python3
"""Render the binary assets: executive CV (PDF), social share image and PNG favicons.

    pip install jinja2 playwright && python3 -m playwright install chromium
    python3 scripts/render_assets.py            # uses Google Fonts over the internet
    python3 scripts/render_assets.py fonts.css  # optional: local @font-face CSS for offline rendering

Re-run after editing src/content.json, then run build.py.
"""
import asyncio
import datetime as dt
import json
import pathlib
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, ASSETS = ROOT / "src", ROOT / "dist" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
c = json.loads((SRC / "content.json").read_text(encoding="utf-8"))
p = c["person"]
LOCAL_FONTS = pathlib.Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else None

env = Environment(loader=FileSystemLoader(str(SRC)), autoescape=select_autoescape(["html", "j2"]))
cv_html = env.get_template("cv.html.j2").render(c=c, p=p, month=dt.date.today().strftime("%B %Y"))

OG = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Hanken+Grotesk:wght@500;600;700&display=swap">
<style>
body{{margin:0;width:1200px;height:630px;background:#111C2E;color:#F1EBDF;font-family:'DM Sans',sans-serif;position:relative;overflow:hidden}}
.g{{position:absolute;inset:0;background-image:linear-gradient(#1E2C47 1px,transparent 1px),linear-gradient(90deg,#1E2C47 1px,transparent 1px);background-size:60px 60px;opacity:.55}}
.l{{position:absolute;left:72px;top:64px;font:500 15px 'DM Sans',sans-serif;letter-spacing:2.5px;text-transform:uppercase;color:#8D96A8;display:flex;gap:16px;align-items:center}}
.l:before{{content:"";width:40px;height:1px;background:#B77955}}
h1{{position:absolute;left:72px;top:118px;margin:0;font:400 92px/0.95 'Clash Grotesk','Hanken Grotesk',sans-serif;letter-spacing:-1.5px;width:760px}}
h1 i{{color:#B77955}}
.n{{position:absolute;left:72px;bottom:64px;font:400 40px 'Clash Grotesk','Hanken Grotesk',sans-serif}}
.d{{position:absolute;left:72px;bottom:38px;font:500 13px 'DM Sans',sans-serif;letter-spacing:1.6px;text-transform:uppercase;color:#E7CFA6}}
.m{{position:absolute;right:64px;top:64px;width:300px;height:502px;border:1px solid #2A3852;background:#182540}}
.m b{{position:absolute;left:0;right:0;top:120px;text-align:center;font:400 150px/1 'Clash Grotesk','Hanken Grotesk',sans-serif;letter-spacing:-4px}}
.m b i{{color:#B77955}}
.m svg{{position:absolute;left:0;bottom:0}}
</style></head><body><div class="g"></div>
<div class="l">Commercial leader · 20+ years of experience</div>
<h1>Turning market opportunity into <i>measurable growth.</i></h1>
<div class="n">{p['name']}</div>
<div class="d">{p['currentRole']} · Roam Electric</div>
<div class="m"><b>SN<i>K</i></b><svg width="300" height="200" viewBox="0 0 300 200"><path d="M24 170H40V156H90V142H112V128H138V114H170V100H212V86H250V72H266V58H280" fill="none" stroke="#B77955" stroke-width="2"/></svg></div>
</body></html>"""

ICON = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700&display=swap">
<style>body{margin:0;width:SIZEpx;height:SIZEpx;background:#111C2E;display:grid;place-items:center;position:relative;overflow:hidden}
.f{position:absolute;inset:calc(SIZEpx*.05);border:calc(SIZEpx*.03) solid #B77955}
b{font:400 calc(SIZEpx*.42)/1 'Clash Grotesk','Hanken Grotesk',sans-serif;color:#F1EBDF;letter-spacing:calc(SIZEpx*-.01);margin-top:calc(SIZEpx*-.08)}b i{color:#B77955}
svg{position:absolute;left:0;bottom:0;width:100%;height:30%}</style></head>
<body><div class="f"></div><b>SN<i>K</i></b><svg viewBox="0 0 64 20" preserveAspectRatio="none"><path d="M10 15h11v-3h11v-3h11v-3h11" fill="none" stroke="#B77955" stroke-width="2"/></svg></body></html>"""


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def page(w, h, html):
            ctx = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg = await ctx.new_page()
            if LOCAL_FONTS:
                await pg.route("https://fonts.googleapis.com/**",
                               lambda r: r.fulfill(status=200, content_type="text/css", body=LOCAL_FONTS))
            await pg.set_content(html, wait_until="networkidle")
            await pg.evaluate("document.fonts.ready")
            return ctx, pg

        ctx, pg = await page(794, 1123, cv_html)
        await pg.pdf(path=str(ASSETS / p["cvFilename"]), format="A4", print_background=True, prefer_css_page_size=True)
        await ctx.close()

        ctx, pg = await page(1200, 630, OG)
        await pg.screenshot(path=str(ASSETS / "og-image.png"))
        await ctx.close()

        for size, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")]:
            ctx, pg = await page(size, size, ICON.replace("SIZE", str(size)))
            await pg.screenshot(path=str(ASSETS / name))
            await ctx.close()
        await browser.close()
    print("Rendered CV PDF, og-image.png and favicons into dist/assets/")

asyncio.run(main())
