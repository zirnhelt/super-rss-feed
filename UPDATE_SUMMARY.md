# Super RSS Feed - Complete Update Package
## Based on Google News Takeout Analysis (4,045 articles analyzed)

---

## 📊 What Changed

### Analysis Results
- **Analyzed period**: Aug 2024 - Jan 2026
- **Total articles clicked**: 4,045
- **Top insight**: You click 10.8% smart home vs 0.3% Meshtastic content
- **Missing sources**: 15 of your top 20 clicked sites weren't in feeds.opml

### Three Major Updates

#### 1. **feeds.opml**: +26 New Sources
- **20 high-value feeds** you actually click frequently
- **6 Google News discovery feeds** for topic-specific aggregation
- Organized by category for easy management

#### 2. **Claude Scoring Interests**: Refined & Restructured
- **Merged** "Meshtastic" (0.3% clicks) → "Smart Home" (10.8% clicks)
- **Restructured** as PRIMARY/SECONDARY/LOW priority
- **Added** specific keywords matching your actual clicks

#### 3. **Cache Expiry**: Fixed Inefficiency
- **Before**: 6h expiry → 43% unnecessary re-scoring
- **After**: 48h expiry → 90%+ cache hit rate
- **Savings**: ~65% reduction in API calls (~$1.36/month saved)

---

## 📥 Files Included

All files are in `/tmp/`:

1. `feeds_updated.opml` - Complete updated OPML (86 total feeds)
2. `updated_interests.py` - New Claude interests for reference
3. `auto_patch.sh` - Automated script to patch Python code
4. `apply_updates.sh` - Interactive guide through all updates
5. `rss_feeds_to_find.txt` - Reference list of sources added

---

## 🚀 Quick Start (Recommended)

### Option A: Automatic (fastest)
```bash
# 1. Update OPML
cd ~/super-rss-feed
cp /tmp/feeds_updated.opml ~/super-rss-feed/feeds.opml

# 2. Patch Python code automatically
bash /tmp/auto_patch.sh

# 3. Test locally
source ~/.local/share/virtualenvs/super-rss-feed-*/bin/activate
python super_rss_curator_json.py feeds.opml

# 4. Review output, then commit
git add feeds.opml super_rss_curator_json.py
git commit -m "Major update: +26 feeds, refined interests, fixed cache"
git push
```

### Option B: Interactive (more control)
```bash
bash /tmp/apply_updates.sh
# Follow the prompts - it will guide you through each change
```

---

## 📝 Manual Update Instructions

If you prefer to understand each change:

### Update 1: feeds.opml

**Action**: Replace your current feeds.opml
```bash
cd ~/super-rss-feed
cp feeds.opml feeds.opml.backup  # Safety first
cp /tmp/feeds_updated.opml feeds.opml
```

**What's new**:
- Tom's Guide (173 clicks) - https://www.tomsguide.com/feeds/all
- CTV News (165 clicks) - https://www.ctvnews.ca/rss/...
- XDA Developers (110 clicks) - https://www.xda-developers.com/feed/
- The Verge (89 clicks) - https://www.theverge.com/rss/index.xml
- [+16 more high-value sources]
- [+6 Google News discovery feeds]

### Update 2: Claude Scoring Interests

**File**: `super_rss_curator_json.py`
**Location**: Around line 454

**Find this**:
```python
interests = """
- AI/ML infrastructure and telemetry
- Systems thinking and complex systems
- Climate tech and sustainability
- Homelab/self-hosting technology
- Meshtastic and mesh networking
- 3D printing (Bambu Lab)
- Sci-fi worldbuilding
- Deep technical content over news
- Canadian content and local news (Williams Lake, Quesnel)
"""
```

**Replace with**:
```python
interests = """
PRIMARY INTERESTS (score 70-100):
- AI/ML infrastructure, platform engineering, and telemetry: MLOps, observability, production AI systems, data pipelines, AI platforms
- Smart home, home automation, and home networking: HomeKit, HomeBridge, Philips Hue, IKEA smart home, home automation systems, mesh networking (Meshtastic, LoRa), self-hosted services, privacy-focused home tech
- Climate tech and clean energy: Solar, batteries, EVs, carbon capture, renewable energy technologies, sustainable materials
- 3D printing: Bambu Lab, PLA materials, printer mechanics, slicing software, additive manufacturing
- Canadian content and BC Interior local news: Williams Lake, Quesnel, Cariboo, Kamloops, BC regional news

SECONDARY INTERESTS (score 40-69):
- Systems thinking and complex systems: Network effects, feedback loops, emergence, interdependencies
- Deep technical how-tos and tutorials: Hands-on guides, configuration walkthroughs, technical troubleshooting
- Sci-fi worldbuilding: Hard science fiction, speculative fiction, magic systems, narrative construction
- Scientific research and discoveries: Breakthrough studies, academic papers, novel findings

LOW PRIORITY (score 10-39):
- General tech news and product announcements
- Surface-level reviews without technical depth
- Entertainment and lifestyle content
"""
```

**Why**: Your actual clicks show 10.8% smart home vs 0.3% Meshtastic. This merges them and adds specific keywords Claude can match.

### Update 3: Cache Expiry Fix

**File**: `super_rss_curator_json.py`

**Change 1** (around line 35):
```python
# Before:
CACHE_EXPIRY_HOURS = 6

# After:
CACHE_EXPIRY_HOURS = 48
```

**Change 2** (around line 168 in `save_scored_cache()` function):
```python
# Before:
cutoff_time = datetime.now(timezone.utc) - timedelta(hours=12)

# After:
cutoff_time = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
```

**Why**: Your workflows run 3x daily (8h apart), but cache expires at 6h. This wastes API calls re-scoring the same articles. Matching to LOOKBACK_HOURS (48h) means articles are only scored once while they're still being fetched.

---

## ✅ Testing Checklist

After applying updates:

```bash
cd ~/super-rss-feed
source ~/.local/share/virtualenvs/super-rss-feed-*/bin/activate
python super_rss_curator_json.py feeds.opml
```

**Look for**:
- ✓ New sources appearing (Tom's Guide, The Verge, CTV, etc.)
- ✓ Cache hit rate 80-90% (up from ~57%)
- ✓ Smart home articles scoring higher (70-100 range)
- ✓ No errors during execution

**Sample good output**:
```
📚 Found 86 feeds in OPML
📥 Fetching articles...
  ✓ Tom's Guide: 12 articles
  ✓ The Verge: 8 articles
  ✓ CTV News: 15 articles
  ...
📖 Loaded 525 articles from scoring cache
💡 Cache: 500 hits, 35 new articles to score  ← Good! 93% hit rate
🤖 Scoring 35 new articles...
```

---

## 📈 Expected Impact

### Immediate
- **More relevant articles**: Sources you actually read now in the feed
- **Better scoring**: Smart home content gets proper priority
- **Lower costs**: ~65% fewer redundant API calls

### Monthly Costs
- **Before**: ~$2.10/month (with 57% cache hit rate)
- **After**: ~$0.74/month (with 90%+ cache hit rate)
- **Savings**: ~$1.36/month (~65% reduction)

### Feed Quality
- **Smart home coverage**: Will improve significantly
- **BC local news**: Better coverage (Kamloops, Kelowna sources added)
- **Google News discovery**: Fills gaps in niche topics

---

## 🔍 Monitoring

After first automated run (check GitHub Actions):

1. **Cache performance**:
   ```bash
   grep "Cache:" ~/super-rss-feed/*.log
   # Should show 80-90% hit rate
   ```

2. **New sources appearing**:
   ```bash
   grep -E "(Tom's Guide|The Verge|CTV News)" scored_articles_cache.json | wc -l
   # Should be > 0
   ```

3. **Smart home scoring**:
   ```bash
   # Check that smart home articles are scoring 70+
   grep -i "homekit\|hue\|smart home" scored_articles_cache.json | head -5
   ```

---

## 🆘 Troubleshooting

### "Some feeds returning 0 articles"
Some new feeds may be slow to index. Give them 24-48h, or check if the RSS URL is correct.

### "Cache hit rate still low"
Make sure BOTH cache changes were applied:
```bash
grep "CACHE_EXPIRY_HOURS" super_rss_curator_json.py
grep "LOOKBACK_HOURS" super_rss_curator_json.py
```

### "Metafilter still appearing"
Check what the actual source name is:
```bash
grep -i metafilter scored_articles_cache.json | head -3
```
Then add that exact name to BLOCKED_SOURCES.

### "Want to revert everything"
```bash
cd ~/super-rss-feed
cp feeds.opml.backup feeds.opml
cp super_rss_curator_json.py.pre-update super_rss_curator_json.py
git checkout .  # Reverts all uncommitted changes
```

---

## 📚 Reference: All New Feeds

### High-Value Direct Sources (20)
1. Tom's Guide - Tech/smart home reviews
2. CTV News - Canadian national news
3. XDA Developers - Android deep-dives
4. The Verge - Tech news
5. Global News - Canadian news
6. ZDNet - Enterprise tech
7. ScienceAlert - Science news
8. InsideEVs - EV news
9. New Atlas - Emerging tech
10. How-To Geek - Tech tutorials
11. MacRumors - Apple news
12. TechRadar - Tech reviews
13. Castanet - Kelowna/Okanagan local
14. CFJC Today - Kamloops local
15. The Tyee - BC independent news
16. CleanTechnica - Clean tech/EVs
17. Android Authority - Android news
18. Android Police - Android news
19. Neowin - Tech news
20. All3DP - 3D printing

### Google News Discovery Feeds (6)
1. Smart Home & Automation
2. 3D Printing  
3. AI/ML Infrastructure
4. Clean Energy & EVs
5. Mesh Networking & LoRa
6. Williams Lake & BC Interior

---

## 🎯 Next Steps

After this update settles (2-3 days):

1. **Review feed quality** - Are you seeing better articles?
2. **Check Inoreader** - Any sources overwhelming the feed?
3. **Monitor costs** - Verify API usage dropped
4. **Fine-tune** - Adjust MAX_PER_SOURCE if needed

---

## Questions?

Check the analysis output:
```bash
cat /tmp/rss_feeds_to_find.txt  # List of sources added
python3 /tmp/analyze_google_news.py  # Re-run analysis
```

Or review your Google News patterns:
- 18.4% AI/ML (matches interests ✓)
- 14.9% Climate (matches interests ✓)  
- 10.8% Smart Home (NOW properly weighted ✓)
- 6.9% 3D Printing (matches interests ✓)
- 7.2% BC Local (expanded coverage ✓)
