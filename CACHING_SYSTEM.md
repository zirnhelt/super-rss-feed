# Smart Article Caching System

## The Problem
Your original script re-scores all articles every time it runs, even if they were just scored minutes ago. This wastes API credits and time.

**Example today:**
- First run: Scored 320 articles ($0.60)
- Second run: Re-scored same 320 articles ($0.60) 
- **Total waste:** $0.60 + time

## The Solution
The cached version (`super_rss_curator_cached.py`) adds smart caching:

### How It Works:
1. **Saves scores** to `scored_articles_cache.json`
2. **Checks cache first** for each article (6-hour expiry)  
3. **Only scores new articles** or ones older than 6 hours
4. **Updates cache** with fresh scores

### Sample Output:
```
📁 Loaded 245 articles from cache
💡 Cache: 198 hits, 122 new articles to score  
🤖 Scoring 122 new articles with Claude...
💾 Saved cache with 367 articles (removed 23 old entries)
```

### Benefits:
- **Massive API savings:** 198 cache hits = $0.36 saved
- **Faster execution:** No delays for cached articles
- **Automatic cleanup:** Removes articles older than 12 hours
- **Resilient:** Works if cache file is missing/corrupted

## Usage

### Replace Your Current Script:
```bash
# In your repo
cp super_rss_curator_cached.py super_rss_curator_json.py
git add super_rss_curator_json.py
git commit -m "Add smart caching to avoid re-scoring same articles"
git push
```

### Cache File Management:
```bash
# Cache file is auto-generated: scored_articles_cache.json
# You can safely delete it to start fresh
# It auto-expires old entries

# To see cache contents:
jq '.[] | {title, score, scored_at}' scored_articles_cache.json | head -20
```

### Configuration:
```python
CACHE_EXPIRY_HOURS = 6    # Don't re-score for 6 hours
SCORED_CACHE_FILE = 'scored_articles_cache.json'
```

## Expected Results

### First Run (Cold Cache):
```
📁 No cache file found, starting fresh
🤖 Scoring 320 articles with Claude...
💾 Saved cache with 320 articles
```

### Second Run (1 hour later):
```  
📁 Loaded 320 articles from cache
💡 Cache: 315 hits, 5 new articles to score
🤖 Scoring 5 new articles with Claude...
💾 Saved cache with 325 articles
```

### Third Run (Next day):
```
📁 Loaded 325 articles from cache  
💡 Cache: 45 hits, 275 new articles to score
🤖 Scoring 275 new articles with Claude...
💾 Saved cache with 320 articles (removed 280 old entries)
```

## Cost Savings

**Without caching (current):**
- Every run: ~320 articles × $0.002 = $0.64
- 5 runs/day = $3.20/day
- Monthly = ~$96

**With caching:**
- First run: $0.64
- Subsequent runs: ~$0.05 (only new articles)
- 5 runs/day = $0.84/day  
- Monthly = ~$25

**Savings: ~$70/month** 

The cache is especially valuable for:
- Manual testing and fixes
- Multiple runs in a day
- GitHub Actions that might retry on failures
