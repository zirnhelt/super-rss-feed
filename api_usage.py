"""Tracks external API call counts and a rough cost estimate for one curator run.

Call sites should call record_call(vendor) for simple per-request vendors
(Cohere, Brave, Kagi) and record_claude_usage(usage, stage=...) for Anthropic
responses, which also carry token counts. main() prints format_summary() once at
the end of a run; log_feed_results.py parses that line into FEED_LOG.md, and
get_summary_dict() goes into calibration_stats_cache.json, where the weekly audit
sets each stage's cost beside how well its scores predict the reader's ratings.

Pricing below is list price in USD per million tokens (Claude Haiku 4.5) and
flat per-call estimates for the other vendors. These are deliberately rough —
intended to give a relative sense of run cost, not an exact bill.
"""

import threading
from collections import defaultdict

_lock = threading.Lock()
_calls = defaultdict(int)
_claude_tokens = defaultdict(int)        # synchronous Messages API calls
_claude_batch_tokens = defaultdict(int)  # Message Batches API calls (50% discount)
_claude_stage_calls = defaultdict(int)
_claude_stage_cost = defaultdict(float)  # USD, batch discount applied

# cache_write is the 1-hour TTL rate (2x input): every cache_control in the
# curator sets ttl=1h. The 5-minute rate (1.25x) undercounted it by ~40%.
HAIKU_PRICING = {'input': 1.00, 'output': 5.00, 'cache_write': 2.00, 'cache_read': 0.10}
BATCH_DISCOUNT = 0.5

# Flat per-call estimates for vendors without token-based pricing tracked here.
# Brave Search is $5 per 1,000 requests. It was priced at 0.0 until 2026-09-23,
# which hid ~$7/month of the feed's spend on a key the podcast shares.
FLAT_COST_PER_CALL = {'cohere': 0.002, 'brave': 0.005, 'kagi': 0.0075, 'kite': 0.0}

VENDOR_ORDER = ['claude', 'cohere', 'brave', 'kagi', 'kite']


def record_call(vendor: str, n: int = 1) -> None:
    """Record n calls to a vendor that doesn't carry token-level usage."""
    with _lock:
        _calls[vendor] += n


def record_claude_usage(usage, batch: bool = False, stage: str = 'other') -> None:
    """Record one Claude API call plus its token usage.

    `usage` is an Anthropic response.usage (or batch result message.usage) object.
    `batch` selects the discounted Message Batches API pricing. `stage` names the
    pipeline step that paid for it ('gate', 'deep_score', 'theme', ...).
    """
    tokens = {
        'input': getattr(usage, 'input_tokens', 0) or 0,
        'output': getattr(usage, 'output_tokens', 0) or 0,
        'cache_write': getattr(usage, 'cache_creation_input_tokens', 0) or 0,
        'cache_read': getattr(usage, 'cache_read_input_tokens', 0) or 0,
    }
    with _lock:
        _calls['claude'] += 1
        bucket = _claude_batch_tokens if batch else _claude_tokens
        for kind, n in tokens.items():
            bucket[kind] += n
        _claude_stage_calls[stage] += 1
        _claude_stage_cost[stage] += _claude_cost(tokens, BATCH_DISCOUNT if batch else 1.0)


def _claude_cost(tokens: dict, discount: float = 1.0) -> float:
    return discount * sum(
        tokens.get(kind, 0) / 1_000_000 * rate
        for kind, rate in HAIKU_PRICING.items()
    )


def estimate_cost() -> float:
    """Rough total cost estimate in USD across all tracked vendors."""
    with _lock:
        total = _claude_cost(_claude_tokens) + _claude_cost(_claude_batch_tokens, BATCH_DISCOUNT)
        for vendor, n in _calls.items():
            if vendor != 'claude':
                total += n * FLAT_COST_PER_CALL.get(vendor, 0.0)
        return total


def get_summary_dict() -> dict:
    """Structured snapshot of call counts, token totals, and estimated cost.

    Used by the calibration agent's per-run audit stats.
    """
    with _lock:
        calls = dict(_calls)
        total_tokens = sum(_claude_tokens.values()) + sum(_claude_batch_tokens.values())
        by_stage = {stage: {'calls': n, 'est_cost_usd': round(_claude_stage_cost[stage], 4)}
                    for stage, n in sorted(_claude_stage_calls.items())}
    return {
        'calls': calls,
        'claude_tokens': total_tokens,
        'claude_by_stage': by_stage,
        'est_cost_usd': round(estimate_cost(), 4),
    }


def format_summary() -> str:
    """A single printable line summarizing call counts, Claude tokens, and est. cost."""
    with _lock:
        if not _calls:
            return ""

        parts = []
        for vendor in VENDOR_ORDER:
            if _calls.get(vendor):
                parts.append(f"{vendor.title()}={_calls[vendor]}")
        for vendor in sorted(_calls):
            if vendor not in VENDOR_ORDER:
                parts.append(f"{vendor.title()}={_calls[vendor]}")
        if not parts:
            return ""

        total_tokens = sum(_claude_tokens.values()) + sum(_claude_batch_tokens.values())

    line = f"📊 API calls: {', '.join(parts)}"
    if total_tokens:
        line += f" | Claude tokens: {total_tokens:,}"
    line += f" | Est. cost: ${estimate_cost():.4f}"
    return line


def reset() -> None:
    """Clear all tracked usage (used by tests / multi-phase scripts)."""
    with _lock:
        _calls.clear()
        _claude_tokens.clear()
        _claude_batch_tokens.clear()
        _claude_stage_calls.clear()
        _claude_stage_cost.clear()
