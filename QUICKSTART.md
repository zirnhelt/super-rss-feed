# Quick Start

This repo runs itself: GitHub Actions builds the feeds nightly (dispatched by the
Cloudflare Worker in curated-podcast-generator, with a 10:00 UTC backstop cron) and
publishes them to `https://zirnhelt.github.io/super-rss-feed/`.

**Subscribe:** add any `feed-<category>.json` from that site to a JSON Feed reader,
or `feed-local.xml` to an RSS reader. `curated-feeds.opml` lists them all.

**Work on it:**

```bash
python3.11 -m venv venv && venv/bin/pip install -r requirements-lock.txt pytest
venv/bin/python config_loader.py && venv/bin/python -m pytest tests/ -q
```

That's free and needs no API keys. A full pipeline run spends on Anthropic, Cohere
and (unless `USE_SEARCH_APIS=false`) the Brave cap shared with the podcast, and it
rewrites committed caches: see README → Local Testing before you start one.

**Tune it:** everything is in `config/` (filters, slots, interests, podcast
charters). See CLAUDE.md for what each file controls, and which knobs the weekly
calibration agent owns.
