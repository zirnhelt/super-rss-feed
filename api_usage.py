"""Tracks external API call counts and a rough cost estimate for one curator run.

Call sites should call record_call(vendor) for simple per-request vendors
(Cohere, Brave, Kagi) and record_claude_usage(usage, stage=...) for Anthropic
responses, which also carry token counts. main() prints format_summary() once at
the end of a run; log_feed_results.py parses that line into FEED_LOG.md, and
get_summary_dict() goes into calibration_stats_cache.json, where the weekly audit
sets each stage's cost beside how well its scores predict the reader's ratings.

Pricing below is list price in USD per million tokens (Claude Haiku 5.5) and
flat per-call estimates for the other vendors. These are deliberately rough —
intended to give a relative sense of run cost, not an exact bill.

Every Claude caller also shares HAIKU_MODEL, HAIKU_EXTRA_BODY and
response_text() from here, since each one already imports this module.
"""

import threading
from collections import defaultdict

_lock = threading.Lock()
_calls = defaultdict(int)
_claude_tokens = defaultdict(int)        # synchronous Messages API calls
_claude_batch_tokens = defaultdict(int)  # Message Batches API calls (50% discount)
_claude_stage_calls = defaultdict(int)
_claude_stage_cost = defaultdict(float)  # USD, batch discount applied
_claude_long_prompt_cost = 0.0           # USD above base rate for >100K-token prompts

# Haiku 5.5 replaced Haiku 4.5 on 2026-10-08 at a tenth of the price. Its
# tokenizer counts the same text as ~30% more tokens, so token totals jumped
# that day without the workload changing.
HAIKU_MODEL = 'claude-haiku-5-5'

# Haiku 5.5 thinks unless told not to, and thinking shares max_tokens with the
# answer. Every call here is short structured output that ran without thinking
# on 4.5, so it stays off. anthropic==0.40.0 predates the `thinking` kwarg (and
# cannot parse thinking blocks), hence extra_body; batch params take the same
# key directly.
HAIKU_EXTRA_BODY = {'thinking': {'type': 'disabled'}}

# cache_write is the 1-hour TTL rate (2x input): every cache_control in the
# curator sets ttl=1h. The 5-minute rate (1.25x) undercounted it by ~40%.
HAIKU_PRICING = {'input': 0.10, 'output': 0.50, 'cache_write': 0.20, 'cache_read': 0.01}
# A prompt over 100K tokens (fresh + cached) is billed on a second rate card, 5x.
LONG_PROMPT_TOKENS = 100_000
LONG_PROMPT_MULTIPLIER = 5.0
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
    global _claude_long_prompt_cost
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
        discount = BATCH_DISCOUNT if batch else 1.0
        prompt = tokens['input'] + tokens['cache_write'] + tokens['cache_read']
        if prompt > LONG_PROMPT_TOKENS:
            # Totals are priced at the base rate; this call's surcharge is kept apart.
            surcharge = _claude_cost(tokens, discount) * (LONG_PROMPT_MULTIPLIER - 1)
            _claude_long_prompt_cost += surcharge
            _claude_stage_cost[stage] += surcharge
        _claude_stage_cost[stage] += _claude_cost(tokens, discount)


def response_text(response) -> str:
    """The text blocks of a Claude response, joined; '' when there are none.

    Never content[0]: a reply can lead with a non-text block. A refusal is a
    normal 200 with stop_reason "refusal" and no text — it is logged and comes
    back as '', which every caller already treats as a failed call.
    """
    if getattr(response, 'stop_reason', None) == 'refusal':
        category = getattr(getattr(response, 'stop_details', None), 'category', None)
        print(f"  ⚠️ Claude declined the request (refusal: {category or 'unspecified'})")
    return ''.join(getattr(b, 'text', '') for b in (getattr(response, 'content', None) or [])
                   if getattr(b, 'type', None) == 'text')


def _claude_cost(tokens: dict, discount: float = 1.0) -> float:
    return discount * sum(
        tokens.get(kind, 0) / 1_000_000 * rate
        for kind, rate in HAIKU_PRICING.items()
    )


def estimate_cost() -> float:
    """Rough total cost estimate in USD across all tracked vendors."""
    with _lock:
        total = (_claude_cost(_claude_tokens) + _claude_cost(_claude_batch_tokens, BATCH_DISCOUNT)
                 + _claude_long_prompt_cost)
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
    global _claude_long_prompt_cost
    with _lock:
        _calls.clear()
        _claude_tokens.clear()
        _claude_batch_tokens.clear()
        _claude_stage_calls.clear()
        _claude_stage_cost.clear()
        _claude_long_prompt_cost = 0.0
