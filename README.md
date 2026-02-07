# Super RSS Feed Curator

AI-powered RSS aggregator that consolidates 80+ feeds into categorized, curated JSON feeds using Claude API.

## Features

- **Aggregates** RSS feeds from OPML + Williams Lake Tribune scraping + Google News discovery
- **Deduplicates** using URL + fuzzy title matching, with source-aware priority (print sources win over broadcast)
- **Filters** blocked sources and keywords (sports, advice columns, etc.)
- **Scores** articles 0-100 with Claude API based on configurable interests
- **Source preferences** — classify sources as print or broadcast with per-type score adjustments and article caps
- **Categorizes** into 7 feeds: local, ai-tech, climate, homelab, science, scifi, news
- **Diversifies** output with per-source limits that respect source type
- **Caches** scored articles to minimize API calls (~80-90% cache hit rate)

## Setup

### 1. Fork this repository

Click "Fork" on GitHub to create your own copy.

### 2. Add your OPML file

Replace `feeds.opml` with your RSS feed list, or edit the existing one.

### 3. Set up API key

1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Claude API key from https://console.anthropic.com

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

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run
python super_rss_curator_json.py feeds.opml

# Validate config
python config_loader.py
```

## How It Works

1. **Fetch** — Pulls articles from all OPML feeds + scrapes Williams Lake Tribune (last 48 hours)
2. **Filter** — Removes blocked sources and keywords
3. **Deduplicate** — Eliminates duplicates by URL and fuzzy title matching; preferred sources (local, then print) win ties
4. **Score** — Claude API rates each article 0-100 based on your interests; cached for 6 hours
5. **Source preferences** — Adjusts scores by source type (print boost, broadcast penalty)
6. **Quality filter** — Drops articles below minimum score threshold
7. **Categorize** — Assigns articles to 7 category feeds using keyword rules
8. **Diversify** — Limits articles per source, with per-type caps from source preferences
9. **Output** — Generates JSON Feed 1.1 files and OPML index

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

**Claude API costs?**
- ~0.5-2 cents per run depending on cache hit rate
- Scored article cache reduces API calls by 65-90%
- Monitor usage at https://console.anthropic.com

## Contributors

- [zirnhelt](https://github.com/zirnhelt) - Creator and maintainer
- [Claude](https://claude.ai) - AI contributor

## License

MIT
