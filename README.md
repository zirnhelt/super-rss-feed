# Super RSS Feed

**TL;DR:** An AI-powered RSS curation system that processes ~300 articles daily from 50+ sources, scores them with Claude’s API, and outputs categorized feeds to combat information overload.

## What It Does

This system solves two problems:

1. **Information diet stagnation** — you keep reading the same sources without discovering new perspectives
1. **RSS reader limitations** — Inoreader’s free tier shows only 20 articles per feed, hiding most content

Instead of a single monolithic feed, it outputs 9 categorized feeds with AI-scored articles:

- **Best Of** — Top-scored articles across all categories
- **Local News** — Williams Lake/Quesnel BC community news (auto-prioritized)
- **AI & Tech** — AI/ML, infrastructure, telemetry, systems
- **Climate & Energy** — Climate tech, energy systems, environmental news
- **Homelab & DIY** — Self-hosting, home automation, networking
- **Mesh Networks** — Meshtastic, LoRa, distributed systems
- **General News** — Politics, society, global affairs
- **Science** — Research, discoveries, technical deep-dives
- **Sci-Fi & Culture** — Worldbuilding, speculative fiction, media

## How It Works

**Pipeline:**

1. Parse OPML → Fetch RSS feeds → Deduplicate (URL hash + fuzzy title matching)
1. Filter blocked keywords → Score with Claude API (prompt caching enabled)
1. Apply source diversity limits → Categorize articles → Generate feeds
1. Scrape images for high-scoring articles → Output JSON feeds + index.html

**Special Handling:**

- Williams Lake Tribune content scraped separately, injected at max priority with 📍 indicators
- Aggregator sources (Metafilter, HN, Reddit) filtered to avoid duplicates with original sources
- Prompt caching reduces API costs by ~90% by caching static scoring instructions
- Smart deduplication catches semantic duplicates with different titles

**Automation:**

- Runs daily at 5-6 AM Pacific via GitHub Actions
- Outputs ~250 curated articles from 300+ processed
- Hosted on GitHub Pages for static serving

## Using the Feeds

Subscribe in Inoreader (or any RSS reader):

```
Best Of:        https://zirnhelt.github.io/super-rss-feed/feed-best-of.json
Local News:     https://zirnhelt.github.io/super-rss-feed/feed-local.json
AI & Tech:      https://zirnhelt.github.io/super-rss-feed/feed-ai-tech.json
Climate:        https://zirnhelt.github.io/super-rss-feed/feed-climate.json
Homelab:        https://zirnhelt.github.io/super-rss-feed/feed-homelab.json
Mesh Networks:  https://zirnhelt.github.io/super-rss-feed/feed-mesh.json
General News:   https://zirnhelt.github.io/super-rss-feed/feed-news.json
Science:        https://zirnhelt.github.io/super-rss-feed/feed-science.json
Sci-Fi:         https://zirnhelt.github.io/super-rss-feed/feed-scifi.json
```

Or browse the web interface: https://zirnhelt.github.io/super-rss-feed/

## Technical Details

**Stack:**

- Python (feedparser, anthropic, BeautifulSoup4, Pillow)
- Claude Sonnet 4.5 API with prompt caching
- GitHub Actions for automation
- GitHub Pages for hosting

**Key Features:**

- Deduplication via URL hashing + fuzzy title matching (80% similarity threshold)
- Source diversity: max 5 articles per source (adjustable)
- Image scraping: limited to high-scoring articles to respect rate limits
- Graceful degradation: continues processing if individual feeds fail
- Local content priority: Tribune articles bypass normal scoring, always max priority

**Rate Limiting:**

- Conservative per-source limits to avoid tracking pixels
- Prompt caching dramatically reduces API calls/costs
- Smart caching of static scoring instructions in system prompts

## Configuration

Edit `curated-feeds.opml` to add/remove sources. The system auto-detects categories based on feed metadata and content.

Williams Lake Tribune scraper handles Black Press Media subscription access separately.

## Future Ideas

- AI-powered feed discovery to auto-identify new sources
- Newsletter generation from curated feeds
- Integration with Inoreader’s API for read-state tracking
- More aggressive deduplication (lower similarity threshold)

## License

GPL-3.0

-----

Built to escape information diet stagnation and make better use of RSS readers’ limitations. Deployed from Horsefly, BC.
