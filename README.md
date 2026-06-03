# Super RSS Feed Curator

AI-powered RSS aggregator that consolidates 80+ feeds into categorized, curated JSON feeds using Claude API.

## Features

- **Aggregates** RSS feeds from OPML + Williams Lake Tribune scraping + Google News discovery
- **Deduplicates** using URL + fuzzy title + term-set containment matching, with source-aware priority (local > print > broadcast)
- **Cross-run dedup** suppresses the same story arriving from a new source/URL on a later run
- **Filters** blocked sources and keywords (sports, advice columns, etc.)
- **Scores** articles 0-100 with Claude API (or Cohere Rerank) based on configurable interests
- **Source preferences** — classify sources as print or broadcast with per-type score adjustments and article caps
- **Categorizes** into 8 feeds: local, ai-tech, climate, homelab, wellness, science, scifi, news
- **Diversifies** output with per-source limits that respect source type
- **Caches** scored articles to minimize API calls (~80-90% cache hit rate)
- **Podcast feeds** — 7 themed daily feeds built from a rolling 7-day article pool
- **Image fetching** — scrapes Open Graph images for quality articles

## Setup

### 1. Fork this repository

Click "Fork" on GitHub to create your own copy.

### 2. Add your OPML file

Replace `feeds.opml` with your RSS feed list, or edit the existing one.

### 3. Set up API keys

**Required:**
1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Claude API key from https://console.anthropic.com

**Optional — Cohere API (enables semantic features):**
5. Add another secret: `COHERE_API_KEY`
6. Value: Your Cohere API key from https://dashboard.cohere.com

When `COHERE_API_KEY` is set, the pipeline automatically switches to Cohere for scoring,
deduplication, and podcast theme scoring (see [Cohere Integration](#cohere-integration) below).
`ANTHROPIC_API_KEY` is still required for the final content scrub pass.

**Optional — Brave Search API (fallback for blocked feeds):**
7. Add another secret: `BRAVE_API_KEY`
8. Value: Your Brave Search API key from https://api.search.brave.com

When `BRAVE_API_KEY` is set, feeds that return HTTP 403 are retried via Brave Search so
blocked sources still contribute articles.

### 4. Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `/ (root)`
4. Save

### 5. Run the workflow

1. Go to Actions tab
2. Click "Generate Super RSS Feed"
3. Click "Run workflow"

Your feeds will be available at:
```
https://YOUR-USERNAME.github.io/super-rss-feed/feed-local.json
https://YOUR-USERNAME.github.io/super-rss-feed/feed-news.json
https://YOUR-USERNAME.github.io/super-rss-feed/feed-ai-tech.json
...
```

The workflow runs automatically **twice daily** (4:30 AM and 8:30 PM Pacific).
Each run fetches the last 48 hours of articles and merges new ones into a 7-day rolling feed.

## Configuration

All configuration lives in the `config/` directory:

| File | Purpose |
|------|---------|
| `limits.json` | Feed size, retention, per-source caps, score thresholds |
| `filters.json` | Blocked sources and keywords |
| `categories.json` | Category definitions (name, emoji, description) |
| `category_rules.json` | Include/exclude keyword rules for categorization |
| `scoring_interests.txt` | Claude scoring prompt with interest hierarchy |
| `source_preferences.json` | Source type classifications and per-type preferences |
| `feeds.json` | Output feed metadata (titles, descriptions, base URL) |
| `system.json` | Cache settings, URLs, lookback window |
| `podcast_schedule.json` | Themed daily podcast feed schedule |

### Source preferences

`config/source_preferences.json` lets you classify sources by type and set per-type behavior:

```json
{
  "source_types": {
    "broadcast": {
      "score_adjustment": -15,
      "max_per_source": 3
    },
    "print": {
      "score_adjustment": 5,
      "max_per_source": 10
    }
  },
  "source_map": {
    "CFJC Today Kamloops": "broadcast",
    "CTV News": "broadcast",
    "Williams Lake Tribune": "print",
    "The Tyee": "print"
  }
}
```

Sources not in the map use the defaults from `limits.json` (8 per source, no score adjustment).

### Scoring interests

Edit `config/scoring_interests.txt` to set your interest hierarchy:

```
PRIMARY INTERESTS (Score 70-100):
- AI/ML infrastructure and telemetry
- Climate tech and renewable energy
- Williams Lake and Cariboo local news

SECONDARY INTERESTS (Score 40-69):
- Systems thinking and complex systems
- Homelab and self-hosting

AVOID (Score 0-20):
- Celebrity news, gossip
- Sports coverage
```

### Podcast schedule

`config/podcast_schedule.json` defines 7 themed daily feeds. Each day has:

- **label** — human name for the theme (e.g. "Wild Spaces & Outdoor Life")
- **categories** — which content categories to draw from primarily
- **keywords** — boost words for article selection ranking
- **scoring_prompt** — detailed theme relevance prompt sent to Claude/Cohere
- **min_score** — minimum base quality score for the article pool
- **holdover_threshold** — minimum theme score to bank an article for future episodes

Articles that score exceptionally well on an upcoming day's theme are automatically
routed and held over so they surface on the right episode rather than being consumed
early.

## Cohere Integration

When `COHERE_API_KEY` is set as a GitHub Actions secret (or local env var), the pipeline
activates Cohere-powered features automatically. No config changes needed — removing the
secret reverts to Claude-only behaviour.

| Feature | Without Cohere | With Cohere |
|---|---|---|
| Article scoring | Claude Haiku (batch=15) | Cohere Rerank against interest query |
| Category assignment | Claude in scoring call | Keyword rules (`category_rules.json`) |
| Story group labels | Claude string matching | Embedding cosine clustering |
| Deduplication | URL hash + fuzzy title + term-set | + cosine similarity pass |
| Podcast theme scoring | Claude Haiku (async batch) | Cohere Rerank per theme |
| Feed discovery scoring | Claude Haiku | Cohere Rerank (Claude fallback) |
| Final headline scrub | Claude Haiku | **Unchanged — always Claude** |

The final scrub always uses Claude because nuanced content judgement ("is this primarily
about sports?") benefits from an LLM reasoning over a ranker.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys (COHERE_API_KEY and BRAVE_API_KEY are optional)
export ANTHROPIC_API_KEY='your-key-here'
export COHERE_API_KEY='your-cohere-key'   # optional
export BRAVE_API_KEY='your-brave-key'     # optional

# Run
python super_rss_curator_json.py feeds.opml

# Validate config
python config_loader.py

# Recover feeds from the 7-day podcast cache (after a scoring outage)
python super_rss_curator_json.py --bootstrap-feeds
```

## How It Works

1. **Fetch** — Pulls articles from all OPML feeds (last 48 hours) + scrapes Williams Lake Tribune. Google News proxy URLs are unwrapped to real article links. Feeds returning HTTP 403 fall back to Brave Search if `BRAVE_API_KEY` is set.
2. **Filter** — Removes blocked sources and keywords; context-aware rules allow local coverage of otherwise-blocked topics.
3. **Deduplicate** — Eliminates duplicates by URL hash, fuzzy title similarity, and term-set containment (catches different headlines covering the same story). Preferred sources win ties: local > print > broadcast.
4. **Cross-run dedup** — Compares new article term-sets against recently-shown articles to suppress the same story appearing again from a new URL.
5. **Score** — Claude API (or Cohere Rerank) rates each article 0-100 based on your interests; results cached for 48 hours.
6. **Enforce local priority** — Post-scoring pass guarantees any article mentioning local signals (Williams Lake, Cariboo, etc.) scores 80+ and lands in the local feed.
7. **Source preferences** — Adjusts scores by source type (print boost, broadcast penalty).
8. **Quality filter** — Drops articles below minimum score threshold (default 30). Per-category floor rescue ensures niche categories always get a few candidates.
9. **Final scrub** — Claude Haiku reviews all headlines to catch sports, celebrity gossip, and AI fluff that slipped past keyword filters.
10. **Images** — Open Graph images are fetched for up to 50 articles per run.
11. **Categorize** — Assigns articles to 8 category feeds using keyword rules; cross-category dedup drops news articles already covered by a specific category.
12. **Podcast cache** — Quality articles are saved to a 7-day rolling cache. At ingest, all articles are scored for every podcast theme in one Claude batch (or Cohere calls), so daily podcast generation needs zero additional API calls.
13. **Podcast feed** — Today's themed feed is generated from the weekly pool, skipping articles already used in the last 7 days of episodes and routing articles that clearly belong to an upcoming day's theme.
14. **Diversify** — Limits articles per source, with per-type caps from source preferences.
15. **Merge & output** — New articles are merged with retained articles from the previous 7 days (story-overlap dedup removes stale versions of the same story). Generates JSON Feed 1.1 files and a curated OPML index.

## Podcast Feeds

The pipeline generates 7 themed daily podcast feeds from a rolling 7-day article pool:

| Day | Theme |
|-----|-------|
| Monday | Arts, Culture & Digital Storytelling |
| Tuesday | Working Lands & Industry |
| Wednesday | Gear, Gadgets & Practical Tech |
| Thursday | Indigenous Lands & Innovation |
| Friday | Wild Spaces & Outdoor Life |
| Saturday | Cariboo Local Affairs |
| Sunday | Science, Wonder & the Natural World |

Each feed is a JSON Feed 1.1 file (`feed-podcast-{day}.json`) with extended metadata
including per-article theme scores, quality scores, and source category.

**Holdover cache** — Articles that score well on a theme but weren't consumed that week
are banked for up to 4 weeks and can resurface on the same day's episode in a later run.

## Troubleshooting

**Feed not updating?**
- Check Actions tab for errors
- Verify `ANTHROPIC_API_KEY` secret is set
- Ensure GitHub Pages is enabled on `gh-pages` branch

**Too many/few articles?**
- Adjust `max_feed_size` in `config/limits.json`
- Change `min_claude_score` threshold
- Modify `max_per_source` limits

**Too much broadcast news?**
- Increase the broadcast `score_adjustment` penalty in `config/source_preferences.json`
- Lower the broadcast `max_per_source` cap
- Add more sources to the broadcast list in `source_map`

**Feed drained after a scoring outage?**
- Run `python super_rss_curator_json.py --bootstrap-feeds` to repopulate from the 7-day podcast cache
- The CI workflow does this automatically when any feed drops below 20 items

**Claude API costs?**
- ~0.5-2 cents per run depending on cache hit rate
- Scored article cache reduces API calls by 65-90%
- Monitor usage at https://console.anthropic.com
- With `COHERE_API_KEY` set, Claude is only used for the final scrub pass (significant reduction)

## Contributors

- [zirnhelt](https://github.com/zirnhelt) - Creator and maintainer
- [Claude](https://claude.ai) - AI contributor

## License

MIT
