"""Tracks external API call counts and a rough cost estimate for one curator run.

Call sites should call record_call(vendor) for simple per-request vendors
(Cohere, Brave, Kagi) and record_claude_usage(usage) for Anthropic responses,
which also carry token counts. main() prints format_summary() once at the end
of a run; log_feed_results.py parses that line into FEED_LOG.md.

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

HAIKU_PRICING = {'input': 1.00, 'output': 5.00, 'cache_write': 1.25, 'cache_read': 0.10}
BATCH_DISCOUNT = 0.5

# Flat per-call estimates for vendors without token-based pricing tracked here.
FLAT_COST_PER_CALL = {'cohere': 0.002, 'brave': 0.0, 'kagi': 0.0075}

VENDOR_ORDER = ['claude', 'cohere', 'brave', 'kagi']


def record_call(vendor: str, n: int = 1) -> None:
    """Record n calls to a vendor that doesn't carry token-level usage."""
    with _lock:
        _calls[vendor] += n


def record_claude_usage(usage, batch: bool = False) -> None:
    """Record one Claude API call plus its token usage.

    `usage` is an Anthropic response.usage (or batch result message.usage) object.
    `batch` selects the discounted Message Batches API pricing.
    """
    with _lock:
        _calls['claude'] += 1
        bucket = _claude_batch_tokens if batch else _claude_tokens
        bucket['input'] += getattr(usage, 'input_tokens', 0) or 0
        bucket['output'] += getattr(usage, 'output_tokens', 0) or 0
        bucket['cache_write'] += getattr(usage, 'cache_creation_input_tokens', 0) or 0
        bucket['cache_read'] += getattr(usage, 'cache_read_input_tokens', 0) or 0


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
    return {
        'calls': calls,
        'claude_tokens': total_tokens,
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
