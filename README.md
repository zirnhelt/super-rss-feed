# Super RSS Feed Curator

AI-powered RSS aggregator that consolidates 50+ feeds into one curated feed using Claude API.

## Features

- **Aggregates** all your OPML feeds into one unified feed
- **Deduplicates** using URL + fuzzy title matching
- **Filters** sports, Fox News, advice columns
- **Scores** articles with Claude API based on your interests
- **Diversifies** output with per-source limits
- **Outputs** top 250 articles daily

## Setup

### 1. Fork this repository

Click "Fork" on GitHub to create your own copy.

### 2. Add your OPML file

Replace `feeds.opml` with your RSS feed list:

```bash
# Either use the enhanced categorized version or your Feedly export
cp enhanced_feed_list_categorized.opml feeds.opml
# OR
cp feedly-*.opml feeds.opml
```

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

Your feed will be available at:
```
https://YOUR-USERNAME.github.io/super-rss-feed/super-feed.xml
```

## Configuration

Edit `super_rss_curator.py` to customize:

```python
MAX_ARTICLES_OUTPUT = 250      # Number of articles in output
MAX_PER_SOURCE = 5             # Max articles per source
LOOKBACK_HOURS = 48            # How far back to fetch
MIN_CLAUDE_SCORE = 30          # Minimum relevance score

# Add/remove blocked sources
BLOCKED_SOURCES = ["fox news", "foxnews"]

# Add/remove blocked keywords
BLOCKED_KEYWORDS = [
    "nfl", "nba", "mlb", "nhl",
    "dear abby", "ask amy"
]
```

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run
python super_rss_curator.py feeds.opml

# Check output
open super-feed.xml
```

## How It Works

1. **Fetch**: Pulls articles from all OPML feeds (last 48 hours)
2. **Filter**: Removes sports, Fox News, advice columns
3. **Dedupe**: Eliminates duplicates by URL and fuzzy title matching
4. **Score**: Claude API rates each article 0-100 based on your interests
5. **Diversify**: Limits articles per source (default: 5 max)
6. **Output**: Top 250 articles sorted by relevance score

## Customizing Interests

Edit the `interests` string in `score_articles_with_claude()`:

```python
interests = """
- AI/ML infrastructure and telemetry
- Systems thinking and complex systems
- Climate tech and sustainability
- Your interests here...
"""
```

## Troubleshooting

**Feed not updating?**
- Check Actions tab for errors
- Verify `ANTHROPIC_API_KEY` secret is set
- Ensure GitHub Pages is enabled on `gh-pages` branch

**Too many/few articles?**
- Adjust `MAX_ARTICLES_OUTPUT`
- Change `MIN_CLAUDE_SCORE` threshold
- Modify `MAX_PER_SOURCE` limits

**Claude API costs?**
- ~0.5-2 cents per run with 250 articles
- ~$0.30-0.60/month for daily runs
- Monitor usage at https://console.anthropic.com

## Contributors

- [zirnhelt](https://github.com/zirnhelt) - Creator and maintainer
- [Claude](https://claude.ai) - AI contributor

## License

MIT
