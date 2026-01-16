# Quick Start Guide

## 5-Minute Setup

### 1. Create GitHub Repository

```bash
# Create new repo on GitHub called "super-rss-feed"
# Then clone and add files:
git clone https://github.com/YOUR-USERNAME/super-rss-feed.git
cd super-rss-feed

# Copy all files from this package into the repo
```

### 2. Install Dependencies (Local Testing)

```bash
pip install -r requirements.txt
```

### 3. Test Locally

```bash
# Set your API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Run the curator
python super_rss_curator.py feeds.opml

# Check output
cat super-feed.xml
```

### 4. Push to GitHub

```bash
git add .
git commit -m "Initial setup"
git push origin main
```

### 5. Configure GitHub

**Add API Key:**
1. Go to repo Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Claude API key

**Enable GitHub Pages:**
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `/ (root)`
4. Save

### 6. Run First Build

1. Go to Actions tab
2. Click "Generate Super RSS Feed"
3. Click "Run workflow" → "Run workflow"
4. Wait ~2-5 minutes

### 7. Subscribe to Your Feed

Your feed URL will be:
```
https://YOUR-USERNAME.github.io/super-rss-feed/super-feed.xml
```

Add this to Inoreader, Feedly, or your RSS reader.

## Customization

### Adjust Filter Keywords

Edit `super_rss_curator.py`:

```python
BLOCKED_KEYWORDS = [
    # Add your keywords here
    "celebrity", "kardashian", "recipe",
]
```

### Change Source Limits

```python
MAX_PER_SOURCE = 3  # Reduce if feeds too dominant
```

### Tune Scoring Threshold

```python
MIN_CLAUDE_SCORE = 40  # Raise for stricter filtering
```

### Update Your Interests

Find the `interests` string in `score_articles_with_claude()` and customize.

## Troubleshooting

**No articles in feed?**
- Check MIN_CLAUDE_SCORE isn't too high (try 20)
- Verify LOOKBACK_HOURS is reasonable (48+)
- Check Action logs for errors

**Too expensive?**
- Reduce LOOKBACK_HOURS to 24
- Increase MIN_CLAUDE_SCORE to 50
- Reduce number of feeds in OPML

**Action fails?**
- Verify ANTHROPIC_API_KEY is set correctly
- Check API usage limits at console.anthropic.com
- Review Actions logs for specific errors

## Daily Workflow

Once set up:
1. Feed automatically updates daily at 6 AM Pacific
2. Subscribe in your RSS reader
3. Adjust filters/scores as needed
4. Feed stays fresh automatically

That's it! 🎉
