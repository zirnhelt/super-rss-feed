# Super RSS Feed - Roadmap

## Current State
- 3x daily runs (6 AM, 2 PM, 10 PM Pacific) via GitHub Actions
- 50+ feeds via OPML, Williams Lake Tribune scraping
- AI scoring via Claude API (~$0.10-0.15/day with prompt caching)
- 7 category feeds: local, ai-tech, climate, homelab, science, scifi, news
- Cumulative feed management with 3-day retention

## Working Well
- Categorization with explicit rules (fixed Jan 27)
- Sports/advice column filtering
- Image scraping with OpenGraph + favicon fallback
- Cost optimization via prompt caching
- Williams Lake Tribune priority scoring (📍 emoji, score 80+)
- Deduplication via URL hash + fuzzy title matching

## Short-term
- [x] Clean up stale backup and fix scripts from root directory
- [x] Stronger deduplication logic for near-duplicate articles
- [x] Improved sports filtering for local content (rec centres, arenas)
- [ ] Categorization accuracy refinement based on reading patterns

## Medium-term
- [x] AI-powered feed discovery runs weekly, scores candidates against the live
      `config/scoring_interests.txt` (so it evolves alongside the podcast's tuning),
      auto-adds high-confidence feeds (75+) to `feeds.opml`, and notifies via an
      auto-merged PR summarizing what changed
- [ ] Better cache health monitoring - alerts when caches go stale or corrupt
- [ ] Feed blocking workarounds for sites that reject User-Agent headers

## Long-term / Speculative
- [ ] Reading pattern feedback loop - user engagement data feeds back into scoring
- [ ] Cross-project: shared interest/scoring config between RSS and Podcast systems
