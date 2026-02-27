#!/usr/bin/env python3
"""Parse feed generation output and maintain FEED_LOG.md and TODO.md.

Usage:
  python log_feed_results.py <feed_output_file>
  python log_feed_results.py -           # read from stdin
  python log_feed_results.py feed.txt --slot morning --date 2026-02-24

Appends a structured entry to FEED_LOG.md grouped by date and run slot
(morning/afternoon/evening). Entries older than RETENTION_DAYS are compressed
into weekly summaries. Regenerates the auto section of TODO.md.
"""

import sys
import re
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict
try:
    from zoneinfo import ZoneInfo
    _PACIFIC = ZoneInfo("America/Los_Angeles")
except ImportError:
    _PACIFIC = None


def _to_pacific(utc_dt: datetime) -> datetime:
    """Convert a UTC datetime to Pacific time (PST/PDT), for log date display."""
    if _PACIFIC:
        return utc_dt.astimezone(_PACIFIC)
    # Fallback: approximate with UTC-8 (PST); acceptable ±1 h error during PDT
    return utc_dt + timedelta(hours=-8)

LOG_FILE = Path('FEED_LOG.md')
TODO_FILE = Path('TODO.md')
RETENTION_DAYS = 7

# GitHub Actions cron schedule -> Pacific slots (UTC hours)
# 0 14 * * *  = 6:00 AM Pacific  (14 UTC)
# 0 22 * * *  = 2:00 PM Pacific  (22 UTC)
# 0 6  * * *  = 10:00 PM Pacific (06 UTC)
SLOT_BY_UTC_HOUR = {14: 'morning', 22: 'afternoon', 6: 'evening'}
SLOT_EMOJIS  = {'morning': '🌅', 'afternoon': '🌞', 'evening': '🌙'}
SLOT_LABELS  = {'morning': '6 AM Pacific', 'afternoon': '2 PM Pacific', 'evening': '10 PM Pacific'}
CATEGORY_ORDER = ['local', 'ai-tech', 'climate', 'homelab', 'science', 'scifi', 'news']

AUTO_START = '<!-- AUTO:START -->'
AUTO_END   = '<!-- AUTO:END -->'


# ---------------------------------------------------------------------------
# Slot detection
# ---------------------------------------------------------------------------

def detect_slot() -> str:
    """Infer run slot from current UTC hour (±1 hour tolerance)."""
    hour = datetime.now(timezone.utc).hour
    for target, slot in SLOT_BY_UTC_HOUR.items():
        if (hour - target) % 24 <= 1 or (target - hour) % 24 <= 1:
            return slot
    # Rough fallback
    if 10 <= hour < 18:
        return 'morning'
    if 18 <= hour <= 23:
        return 'afternoon'
    return 'evening'


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

def parse_output(text: str) -> dict:
    """Extract metrics from super_rss_curator_json.py stdout."""
    m = {
        'articles_fetched': None,
        'after_dedup':      None,
        'new_articles':     None,
        'after_scoring':    None,
        'categories':       {},
        'feed_sizes':       {},
        'failed_feeds':     [],  # list of {feed, error}
        'errors':           [],
        'warnings':         [],
        'images_found':     None,
        'images_total':     None,
    }

    # Patterns that indicate low-signal cache housekeeping (skip from warnings)
    SKIP_WARN = ('cleaned', 'cache updated', 'podcast cache', 'wlt cache', 'scored cache')

    for line in text.splitlines():
        s = line.strip()

        def grab(pattern, cast=int):
            hit = re.search(pattern, line)
            return cast(hit.group(1)) if hit else None

        if m['articles_fetched'] is None:
            m['articles_fetched'] = grab(r'Articles fetched:\s*(\d+)')

        if m['after_dedup'] is None:
            m['after_dedup'] = grab(r'After dedup:\s*(\d+)')

        # "🆕 New articles (not previously shown): 180 → 42"
        if m['new_articles'] is None:
            hit = re.search(r'New articles.*?:\s*\d+\s*→\s*(\d+)', line)
            if hit:
                m['new_articles'] = int(hit.group(1))

        if m['after_scoring'] is None:
            m['after_scoring'] = grab(r'After scoring:\s*(\d+)')

        # Category breakdown: "  ai-tech: 12 articles"
        hit = re.match(r'\s+(local|ai-tech|climate|homelab|news|science|scifi):\s+(\d+)', line)
        if hit:
            m['categories'][hit.group(1)] = int(hit.group(2))

        # Generated feed size: "✅ Generated ai-tech feed: 45 articles"
        hit = re.search(r'Generated ([\w-]+) feed:\s*(\d+) articles', line)
        if hit:
            m['feed_sizes'][hit.group(1)] = int(hit.group(2))

        # Failed feed: "  ✗ CFJC Today Kamloops: <error>"
        hit = re.search(r'✗\s+(.+?):\s+(.+)', s)
        if hit:
            m['failed_feeds'].append({
                'feed':  hit.group(1).strip(),
                'error': hit.group(2).strip()[:120],
            })

        # Image stats: "Found images for 38/42 articles"
        hit = re.search(r'Found images for (\d+)/(\d+)', line)
        if hit:
            m['images_found'] = int(hit.group(1))
            m['images_total'] = int(hit.group(2))

        # Errors and warnings
        if '❌' in s and s:
            m['errors'].append(s)
        elif '⚠️' in s and s:
            if not any(p in s.lower() for p in SKIP_WARN):
                m['warnings'].append(s)

    return m


# ---------------------------------------------------------------------------
# Run section formatter
# ---------------------------------------------------------------------------

def format_run_section(slot: str, metrics: dict) -> str:
    emoji = SLOT_EMOJIS.get(slot, '🕐')
    label = SLOT_LABELS.get(slot, slot)
    lines = [f'#### {emoji} {label}']

    # Pipeline summary
    pipe = []
    if metrics['articles_fetched'] is not None:
        pipe.append(f"Fetched **{metrics['articles_fetched']}**")
    if metrics['after_dedup'] is not None:
        pipe.append(f"→ dedup **{metrics['after_dedup']}**")
    if metrics['new_articles'] is not None:
        pipe.append(f"→ new **{metrics['new_articles']}**")
    if metrics['after_scoring'] is not None:
        pipe.append(f"→ quality **{metrics['after_scoring']}**")
    if pipe:
        lines.append('- ' + ' '.join(pipe))

    # Category mix
    cats = metrics['categories']
    if cats:
        total = sum(cats.values()) or 1
        parts = []
        for cat in CATEGORY_ORDER:
            n = cats.get(cat, 0)
            if n:
                parts.append(f'{cat}:{n}({round(100*n/total)}%)')
        lines.append('- Mix: ' + ', '.join(parts))

    # Feed output sizes
    sizes = metrics['feed_sizes']
    if sizes:
        parts = [f'{c}:{sizes[c]}' for c in CATEGORY_ORDER if c in sizes]
        lines.append('- Feeds: ' + ', '.join(parts))

    # Images
    if metrics['images_found'] is not None:
        lines.append(f'- Images: {metrics["images_found"]}/{metrics["images_total"]}')

    # Failed feeds
    for f in metrics['failed_feeds']:
        lines.append(f'- ⚠️ **{f["feed"]}** failed — `{f["error"]}`')

    # Hard errors
    for e in metrics['errors']:
        lines.append(f'- ❌ {e}')

    # Warnings (cap at 5)
    for w in metrics['warnings'][:5]:
        lines.append(f'- ⚠️ {w}')

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# FEED_LOG.md management
# ---------------------------------------------------------------------------

LOG_HEADER = (
    '# Feed Generation Log\n\n'
    '_Auto-updated 3× daily (6 AM / 2 PM / 10 PM Pacific). '
    'Full detail kept for the last 7 days; older entries are compressed to weekly summaries._\n\n'
    '---\n\n'
)


def day_label(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d (%A)')


def parse_log_sections(content: str) -> list:
    """Split FEED_LOG.md into section dicts: {type, key, lines}."""
    sections = []
    lines = content.splitlines(keepends=True)
    cur = {'type': 'preamble', 'key': '', 'lines': []}

    for line in lines:
        m_day = re.match(r'^## (\d{4}-\d{2}-\d{2} \(\w+\))\s*$', line)
        m_wk  = re.match(r'^## (Week of \d{4}-\d{2}-\d{2}[^\n]*)\s*$', line)
        if m_day:
            if cur['lines']:
                sections.append(cur)
            cur = {'type': 'day', 'key': m_day.group(1), 'lines': [line]}
        elif m_wk:
            if cur['lines']:
                sections.append(cur)
            cur = {'type': 'week', 'key': m_wk.group(1), 'lines': [line]}
        else:
            cur['lines'].append(line)

    if cur['lines']:
        sections.append(cur)
    return sections


def reassemble_log(sections: list) -> str:
    out = []
    for sec in sections:
        text = ''.join(sec['lines'])
        out.append(text.rstrip('\n'))
        if sec['type'] in ('day', 'week'):
            out.append('\n\n---\n')
        out.append('\n')
    return '\n'.join(out)


def compress_to_week(day_sections: list) -> dict | None:
    """Turn a list of day sections into one weekly summary section."""
    if not day_sections:
        return None

    dates = []
    for sec in day_sections:
        hit = re.match(r'(\d{4}-\d{2}-\d{2})', sec['key'])
        if hit:
            try:
                dates.append(datetime.strptime(hit.group(1), '%Y-%m-%d'))
            except ValueError:
                pass
    if not dates:
        return None

    week_start = min(dates).strftime('%Y-%m-%d')
    week_end   = max(dates).strftime('%Y-%m-%d')

    total_runs      = 0
    fetched_vals    = []
    quality_vals    = []
    all_issues      = []
    cat_totals      = defaultdict(int)

    for sec in day_sections:
        text = ''.join(sec['lines'])
        total_runs += len(re.findall(r'^####', text, re.MULTILINE))
        for hm in re.finditer(r'Fetched \*\*(\d+)\*\*', text):
            fetched_vals.append(int(hm.group(1)))
        for qm in re.finditer(r'quality \*\*(\d+)\*\*', text):
            quality_vals.append(int(qm.group(1)))
        for cm in re.finditer(r'(local|ai-tech|climate|homelab|news|science|scifi):(\d+)\(', text):
            cat_totals[cm.group(1)] += int(cm.group(2))
        for ln in text.splitlines():
            if '❌' in ln or ('⚠️' in ln and 'failed' in ln.lower()):
                all_issues.append(re.sub(r'[*`]', '', ln.strip()))

    avg_f = round(sum(fetched_vals) / len(fetched_vals)) if fetched_vals else 0
    avg_q = round(sum(quality_vals) / len(quality_vals)) if quality_vals else 0

    summary_lines = [f'## Week of {week_start}–{week_end}\n']
    summary_lines.append(f'- {total_runs} runs · avg fetched {avg_f} · avg quality {avg_q}\n')

    if cat_totals:
        total = sum(cat_totals.values()) or 1
        dominant = max(cat_totals, key=cat_totals.get)
        summary_lines.append(
            f'- Dominant: **{dominant}** ({round(100*cat_totals[dominant]/total)}%) '
            + ' / '.join(f'{c}:{cat_totals[c]}' for c in CATEGORY_ORDER if cat_totals[c])
            + '\n'
        )

    seen = set()
    for issue in all_issues:
        clean = issue[:120]
        if clean not in seen:
            seen.add(clean)
            summary_lines.append(f'- {clean}\n')

    return {'type': 'week', 'key': f'Week of {week_start}–{week_end}', 'lines': summary_lines}


def update_feed_log(slot: str, metrics: dict, run_time: datetime):
    content = LOG_FILE.read_text('utf-8') if LOG_FILE.exists() else LOG_HEADER
    sections = parse_log_sections(content)

    # Use Pacific local time for date labels so the evening slot (fires at
    # 06:00 UTC the next calendar day) appears under the correct Pacific date.
    pac_time    = _to_pacific(run_time)
    today_str   = pac_time.strftime('%Y-%m-%d')
    today_label = day_label(pac_time)
    cutoff_str  = (pac_time - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')

    run_text = format_run_section(slot, metrics)

    # Find or create today's day section
    today_sec = next((s for s in sections if s['type'] == 'day' and s['key'].startswith(today_str)), None)

    slot_marker = f'#### {SLOT_EMOJIS.get(slot, "")}'
    if today_sec:
        existing_text = ''.join(today_sec['lines'])
        if slot_marker not in existing_text:
            today_sec['lines'].append('\n' + run_text)
        # else: slot already recorded this day, skip to avoid duplicates
    else:
        new_sec = {
            'type': 'day',
            'key':  today_label,
            'lines': [f'## {today_label}\n', '\n', run_text],
        }
        # Insert right after preamble (index 0 or 1)
        insert_at = next((i + 1 for i, s in enumerate(sections) if s['type'] == 'preamble'), 0)
        sections.insert(insert_at, new_sec)

    # Identify day sections old enough to compress
    old_days  = [s for s in sections if s['type'] == 'day'
                 and re.match(r'(\d{4}-\d{2}-\d{2})', s['key'])
                 and re.match(r'(\d{4}-\d{2}-\d{2})', s['key']).group(1) < cutoff_str]
    keep      = [s for s in sections if s not in old_days]

    if old_days:
        # Group by ISO week number
        by_week = defaultdict(list)
        for sec in old_days:
            dt = datetime.strptime(re.match(r'(\d{4}-\d{2}-\d{2})', sec['key']).group(1), '%Y-%m-%d')
            by_week[dt.strftime('%G-W%V')].append(sec)

        existing_week_keys = {s['key'] for s in keep if s['type'] == 'week'}
        for _, days in sorted(by_week.items()):
            compressed = compress_to_week(days)
            if compressed and compressed['key'] not in existing_week_keys:
                keep.append(compressed)

    LOG_FILE.write_text(reassemble_log(keep), 'utf-8')


# ---------------------------------------------------------------------------
# TODO.md management
# ---------------------------------------------------------------------------

def extract_recent_entries() -> list:
    """Pull (date, slot, metrics_dict) tuples from the last RETENTION_DAYS in FEED_LOG.md."""
    if not LOG_FILE.exists():
        return []

    content    = LOG_FILE.read_text('utf-8')
    cutoff     = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    results    = []

    for m_day in re.finditer(
        r'^## (\d{4}-\d{2}-\d{2}[^\n]*)\n(.*?)(?=^## |\Z)',
        content, re.MULTILINE | re.DOTALL
    ):
        date_key = re.match(r'\d{4}-\d{2}-\d{2}', m_day.group(1))
        if not date_key or date_key.group() < cutoff:
            continue
        day_date    = date_key.group()
        day_content = m_day.group(2)

        emoji_inv = {v: k for k, v in SLOT_EMOJIS.items()}

        for m_run in re.finditer(
            r'^#### ([🌅🌞🌙🕐])\s+.+?\n(.*?)(?=^####|\Z)',
            day_content, re.MULTILINE | re.DOTALL
        ):
            slot        = emoji_inv.get(m_run.group(1), 'unknown')
            run_content = m_run.group(2)

            metrics = {
                'after_scoring': None,
                'categories':    {},
                'failed_feeds':  [],
                'errors':        [],
                'warnings':      [],
            }

            qm = re.search(r'quality \*\*(\d+)\*\*', run_content)
            if qm:
                metrics['after_scoring'] = int(qm.group(1))

            for cm in re.finditer(r'(local|ai-tech|climate|homelab|news|science|scifi):(\d+)\(', run_content):
                metrics['categories'][cm.group(1)] = int(cm.group(2))

            for em in re.finditer(r'❌ (.+)', run_content):
                metrics['errors'].append(em.group(1).strip())

            for fm in re.finditer(r'⚠️ \*\*(.+?)\*\* failed — `(.+?)`', run_content):
                metrics['failed_feeds'].append({'feed': fm.group(1), 'error': fm.group(2)})

            results.append((day_date, slot, metrics))

    return results[-21:]  # cap at 7 days × 3 runs


def build_auto_section(entries: list) -> str:
    lines = [AUTO_START + '\n']

    # --- Errors table ---
    error_rows = []
    for date, slot, m in entries:
        label = SLOT_LABELS.get(slot, slot)
        for f in m['failed_feeds']:
            error_rows.append(f'| {date} | {SLOT_EMOJIS.get(slot,"")} {label} | ⚠️ **{f["feed"]}** failed | `{f["error"]}` |')
        for e in m['errors']:
            clean = re.sub(r'[❌⚠️]', '', e).strip()
            error_rows.append(f'| {date} | {SLOT_EMOJIS.get(slot,"")} {label} | ❌ Error | {clean[:100]} |')

    lines.append('## Feed Errors — Last 7 Days\n\n')
    if error_rows:
        lines.append('| Date | Slot | Issue | Detail |\n')
        lines.append('|------|------|-------|--------|\n')
        for row in error_rows:
            lines.append(row + '\n')
    else:
        lines.append('_No errors recorded in the last 7 days._\n')

    # --- Content mix table ---
    lines.append('\n## Content Mix — Last 7 Days\n\n')
    if entries:
        lines.append('| Date | Slot | Quality | Mix (top 3) |\n')
        lines.append('|------|------|---------|-------------|\n')
        for date, slot, m in entries:
            quality  = m['after_scoring'] if m['after_scoring'] is not None else '–'
            cats     = m['categories']
            total    = sum(cats.values()) or 1
            top3     = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
            mix_str  = ', '.join(f'{c}:{n}({round(100*n/total)}%)' for c, n in top3) if top3 else '–'
            lines.append(f'| {date} | {SLOT_EMOJIS.get(slot,"")} {slot} | {quality} | {mix_str} |\n')
    else:
        lines.append('_No data yet — will populate after the first logged run._\n')

    lines.append(f'\n_Last updated by log\\_feed\\_results.py · {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}_\n\n')
    lines.append(AUTO_END + '\n')
    return ''.join(lines)


def update_todo(entries: list):
    auto = build_auto_section(entries)

    if TODO_FILE.exists():
        existing = TODO_FILE.read_text('utf-8')
        if AUTO_START in existing and AUTO_END in existing:
            before = existing[:existing.index(AUTO_START)]
            after  = existing[existing.index(AUTO_END) + len(AUTO_END):]
            content = before + auto + after
        else:
            content = auto + '\n' + existing
    else:
        content = (
            '# Feed Issues & Review\n\n'
            '_The AUTO section below is regenerated on every run. '
            'Add your own notes in the **Notes & Review** section — it is never overwritten._\n\n'
            + auto +
            '\n## Notes & Review\n\n'
            '_Add observations and action items here._\n'
        )

    TODO_FILE.write_text(content, 'utf-8')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Log feed generation results to FEED_LOG.md and TODO.md')
    parser.add_argument('output_file', nargs='?', default='-',
                        help='Path to captured feed output (default: stdin)')
    parser.add_argument('--slot', choices=['morning', 'afternoon', 'evening'],
                        help='Override run-slot detection')
    parser.add_argument('--date', help='Override date as YYYY-MM-DD')
    args = parser.parse_args()

    if args.output_file == '-':
        text = sys.stdin.read()
    else:
        path = Path(args.output_file)
        if not path.exists():
            print(f'⚠️  Output file not found: {path}', file=sys.stderr)
            sys.exit(1)
        text = path.read_text('utf-8', errors='replace')

    run_time = datetime.now(timezone.utc)
    if args.date:
        try:
            d = datetime.strptime(args.date, '%Y-%m-%d')
            run_time = run_time.replace(year=d.year, month=d.month, day=d.day)
        except ValueError:
            pass

    slot = args.slot or detect_slot()

    if not LOG_FILE.exists():
        LOG_FILE.write_text(LOG_HEADER, 'utf-8')

    metrics = parse_output(text)
    update_feed_log(slot, metrics, run_time)

    recent = extract_recent_entries()
    update_todo(recent)

    q  = metrics['after_scoring']
    ff = len(metrics['failed_feeds'])
    print(
        f"✅ Logged {slot} run → {LOG_FILE}  "
        f"(quality={q if q is not None else '?'}, failed_feeds={ff})"
    )


if __name__ == '__main__':
    main()
