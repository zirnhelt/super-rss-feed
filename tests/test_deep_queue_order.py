"""The news deep-scoring queue rations relevance scoring, so its order matters.

_interleave_reserved must hold the reserve at every prefix length — the consumer
truncates the list at the slice cap, so a share honoured only overall is a share
of nothing.
"""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import super_rss_curator_json as m


def _a(tag):
    o = types.SimpleNamespace()
    o.url_hash = tag
    return o


def test_reserve_holds_at_every_prefix():
    primary = [_a(f'p{i}') for i in range(20)]
    reserved = list(reversed(primary))
    out = m._interleave_reserved(primary, reserved, 0.4)

    assert len(out) == 20
    assert len({a.url_hash for a in out}) == 20, 'no article may appear twice'

    from_reserved_top = {a.url_hash for a in reserved[:8]}
    for cut in (5, 10, 15, 20):
        got = sum(1 for a in out[:cut] if a.url_hash in from_reserved_top)
        assert got >= 1, f'reserve vanished in the first {cut} slots'


def test_no_reserve_list_is_a_passthrough():
    primary = [_a(f'p{i}') for i in range(5)]
    assert m._interleave_reserved(primary, [], 0.4) == primary
    assert m._interleave_reserved(primary, list(reversed(primary)), 0.0) == primary


def test_both_heads_reach_the_truncated_slice():
    """The point of the split: an article top-ranked on interest but mid on q_gate
    must survive a cut that only takes the first N."""
    arts = [_a(f'x{i}') for i in range(100)]
    by_gate = arts
    by_interest = [arts[73]] + [a for a in arts if a is not arts[73]]
    out = m._interleave_reserved(by_gate, by_interest, 0.4)
    slice_ = {a.url_hash for a in out[:50]}
    assert 'x73' in slice_, 'interest-ranked lead must reach the deep-scoring slice'
    assert 'x0' in slice_, 'newsworthiness lead must still reach it too'


def test_output_is_a_permutation_of_primary():
    primary = [_a(f'p{i}') for i in range(37)]
    reserved = sorted(primary, key=lambda a: a.url_hash)
    out = m._interleave_reserved(primary, reserved, 0.4)
    assert sorted(a.url_hash for a in out) == sorted(a.url_hash for a in primary)
