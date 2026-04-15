# Bulevardi Lounas

Daily-updating lunch menu page for restaurants on Bulevardi, Helsinki. Scrapes lounaat.info via GitHub Actions, serves the result as a static site on GitHub Pages.

## Setup (one-time, ~5 min)

1. **Create the repo**
   - On github.com → New repository → name it whatever (e.g. `bulevardi-lounas`) → Public → Create
   - Upload all four files from this folder: `index.html`, `menus.json`, `scripts/scrape.py`, `.github/workflows/update-menus.yml`
     (Keep the folder structure. The web upload supports drag-and-drop with folders.)

2. **Enable GitHub Pages**
   - Repo → Settings → Pages
   - Source: **Deploy from a branch**, Branch: **main**, Folder: **/ (root)** → Save
   - Wait ~1 min. Your site is live at `https://YOUR-USERNAME.github.io/bulevardi-lounas/`

3. **Allow Actions to push back to the repo**
   - Repo → Settings → Actions → General
   - Under **Workflow permissions**: select **Read and write permissions** → Save

4. **Run it once manually to populate `menus.json`**
   - Repo → Actions tab → "Update lunch menus" → **Run workflow** → Run workflow
   - Wait ~30 sec. It scrapes, commits, and `menus.json` is filled in.

5. **Open your site.** Done. Bookmark it on your phone.

## How it works

- `scripts/scrape.py` fetches each lounaat.info page, picks today's day-block, parses dishes/prices/tags, writes `menus.json`.
- `.github/workflows/update-menus.yml` runs the scraper every weekday at 09:30 Helsinki time and commits the updated JSON.
- `index.html` loads `menus.json` on page load — no API calls, no servers.

## Editing restaurants

Edit two places to keep them in sync:
- `index.html` → the `RESTAURANTS` array (display info + `lounaat:` slug)
- `scripts/scrape.py` → the `SLUGS` list (just the slugs)

The slug is the part after `/lounas/` in a lounaat.info URL, e.g. `https://www.lounaat.info/lounas/southpark/helsinki` → `southpark`.

## Triggering an update manually

Repo → Actions → Update lunch menus → Run workflow. Useful if a restaurant updates their menu mid-week.
