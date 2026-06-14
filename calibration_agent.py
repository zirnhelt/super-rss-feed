#!/usr/bin/env python3
"""Weekly calibration agent for the Super RSS Curator.

Reviews the rolling `calibration_stats_cache.json` (written each pipeline
run by `super_rss_curator_json.py::record_run_stats`) against the curator's
stated interests, maintains cross-week memory of recurring issues in
`calibration_memory/`, and proposes small, bounded adjustments to a
whitelisted set of config knobs (`config/calibration_bounds.json`).

Proposed changes are clamped to safety bounds, checked against
`global_caps` and a flip-flop guard, then either applied to
`config/limits.json` / `config/podcast_schedule.json` (auto-apply mode) or
left as a dry-run report. Every run appends a section to `CALIBRATION_LOG.md`
and updates the memory files.

Runs as its own weekly GitHub Actions job, separate from the twice-daily
pipeline. On any unexpected error this module logs "no changes" and exits 0
so it never fails the workflow.
"""

import json
import os
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anthropic

import api_usage
import config_loader

BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / 'calibration_memory'
CALIBRATION_LOG_FILE = BASE_DIR / 'CALIBRATION_LOG.md'
CALIBRATION_STATS_CACHE_FILE = BASE_DIR / 'calibration_stats_cache.json'

RECURRING_ISSUES_FILE = MEMORY_DIR / 'recurring_issues.json'
CHANGE_HISTORY_FILE = MEMORY_DIR / 'change_history.json'
NOTES_FILE = MEMORY_DIR / 'notes.md'

MODEL = "claude-sonnet-4-5"


# ---------------------------------------------------------------------------
# Audit data
# ---------------------------------------------------------------------------

def _load_stats_records() -> List[Dict]:
    if not CALIBRATION_STATS_CACHE_FILE.exists():
        return []
    try:
        with open(CALIBRATION_STATS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def gather_audit_data(window_days: int = 14) -> Dict:
    """Summarize the rolling run-stats cache for the calibration prompt.

    Returns aggregate/time-series data only; per-run analysis (e.g. detecting
    "theme score collapse") is left to the model, which has the full series.
    """
    records = _load_stats_records()
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    in_window = []
    for r in records:
        try:
            if datetime.fromisoformat(r['timestamp']) > cutoff:
                in_window.append(r)
        except (KeyError, ValueError):
            continue
    in_window.sort(key=lambda r: r.get('timestamp', ''))

    summary: Dict[str, Any] = {
        'window_days': window_days,
        'run_count': len(in_window),
        'run_ids': [r.get('run_id') for r in in_window],
    }
    if not in_window:
        return summary

    summary['date_range'] = {
        'first': in_window[0].get('timestamp'),
        'last': in_window[-1].get('timestamp'),
    }

    # Ingest / dedup trend
    summary['ingest'] = [
        {
            'run_id': r.get('run_id'),
            'fetched': r.get('ingest', {}).get('fetched'),
            'deduped': r.get('ingest', {}).get('deduped'),
            'new': r.get('ingest', {}).get('new'),
            'cross_run_story_dupes': r.get('ingest', {}).get('cross_run_story_dupes'),
        }
        for r in in_window
    ]

    # Score histograms per category, aggregated across the window
    score_hist_totals: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in in_window:
        for cat, hist in r.get('scoring', {}).get('score_histogram_by_category', {}).items():
            for bucket, count in hist.items():
                score_hist_totals[cat][bucket] += count
    summary['score_histogram_by_category'] = {
        cat: dict(buckets) for cat, buckets in score_hist_totals.items()
    }

    # Scrub removals aggregated by category
    cohere_removed: Dict[str, int] = defaultdict(int)
    haiku_removed: Dict[str, int] = defaultdict(int)
    for r in in_window:
        scrub = r.get('scrub', {})
        for cat, n in scrub.get('cohere_removed_by_category', {}).items():
            cohere_removed[cat] += n
        for cat, n in scrub.get('haiku_removed_by_category', {}).items():
            haiku_removed[cat] += n
    summary['scrub_removed_by_category'] = {
        'cohere': dict(cohere_removed),
        'haiku': dict(haiku_removed),
    }

    # Quality gate pass/drop totals by category
    passed: Dict[str, int] = defaultdict(int)
    dropped: Dict[str, int] = defaultdict(int)
    for r in in_window:
        qg = r.get('quality_gate', {})
        for cat, n in qg.get('passed_by_category', {}).items():
            passed[cat] += n
        for cat, n in qg.get('dropped_below_floor_by_category', {}).items():
            dropped[cat] += n
    summary['quality_gate_totals_by_category'] = {
        'passed': dict(passed),
        'dropped_below_floor': dict(dropped),
    }

    # Theme scoring trend per day (time series of mean/scored/histogram)
    theme_score_trends: Dict[str, List[Dict]] = defaultdict(list)
    for r in in_window:
        for day, stats in r.get('theme_scoring', {}).items():
            theme_score_trends[day].append({
                'run_id': r.get('run_id'),
                'mean': stats.get('mean'),
                'max': stats.get('max'),
                'scored': stats.get('scored'),
                'histogram': stats.get('histogram'),
            })
    summary['theme_score_trends'] = dict(theme_score_trends)

    # Theme routing trend (cross-day banking)
    summary['theme_routing'] = [
        {'run_id': r.get('run_id'), **r.get('theme_routing', {})}
        for r in in_window if r.get('theme_routing')
    ]

    # Podcast feed composition per day (one entry per run that generated that day's feed)
    podcast_feed_trends: Dict[str, List[Dict]] = defaultdict(list)
    for r in in_window:
        for day, fs in r.get('podcast_feeds', {}).items():
            podcast_feed_trends[day].append({'run_id': r.get('run_id'), **fs})
    summary['podcast_feed_trends'] = dict(podcast_feed_trends)

    # Holdover bank size trend (end-of-run snapshot) + banked-today counts
    summary['holdover'] = [
        {
            'run_id': r.get('run_id'),
            'bank_size_by_day_eod': r.get('holdover', {}).get('bank_size_by_day_eod', {}),
            'banked_today': r.get('holdover', {}).get('banked_today', 0),
        }
        for r in in_window if r.get('holdover')
    ]

    # Final feed sizes trend
    summary['final_feeds'] = [
        {'run_id': r.get('run_id'), **r.get('final_feeds', {})}
        for r in in_window
    ]

    # API cost
    costs = [r.get('api_usage', {}).get('est_cost_usd', 0) for r in in_window]
    summary['api_cost'] = {
        'total_usd': round(sum(costs), 4),
        'mean_per_run_usd': round(sum(costs) / len(costs), 4) if costs else 0,
    }

    return summary


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

def load_memory_context() -> Dict:
    def _load_json(path: Path, default: Dict) -> Dict:
        if not path.exists():
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default

    recurring = _load_json(RECURRING_ISSUES_FILE, {'issues': []})
    history = _load_json(CHANGE_HISTORY_FILE, {'changes': []})
    notes = ''
    if NOTES_FILE.exists():
        try:
            notes = NOTES_FILE.read_text(encoding='utf-8')
        except Exception:
            notes = ''

    return {'recurring_issues': recurring, 'change_history': history, 'notes': notes}


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

OUTPUT_SCHEMA = """Respond with a single JSON object (no markdown fences) with this shape:
{
  "analysis": "2-4 paragraph summary of what you observed in the audit window",
  "proposed_changes": [
    {"knob": "limits.min_score_by_category.ai-tech", "new_value": 25, "rationale": "..."}
  ],
  "proposed_keyword_changes": [
    {"knob": "podcast.schedule.saturday.anti_keywords", "additions": ["..."], "removals": ["..."], "rationale": "..."}
  ],
  "issue_updates": [
    {"id": "tuesday-theme-score-collapse", "theme": "tuesday", "status": "open|monitoring|resolved",
     "description": "...", "actions_taken": "summary of what this run did about it (or 'none')",
     "recommendation_pending": false}
  ],
  "human_recommendations": [
    "Free-text recommendations for changes outside the auto-tunable whitelist (e.g. scoring_prompt rewrites, category definitions)."
  ]
}
Only propose changes for knobs listed in calibration_bounds.json's "knobs" or "keyword_lists" sections.
Never propose changes to anything in the "forbidden" list — raise those as human_recommendations instead.
If nothing needs to change, return empty lists for proposed_changes/proposed_keyword_changes/issue_updates,
and still fill in "analysis"."""

PHILOSOPHY = """You are the weekly calibration agent for a personal RSS/podcast curation pipeline.
Your job is to keep the article scoring, filtering, and podcast theme routing aligned with the
maintainer's stated interests, based on aggregate statistics from recent runs (no article text or
URLs are available to you, only counts/histograms/means).

Guidelines:
- Be conservative. Prefer small steps (the bounds file enforces max_step, but you should usually
  propose less than the max unless evidence is strong).
- Use memory: don't propose reversing a change made in the last few runs unless you have new
  evidence the previous change made things worse. If a change you made previously hasn't had
  enough time to show effect, say so in "analysis" and don't touch that knob again yet.
- Distinguish between "this knob is the right lever" vs "the real fix is a prompt/category
  change" (those are forbidden for auto-edit — surface them as human_recommendations).
- A theme whose mean score is collapsing toward 0 across multiple consecutive runs is a strong
  signal (often caused by a scoring_prompt change) — flag it as a recurring issue. If lowering
  min_score/holdover_threshold won't fix a near-zero mean, say so and recommend a prompt review
  instead of just lowering thresholds repeatedly.
- Keyword list changes should be small, specific, and grounded in what's plausible for the theme.
"""


def build_audit_prompt(
    audit_data: Dict,
    memory: Dict,
    current_config: Dict,
    bounds: Dict,
    interests_text: str,
) -> Tuple[str, str]:
    system_prompt = PHILOSOPHY + "\n\n" + OUTPUT_SCHEMA

    user_parts = [
        "## Curator interests/profile (for context, do not propose changes to this file)\n",
        interests_text.strip(),
        "\n\n## Whitelisted knobs and bounds (config/calibration_bounds.json)\n",
        json.dumps(bounds, indent=2),
        "\n\n## Current values of relevant config\n",
        json.dumps({
            'limits': current_config.get('limits', {}),
            'podcast_schedule_top_level': {
                k: v for k, v in current_config.get('podcast_schedule', {}).items()
                if k != 'schedule'
            },
            'podcast_schedule_per_theme': {
                day: {
                    'min_score': cfg.get('min_score'),
                    'holdover_threshold': cfg.get('holdover_threshold'),
                    'keywords': cfg.get('keywords', []),
                    'anti_keywords': cfg.get('anti_keywords', []),
                }
                for day, cfg in current_config.get('podcast_schedule', {}).get('schedule', {}).items()
            },
        }, indent=2),
        "\n\n## Audit data (rolling window)\n",
        json.dumps(audit_data, indent=2),
        "\n\n## Memory: recurring issues\n",
        json.dumps(memory.get('recurring_issues', {}), indent=2),
        "\n\n## Memory: recent change history\n",
        json.dumps(memory.get('change_history', {}), indent=2),
        "\n\n## Memory: free-text notes\n",
        memory.get('notes', '') or '(empty)',
        "\n\nReview the above and produce your JSON response per the schema in the system prompt.",
    ]
    return system_prompt, "\n".join(user_parts)


# ---------------------------------------------------------------------------
# Claude call
# ---------------------------------------------------------------------------

def call_claude_with_memory(system_prompt: str, user_prompt: str, api_key: str) -> Optional[Dict]:
    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        api_usage.record_claude_usage(response.usage)

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            lines = raw.splitlines()
            inner = lines[1:]
            if inner and inner[-1].strip() == "```":
                inner = inner[:-1]
            raw = "\n".join(inner).strip()

        start = raw.find('{')
        if start == -1:
            raise ValueError("No JSON object in response")
        result, _ = json.JSONDecoder().raw_decode(raw, start)
        return result
    except Exception as e:
        print(f"  ⚠️ Calibration agent Claude call/parse failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Validation / clamping
# ---------------------------------------------------------------------------

def _get_current_value(config: Dict, path: List[str]) -> Any:
    node = config
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _is_forbidden(knob: str, forbidden: List[str]) -> bool:
    parts = knob.split('.')
    for pattern in forbidden:
        pparts = pattern.split('.')
        if len(pparts) != len(parts):
            continue
        if all(pp == '*' or pp == p for pp, p in zip(pparts, parts)):
            return True
    return False


def _recent_changes_for_knob(change_history: Dict, knob: str, lookback_runs: int) -> List[Dict]:
    changes = [c for c in change_history.get('changes', []) if c.get('knob') == knob]
    changes.sort(key=lambda c: c.get('run_date', ''), reverse=True)
    return changes[:lookback_runs]


def validate_and_clamp_changes(
    result: Dict,
    bounds: Dict,
    current_config: Dict,
    memory: Dict,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Validate proposed_changes/proposed_keyword_changes against calibration_bounds.json.

    Returns (accepted, rejected, clamping_notes). `accepted` entries have
    'knob', 'file', 'path', 'old_value', 'new_value', 'rationale', and for
    keyword lists 'additions'/'removals' instead of old/new value.
    """
    knobs = bounds.get('knobs', {})
    keyword_lists = bounds.get('keyword_lists', {})
    forbidden = bounds.get('forbidden', [])
    global_caps = bounds.get('global_caps', {})
    flip_flop = bounds.get('flip_flop_guard', {})
    lookback_runs = flip_flop.get('lookback_runs', 4)
    change_history = memory.get('change_history', {})

    accepted: List[Dict] = []
    rejected: List[Dict] = []
    clamping_notes: List[Dict] = []
    files_touched = set()

    # --- scalar knobs ---
    for change in result.get('proposed_changes', []) or []:
        knob = change.get('knob', '')
        rationale = change.get('rationale', '')
        new_value = change.get('new_value')

        if _is_forbidden(knob, forbidden):
            rejected.append({**change, 'reason': 'forbidden knob'})
            continue

        spec = knobs.get(knob)
        if not spec:
            rejected.append({**change, 'reason': 'unknown knob (not in calibration_bounds.json)'})
            continue

        old_value = _get_current_value(current_config, [_config_root(spec)] + spec['path'])
        if old_value is None:
            rejected.append({**change, 'reason': 'current value not found in config'})
            continue

        try:
            if spec['type'] == 'int':
                new_value = int(round(float(new_value)))
            elif spec['type'] == 'float':
                new_value = float(new_value)
        except (TypeError, ValueError):
            rejected.append({**change, 'reason': 'new_value not numeric'})
            continue

        original_proposed = new_value

        # Clamp to [min, max]
        clamped_to_bounds = max(spec['min'], min(spec['max'], new_value))

        # Clamp step size relative to current value
        max_step = spec.get('max_step')
        if max_step is not None:
            delta = clamped_to_bounds - old_value
            if abs(delta) > max_step:
                step = max_step if delta > 0 else -max_step
                clamped_to_bounds = old_value + step
                if spec['type'] == 'int':
                    clamped_to_bounds = int(round(clamped_to_bounds))

        new_value = clamped_to_bounds
        if new_value != original_proposed:
            clamping_notes.append({
                'knob': knob, 'proposed': original_proposed, 'clamped_to': new_value,
            })

        if new_value == old_value:
            rejected.append({**change, 'reason': 'no-op after clamping (already at/near value)'})
            continue

        # Flip-flop guard: reject if this reverses a recent change without a linked issue update
        recent = _recent_changes_for_knob(change_history, knob, lookback_runs)
        if recent:
            last_delta = recent[0].get('delta', 0)
            this_delta = new_value - old_value
            has_issue_evidence = bool(result.get('issue_updates'))
            if last_delta and this_delta and (last_delta > 0) != (this_delta > 0) and not has_issue_evidence:
                rejected.append({**change, 'reason': 'flip-flop guard: reverses a recent change with no new evidence'})
                continue

        accepted.append({
            'knob': knob,
            'file': spec['file'],
            'path': spec['path'],
            'old_value': old_value,
            'new_value': new_value,
            'rationale': rationale,
        })
        files_touched.add(spec['file'])

    # --- keyword list knobs ---
    for change in result.get('proposed_keyword_changes', []) or []:
        knob = change.get('knob', '')
        rationale = change.get('rationale', '')
        additions = [a for a in (change.get('additions') or []) if isinstance(a, str)]
        removals = [r for r in (change.get('removals') or []) if isinstance(r, str)]

        if _is_forbidden(knob, forbidden):
            rejected.append({**change, 'reason': 'forbidden knob'})
            continue

        # Match against templated keyword_lists, e.g. "podcast.schedule.saturday.keywords"
        spec = None
        spec_key = None
        for template_key, template_spec in keyword_lists.items():
            prefix, _, suffix = template_key.partition('<day>')
            if not suffix:
                continue
            prefix = prefix.rstrip('.')
            suffix = suffix.lstrip('.')
            if knob.startswith(prefix + '.') and knob.endswith('.' + suffix):
                day = knob[len(prefix) + 1: -(len(suffix) + 1)]
                if day in template_spec.get('applies_to_days', []):
                    spec = template_spec
                    spec_key = (template_key, day)
                break

        if not spec:
            rejected.append({**change, 'reason': 'unknown or inapplicable keyword list knob'})
            continue

        day = spec_key[1]
        path = [p.format(day=day) for p in spec['path_template']]
        old_list = _get_current_value(current_config, ['podcast_schedule'] + path)
        if old_list is None:
            old_list = []

        max_add = spec.get('max_additions_per_run', 0)
        max_rem = spec.get('max_removals_per_run', 0)

        if spec.get('mode') == 'additions_only':
            removals = []
        if len(additions) > max_add:
            clamping_notes.append({'knob': knob, 'note': f'additions truncated to {max_add}'})
            additions = additions[:max_add]
        if len(removals) > max_rem:
            clamping_notes.append({'knob': knob, 'note': f'removals truncated to {max_rem}'})
            removals = removals[:max_rem]

        additions = [a for a in additions if a not in old_list]
        removals = [r for r in removals if r in old_list]

        if not additions and not removals:
            rejected.append({**change, 'reason': 'no-op (no new valid additions/removals)'})
            continue

        accepted.append({
            'knob': knob,
            'file': spec['file'],
            'path': path,
            'additions': additions,
            'removals': removals,
            'rationale': rationale,
        })
        files_touched.add(spec['file'])

    # --- global caps ---
    max_total = global_caps.get('max_total_changes_per_run')
    if max_total is not None and len(accepted) > max_total:
        overflow = accepted[max_total:]
        accepted = accepted[:max_total]
        for change in overflow:
            rejected.append({**change, 'reason': f'exceeded global cap of {max_total} changes per run'})

    max_files = global_caps.get('max_config_files_touched_per_run')
    if max_files is not None:
        kept_files = set()
        final_accepted = []
        overflow = []
        for change in accepted:
            f = change['file']
            if f in kept_files or len(kept_files) < max_files:
                kept_files.add(f)
                final_accepted.append(change)
            else:
                overflow.append(change)
        accepted = final_accepted
        for change in overflow:
            rejected.append({**change, 'reason': f'exceeded global cap of {max_files} config files touched per run'})

    return accepted, rejected, clamping_notes


def _config_root(spec: Dict) -> str:
    """Map a knob's `file` to the key used in current_config."""
    if spec['file'] == 'config/limits.json':
        return 'limits'
    if spec['file'] == 'config/podcast_schedule.json':
        return 'podcast_schedule'
    return ''


# ---------------------------------------------------------------------------
# Apply changes
# ---------------------------------------------------------------------------

def _set_path(node: Dict, path: List[str], value: Any) -> None:
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value


def apply_bounded_adjustments(accepted: List[Dict], dry_run: bool) -> List[Dict]:
    """Write accepted changes to their config files (unless dry_run).

    Returns the list of applied changes (same shape as `accepted`, with
    keyword changes resolved to their resulting before/after lists) for the
    changelog, regardless of dry_run.
    """
    by_file: Dict[str, List[Dict]] = defaultdict(list)
    for change in accepted:
        by_file[change['file']].append(change)

    applied: List[Dict] = []
    for file_rel, changes in by_file.items():
        file_path = BASE_DIR / file_rel
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            for change in changes:
                applied.append({**change, 'error': f'failed to load {file_rel}: {e}'})
            continue

        for change in changes:
            path = change['path']
            if 'new_value' in change:
                _set_path(config, path, change['new_value'])
                applied.append(change)
            else:
                current = _get_current_value(config, path) or []
                updated = [v for v in current if v not in change.get('removals', [])]
                updated.extend(change.get('additions', []))
                _set_path(config, path, updated)
                applied.append({**change, 'old_value': current, 'new_value': updated})

        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    f.write('\n')
            except Exception as e:
                for change in changes:
                    print(f"  ⚠️ Failed to write {file_rel}: {e}")

    return applied


# ---------------------------------------------------------------------------
# Changelog + memory updates
# ---------------------------------------------------------------------------

def write_changelog(
    result: Optional[Dict],
    applied: List[Dict],
    rejected: List[Dict],
    clamping_notes: List[Dict],
    audit_data: Dict,
    dry_run: bool,
) -> None:
    now = datetime.now(timezone.utc)
    run_date = now.strftime('%Y-%m-%d')

    lines = [f"\n## {run_date}{' (dry run)' if dry_run else ''}\n"]

    if result is None:
        lines.append("No changes: Claude call or response parsing failed. See logs for details.\n")
    else:
        lines.append(f"Audit window: {audit_data.get('run_count', 0)} runs "
                      f"({audit_data.get('date_range', {}).get('first', '?')} to "
                      f"{audit_data.get('date_range', {}).get('last', '?')}).\n")
        lines.append(f"\n**Analysis**\n\n{result.get('analysis', '').strip()}\n")

        if applied:
            lines.append("\n**Changes applied" + (" (dry run, not written)" if dry_run else "") + "**\n")
            for c in applied:
                if 'additions' in c or 'removals' in c:
                    parts = []
                    if c.get('additions'):
                        parts.append(f"+{c['additions']}")
                    if c.get('removals'):
                        parts.append(f"-{c['removals']}")
                    lines.append(f"- `{c['knob']}`: {', '.join(parts)} — {c.get('rationale', '')}")
                else:
                    lines.append(f"- `{c['knob']}`: {c['old_value']} → {c['new_value']} — {c.get('rationale', '')}")
        else:
            lines.append("\nNo changes applied this run.\n")

        if clamping_notes:
            lines.append("\n**Clamped**\n")
            for n in clamping_notes:
                if 'clamped_to' in n:
                    lines.append(f"- `{n['knob']}`: proposed {n['proposed']} clamped to {n['clamped_to']}")
                else:
                    lines.append(f"- `{n['knob']}`: {n.get('note', '')}")

        if rejected:
            lines.append("\n**Rejected**\n")
            for r in rejected:
                lines.append(f"- `{r.get('knob', '?')}`: {r.get('reason', '')}")

        if result.get('human_recommendations'):
            lines.append("\n**Human recommendations**\n")
            for rec in result['human_recommendations']:
                lines.append(f"- {rec}")

    section = "\n".join(lines) + "\n"

    if not CALIBRATION_LOG_FILE.exists():
        CALIBRATION_LOG_FILE.write_text("# Calibration Log\n", encoding='utf-8')
    with open(CALIBRATION_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(section)

    if result is None:
        return

    # Update change_history.json
    history = json.loads(CHANGE_HISTORY_FILE.read_text(encoding='utf-8')) if CHANGE_HISTORY_FILE.exists() else {'changes': []}
    for c in applied:
        if 'additions' in c or 'removals' in c:
            continue
        history['changes'].append({
            'run_date': run_date,
            'knob': c['knob'],
            'old_value': c['old_value'],
            'new_value': c['new_value'],
            'delta': c['new_value'] - c['old_value'],
            'rationale': c.get('rationale', ''),
            'dry_run': dry_run,
        })
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(CHANGE_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # Update recurring_issues.json
    issues_data = json.loads(RECURRING_ISSUES_FILE.read_text(encoding='utf-8')) if RECURRING_ISSUES_FILE.exists() else {'issues': []}
    issues_by_id = {issue['id']: issue for issue in issues_data.get('issues', []) if 'id' in issue}
    for update in result.get('issue_updates', []) or []:
        issue_id = update.get('id')
        if not issue_id:
            continue
        existing = issues_by_id.get(issue_id)
        if existing:
            existing['last_observed'] = run_date
            existing['status'] = update.get('status', existing.get('status', 'open'))
            existing['description'] = update.get('description', existing.get('description', ''))
            existing.setdefault('actions_taken', []).append({
                'run_date': run_date, 'action': update.get('actions_taken', '')
            })
            existing['recommendation_pending'] = update.get('recommendation_pending', existing.get('recommendation_pending', False))
        else:
            new_issue = {
                'id': issue_id,
                'theme': update.get('theme'),
                'first_observed': run_date,
                'last_observed': run_date,
                'status': update.get('status', 'open'),
                'description': update.get('description', ''),
                'evidence_runs': list(audit_data.get('run_ids', [])),
                'actions_taken': [{'run_date': run_date, 'action': update.get('actions_taken', '')}],
                'recommendation_pending': update.get('recommendation_pending', False),
            }
            issues_data.setdefault('issues', []).append(new_issue)
            issues_by_id[issue_id] = new_issue
    with open(RECURRING_ISSUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(issues_data, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # Append to notes.md
    with open(NOTES_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n## {run_date}{' (dry run)' if dry_run else ''}\n\n{result.get('analysis', '').strip()}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    dry_run = os.environ.get('CALIBRATION_DRY_RUN', 'true').strip().lower() not in ('0', 'false', 'no')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set; skipping calibration run")
        write_changelog(None, [], [], [], {}, dry_run)
        return

    audit_data = gather_audit_data()
    if audit_data.get('run_count', 0) == 0:
        print("ℹ️ No calibration stats in window; skipping calibration run")
        write_changelog(None, [], [], [], audit_data, dry_run)
        return

    memory = load_memory_context()
    current_config = {
        'limits': config_loader.load_limits_config(),
        'podcast_schedule': config_loader.load_podcast_schedule_config(),
    }
    bounds = config_loader.load_calibration_bounds()
    interests_text = config_loader.load_scoring_interests()

    system_prompt, user_prompt = build_audit_prompt(audit_data, memory, current_config, bounds, interests_text)
    result = call_claude_with_memory(system_prompt, user_prompt, api_key)

    if result is None:
        write_changelog(None, [], [], [], audit_data, dry_run)
        return

    accepted, rejected, clamping_notes = validate_and_clamp_changes(result, bounds, current_config, memory)
    applied = apply_bounded_adjustments(accepted, dry_run)
    write_changelog(result, applied, rejected, clamping_notes, audit_data, dry_run)

    print(f"✅ Calibration run complete: {len(applied)} applied, {len(rejected)} rejected, {len(clamping_notes)} clamped"
          + (" (dry run, not written)" if dry_run else ""))
    summary = api_usage.format_summary()
    if summary:
        print(summary)


if __name__ == '__main__':
    main()
