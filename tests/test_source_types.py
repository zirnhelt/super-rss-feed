"""Source types demote and cap an outlet whose format the reader rejects."""
from types import SimpleNamespace

import super_rss_curator_json as curator


def test_archdaily_showcases_are_capped_at_two_a_day():
    """2026-11-08: 16 of 18 ArchDaily 'Name / Firm' showcases rated bad
    ("No local hook"); its essays rated interesting, so it is capped, not blocked."""
    arts = [SimpleNamespace(source="ArchDaily", score=s, title=f"House {s} / Studio")
            for s in (60, 55, 50, 45)]
    kept = curator.apply_diversity_limits(arts, "design")
    assert [a.score for a in kept] == [60, 55]
    prefs = curator.SOURCE_PREFS
    assert prefs["source_map"]["ArchDaily"] == "project_showcase"
    assert prefs["source_types"]["project_showcase"]["score_adjustment"] < 0
