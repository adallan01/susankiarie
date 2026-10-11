# Susan Njeri Kiarie: executive portfolio website

A static, single-page executive portfolio. It has no framework and no runtime dependencies. `dist/` is the finished website and can be deployed as it is.

Page order: identity hero, What I bring, Executive impact (featured and secondary results with rolling-digit counters), Commercial milestones (intro band, three editorial features, two compact ones), Opening new markets role after role (sticky map that lights up each market entry as you scroll, plus the expandable career chronology), Where I’ve made an impact (3D rotating logo gallery), Leadership, Education, Contact.

Type (matching spironet.com): Clash Grotesk for headlines and figures, DM Sans for everything else. Clash Grotesk is free from Fontshare (ITF Free Font License) and loads from api.fontshare.com on the live site; Hanken Grotesk is the fallback, and it is what the Claude preview shows because the preview can only load Google Fonts. To self-host Clash Grotesk, download it from fontshare.com, put the .woff2 files in dist/assets/fonts/ and swap the Fontshare <link> for an @font-face rule. Palette: ivory #F6F2EA, stone #EAE5DC, midnight navy #111C2E, copper #B77955. Small copper text uses a darker #8A5536 so it meets AA contrast on ivory.

## What's in the folder

```
dist/                      ← deploy this folder
  index.html               the website (HTML, CSS and JS in one file)
  404.html                 branded not-found page
  robots.txt
  vercel.json              clean URLs and caching headers for Vercel
  assets/
    Susan-Njeri-Kiarie-Executive-CV.pdf   downloadable 3-page executive CV (no referees, no home address)
    og-image.png           1200×630 social share image
    favicon.svg, favicon-32.png, apple-touch-icon.png, icon-512.png
    logos/                 employer logos (trimmed, transparent PNGs)
    bg/                    the twelve section background photographs. Every section is dark: hero = stage, What I bring = panels, impact = gold spotlight, milestones intro = hanging frames, ecoligo = gold dust, Sagemcom = gold streaks, Vodafone = single spotlight, consultancy/Mobiserve = stool and lamp, markets = faint gold streaks, logos = frame wall, leadership = silver spotlights, education = spotlight cone, contact = stage floor
src/
  content.json             ALL copy, figures, roles, education and contact details
  index.html.j2            page template
  styles.css               design system (colour tokens, type scale, layout)
  main.js                  menu, reveals, count-ups, map legend, copy buttons, CV download
  map.json                 pre-projected map of East, Central and Southern Africa (Natural Earth via world-atlas)
  cv.html.j2               template for the PDF CV
scripts/render_assets.py   regenerates the CV PDF, share image and PNG favicons
scripts/prepare_logos.py   trims supplied logo files and removes their light backgrounds
build.py                   regenerates dist/index.html and dist/404.html from src/
```

## Editing content

1. Edit `src/content.json`. Every figure in it is taken from Susan's April 2026 CV. Do not add figures that aren't in the CV.
2. Run `python3 build.py` (needs `pip install jinja2`).
3. If you changed anything that also appears in the CV PDF or share image, run `python3 scripts/render_assets.py` first (needs `pip install playwright && python3 -m playwright install chromium`).

## Adding Susan's portrait

1. Save a high-resolution portrait (at least 1000 × 1250 px, portrait orientation) as `dist/assets/portrait.jpg`.
2. In `src/content.json`, set `"portrait": "assets/portrait.jpg"`.
3. Run `python3 build.py`. The SNK monogram panel in the hero is replaced by the photo.

## Adding articles, interviews or talks

Add items to the `insights` list in `src/content.json`. Use the shape shown in `_insightsHelp`. An Insights section and nav link appear automatically once the list has at least one item.

## Deploying

**Vercel (dashboard):** create a new project, upload or connect the repo, set the *Output Directory* to `dist` and leave the build command empty.
**Vercel CLI:** `cd dist && npx vercel --prod`
**Netlify:** drag the `dist` folder onto app.netlify.com/drop.

After the first deploy, put the live URL in `seo.canonical` in `content.json` (for example `https://susankiarie.com`) and rebuild. This adds the canonical tag and makes the share-image URL absolute, which LinkedIn and WhatsApp previews need.

## Logos

Logos sit in `dist/assets/logos/`. Each organisation is listed under `organisations.items` in `content.json`, with its logo path, display height (`h`) and official URL. Leave `url` empty to show a tile without a link.

- Telkom Kenya's logo was supplied for Zote Telkom but was not used. Zote Telkom (formerly Net@home Wireless Networks) is a different company. It appears as a name tile.
- Adrian Kenya has no link: adriankenya.com currently shows a hosting login page instead of a company homepage.
- Power-Wiz uses the PEL logo supplied on 11 Oct 2026. Its colours match power-wiz.co.ke.
- The GSK logo supplied is an earlier GSK mark. GSK adopted a new visual identity in 2022, so you may want to swap in the current logo.

## Points to confirm with Susan

- **Portrait:** none was available. The saved WhatsApp page held only a low-resolution video thumbnail.
- **Job title wording:** the CV says "Head Sales/Deputy Managing Director" at Sagemcom. The site uses "Head of Sales / Deputy Managing Director", as specified in the brief.
- **Award:** the Vodacom "Best IoT/M2M Sales Person of the Year 2015–2016" award is included because it is in the CV.
- **Mobiserve breakdown:** the CV gives "50% … (34% in Kenya and 18% in Uganda and Tanzania)". The site repeats this without interpreting it.
- **Contact details:** the email, phone and LinkedIn are published as supplied. No home address or referee details appear anywhere.
