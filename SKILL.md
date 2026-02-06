# Cariboo Signals — Technical Reference

## Repos & URLs
| System | Repo | Live site |
|---|---|---|
| RSS | github.com/zirnhelt/super-rss-feed | zirnhelt.github.io/super-rss-feed/ |
| Podcast | github.com/zirnhelt/curated-podcast-generator | zirnhelt.github.io/curated-podcast-generator/ |

Local paths: `~/super-rss-feed`, `~/curated-podcast-generator`

---

## RSS Feed System — key files
- `super_rss_curator_json.py` — main script (only curator that runs)
- `fetch_images.py` — OpenGraph scraping + favicon fallback
- `config_loader.py` — loads config/ directory
- `config/` — categories.json, category_rules.json, filters.json, limits.json, system.json, feeds.json, scoring_interests.txt
- `feeds.opml` — 50+ source feeds
- `.github/workflows/generate-feed.yml` — runs 3x daily (6 AM / 2 PM / 10 PM Pacific)
- `index.html` — feed website
- `scored_articles_cache.json`, `shown_articles_cache.json`, `wlt_cache.json` — runtime caches, committed by workflow
- `ROADMAP.md` — planned features and improvements

## Podcast Generator — key files
- `podcast_generator.py` — main script (only generator that runs)
- `dedup_articles.py` — cross-episode dedup (checks last 7 days of citations)
- `config_loader.py` — loads config/ directory
- `config/` — podcast.json, hosts.json, themes.json, credits.json, interests.txt
- `.github/workflows/daily-podcast.yml` — runs daily at 4 AM Pacific
- `generate_html.py` — builds index.html from config
- `fix_rss.py` — standalone RSS repair utility (manual)
- `episode_memory.json`, `host_personality_memory.json` — runtime state
- `ROADMAP.md` — planned features and improvements

---

## Dead files — do not touch
**RSS repo:** `super_rss_curator.py`, `super_rss_curator_cached.py`, all `*.backup*`, all `fix_*.py`, `super_rss_curator_json_old.py`

**Podcast repo:** `podcast_generator_backup*.py`, `podcast_generator_old.py`, `podcast_generator_with_music.py`, `index_old.html`

---

## Active gotchas
1. **WLT cache corruption** — entries can become bare strings instead of dicts. Always guard with `isinstance(v, dict)` before accessing.
2. **Cache merge conflicts** — GitHub Actions commits caches; local pulls can conflict. Resolve by keeping remote version.
3. **RSS feed blocking** — some tech sites reject default User-Agent. Both `fetch_images.py` and `fetch_feed_articles()` send custom UA headers.
4. **shown_articles_cache bloat** — cleanup logic in `load_shown_cache()` if it grows past ~300K.
5. **Podcast RSS XML escaping** — bare `&` breaks DOMParser. All RSS output must use `saxutils.escape()`.
6. **Mint venv required** — local Python: `python -m venv venv && source venv/bin/activate`

---

## Session workflow
1. User runs `git pull` in relevant repo
2. User states what's broken or wanted + which file
3. Claude fetches/views only that file
4. Claude proposes change (small, reviewable)
5. User approves
6. Claude executes str_replace + syntax check
7. User decides commit/push

**Rules:** Never build automatically. Prompt first. All instructions must be copy-pastable bash. Separate steps if review needed between them.

---

## Project snapshot
Run `~/Downloads/project_snapshot_script.sh` to generate fresh snapshot of both projects for uploading to Project Knowledge. Script pulls latest from GitHub, captures core files (not backups/caches), and includes last 50 commits.

---

## Environment
- GitHub ID: zirnhelt
- Hosting: GitHub Pages (static files)
- Home system: Linux Mint
- Editor: gedit (exploring VS Code for Python)
- Browser: Chrome
- RSS reader: Inoreader free edition
