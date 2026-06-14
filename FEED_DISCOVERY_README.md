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

The system runs automatically every Sunday via GitHub Actions:

1. `feed_discovery.py` evaluates new candidates and refreshes the report/cache
2. `integrate_discoveries.py --auto-add-threshold 75` adds any high-confidence
   feeds (score 75+) directly to `feeds.opml` — no manual integration step
3. The run is committed via a PR that's **auto-merged immediately**; the PR
   description is your notification of what changed (which feeds were added,
   with scores/categories/URLs, or a note that nothing cleared the bar)
4. Anything that didn't clear the auto-add bar but scored 60+ stays in
   `feed_discovery_report.json` for manual review/integration if you want it

No action is required to keep the OPML current — just skim the merged PRs (or
`feed_discovery_report.json`) to see what showed up and prune anything that
doesn't earn its keep from `feeds.opml`.

Setup: ensure `ANTHROPIC_API_KEY` (and optionally `COHERE_API_KEY` /
`BRAVE_API_KEY`) secrets are set in the repo.

### Manual Catch-Up Runs

High-volume sources (currently Kagi Small Web) are gated to
`max_new_candidates_per_run` (default 25, see `config/source_preferences.json`)
new candidates per run, so the cache only advances ~25 entries/week. To work
through a backlog faster, trigger the workflow manually
(`workflow_dispatch`) with the `max_candidates` input set to a larger number
(e.g. 200). This overrides the cap for that single run only — scheduled runs
keep using the config default. It's safe to run with a much larger batch: the
free prescore keyword filter rejects most off-topic feeds without an API
call, so the extra cost is mostly just feed-fetch time.

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

The weekly workflow already runs `--auto-add-threshold 75` for you (see above).
These modes are for catching the 60-74 range manually, or for ad hoc runs.

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
- Pass `--summary-file path.md` to also write a markdown summary of what was
  added (or a "nothing qualified" note) — this is what feeds the auto-merged
  weekly PR's notification body

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
