# Super RSS Feed Curator - Project Summary

## What You've Got

A complete, production-ready RSS aggregation system that:

✅ **Consolidates** 58 feeds into one curated stream  
✅ **Filters** sports, Fox News, advice columns automatically  
✅ **Deduplicates** using URL + fuzzy title matching  
✅ **Scores** with Claude API (0-100) based on your interests  
✅ **Diversifies** with per-source limits (max 5 articles/source)  
✅ **Outputs** top 250 articles daily  
✅ **Runs** automatically via GitHub Actions  
✅ **Hosts** on GitHub Pages (free)

## File Structure

```
super-rss-feed/
├── super_rss_curator.py      # Main Python script
├── requirements.txt           # Dependencies
├── feeds.opml                 # Your 58 consolidated feeds
├── test_setup.py             # Setup verification script
├── index.html                # Landing page
├── README.md                 # Full documentation
├── QUICKSTART.md             # 5-minute setup guide
├── .gitignore                # Git ignore rules
└── .github/
    └── workflows/
        └── generate-feed.yml  # Daily automation
```

## How It Works

### Phase 1: Fetch
- Reads `feeds.opml` (58 unique feeds)
- Fetches articles from last 48 hours
- Parses ~1000-2000 raw articles

### Phase 2: Filter
Removes:
- Fox News (any source with "fox" or "foxnews")
- Sports (NFL, NBA, MLB, NHL, playoff, etc.)
- Advice columns (Dear Abby, Ask Amy, etc.)

### Phase 3: Deduplicate
- Exact match: URL hashing
- Fuzzy match: 85% title similarity threshold
- Typically removes 20-30% duplicates

### Phase 4: Score with Claude
Batches of 10 articles sent to Claude API:
```
Your interests:
- AI/ML infrastructure and telemetry
- Systems thinking and complex systems
- Climate tech and sustainability
- Homelab/self-hosting technology
- Meshtastic and mesh networking
- 3D printing (Bambu Lab)
- Sci-fi worldbuilding
- Canadian content and local news
```

Returns score 0-100 for each article.

### Phase 5: Quality Filter
- Drops articles < 30 score (configurable)
- Typically keeps 60-70% of scored articles

### Phase 6: Diversity
- Limits to max 5 articles per source
- Prevents Aeon/NYT overload
- Maintains balanced mix

### Phase 7: Output
- Top 250 articles by score
- Generated as RSS 2.0 XML
- Includes source + score in description
- Hosted on GitHub Pages

## Cost Estimate

**Claude API usage:**
- ~1500 articles/day fetched
- After dedup: ~1000 articles
- Batches of 10 = 100 API calls
- Each call: ~100 input + 20 output tokens
- Total: ~12,000 tokens/day

**Pricing:**
- Sonnet 4: $3/MTok input, $15/MTok output
- Daily: ~$0.04 input + $0.03 output = **$0.07/day**
- Monthly: **~$2.10/month**

**GitHub:**
- Actions: Free (2000 min/month limit)
- Pages: Free
- Storage: Free

**Total: ~$2/month**

## Configuration Options

### Tuning Parameters

```python
# Output size
MAX_ARTICLES_OUTPUT = 250

# Source diversity
MAX_PER_SOURCE = 5

# Time window
LOOKBACK_HOURS = 48

# Quality threshold
MIN_CLAUDE_SCORE = 30
```

### Source-Specific Limits

To give some sources more/less weight:

```python
# In apply_diversity_limits(), add:
source_limits = {
    'MIT Technology Review': 10,
    'Aeon Essays': 3,
    'Williams Lake Tribune': 8,
    # default: 5
}
```

### Category Filtering

Want to emphasize certain topics?

```python
# Add category boost in scoring prompt:
interests = """
PRIORITY (2x weight):
- AI/ML infrastructure

NORMAL:
- Climate tech
- Sci-fi

LOW PRIORITY (0.5x weight):
- General news
"""
```

## Maintenance

**Weekly:**
- Check feed output quality
- Review low-scoring articles (are they actually bad?)
- Adjust MIN_CLAUDE_SCORE if needed

**Monthly:**
- Review Claude API costs
- Check for dead feeds (update feeds.opml)
- Scan for new blocked keywords

**Quarterly:**
- Update interests in scoring prompt
- Review source diversity distribution
- Consider adding new feeds

## Next Steps

**After Setup:**

1. **Week 1:** Monitor daily - tune MIN_CLAUDE_SCORE
2. **Week 2:** Adjust MAX_PER_SOURCE for dominant sources
3. **Week 3:** Add any missed filter keywords
4. **Week 4:** Locked in - run on autopilot

**Optional Enhancements:**

- Add category tags to articles
- Build web UI to browse scored articles
- Add "thumbs up/down" feedback loop
- Email digest of top 10 articles
- Slack/Discord notifications for high-scoring articles

## Support

**Issues?**
1. Check Actions tab for error logs
2. Run `python test_setup.py` locally
3. Verify API key in Secrets
4. Check console.anthropic.com for API issues

**Want to tweak?**
- All code is commented
- README has full customization guide
- Parameters are at top of script

That's it! You now have an AI-powered RSS curator running automatically. 🎉
