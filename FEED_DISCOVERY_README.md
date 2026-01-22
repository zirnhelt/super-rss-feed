# Feed Discovery System

Automated system to discover and recommend new RSS feeds based on your interests using AI scoring.

## How It Works

1. **Fetches** curated OPML files from high-quality sources (AI/ML, tech, climate, etc.)
2. **Filters** out feeds you already have 
3. **Samples** recent articles from candidate feeds
4. **Scores** feeds using your existing Claude API interests profile
5. **Recommends** feeds above threshold (default: 60+ score)
6. **Caches** results for a month to minimize API costs

## Quick Start

### Manual Discovery
```bash
# Run discovery (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY='your-key-here'
python feed_discovery.py

# Review recommendations
cat feed_discovery_report.json | jq '.summary.top_recommendations'

# Add feeds interactively 
python integrate_discoveries.py

# Or auto-add high-scoring feeds
python integrate_discoveries.py --auto-add-threshold 75
```

### Automated Weekly Discovery

The system runs automatically every Sunday via GitHub Actions and creates a PR with results.

1. Enable the workflow in `.github/workflows/discover-feeds.yml`
2. Ensure `ANTHROPIC_API_KEY` secret is set in repo
3. Review weekly PRs with discovery reports
4. Manually integrate promising feeds using the integration script

## Discovery Sources

Current curated OPML sources:
- **AI/ML**: ~250 feeds from awesome_ML_AI_RSS_feed
- **Tech & Startups**: ~500 feeds covering startups, science, tech
- **RSS Renaissance**: Additional AI-focused feeds
- **Plenary**: General recommended feeds + international news

## Output Files

- `feed_discovery_report.json` - Full recommendations with scores
- `discovery_cache.json` - Cache to avoid re-scoring feeds
- GitHub Actions artifact with both files

## Report Structure

```json
{
  "total_candidates_evaluated": 150,
  "recommended_feeds": 12,
  "min_score_threshold": 60,
  "categories": {
    "ai_ml": {
      "count": 5,
      "feeds": [{
        "title": "MIT AI Lab",
        "url": "https://example.com/feed.xml",
        "average_score": 78.5,
        "sample_articles": 3,
        "reason": "Strong alignment with your interests"
      }]
    }
  },
  "summary": {
    "top_recommendations": [...] // Top 10 feeds
  }
}
```

## Integration Options

### Interactive Mode (Default)
```bash
python integrate_discoveries.py
```
- Shows each recommended feed
- Lets you decide y/n for each
- Adds selections to OPML under "Discovered Feeds"

### Auto-Add Mode  
```bash
python integrate_discoveries.py --auto-add-threshold 80
```
- Automatically adds feeds scoring 80+
- Good for high-confidence discoveries
- Still creates separate category for review

### Dry Run
```bash
python integrate_discoveries.py --dry-run
```
- Shows what would be added without changes
- Good for reviewing before committing

## Customization

### Add More Discovery Sources
Edit `DISCOVERY_SOURCES` in `feed_discovery.py`:

```python
DISCOVERY_SOURCES.append({
    'name': 'Climate Tech Feeds',
    'url': 'https://example.com/climate-feeds.opml',
    'category': 'climate'
})
```

### Adjust Scoring Threshold
```python
MIN_FEED_SCORE = 70  # Raise for higher quality filter
```

### Change Sampling
```python
MAX_ARTICLES_PER_FEED = 5  # Sample more articles per feed
```

## Caching

- Feeds are re-evaluated monthly (configurable)
- Cache stored in `discovery_cache.json`
- Delete cache file to force fresh evaluation of all feeds
- Cache includes scores, article counts, and error states
- Monthly caching dramatically reduces API costs

## Troubleshooting

### No recommendations found
- Check if threshold is too high (try lowering `MIN_FEED_SCORE`)
- Verify OPML sources are accessible
- Check for existing feeds already in your OPML

### API errors
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check Claude API usage/rate limits
- Large batches might need rate limiting

### OPML parsing errors
- Some sources may have malformed OPML
- Check `discovery_cache.json` for specific errors
- Script continues with other sources if one fails

## Cost Estimation

**Per discovery run:**
- ~100-200 candidate feeds
- ~3 articles per feed = 300-600 articles to score  
- ~30-60 Claude API calls (10 articles per call)
- **Cost: ~$0.10-0.20 per discovery run**

**Weekly automation: ~$0.50/month**

Much cheaper than your main curation since it's only sampling articles, and monthly caching means most weeks hit the cache instead of re-scoring.
