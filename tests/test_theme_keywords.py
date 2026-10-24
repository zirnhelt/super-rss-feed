"""Theme keywords match whole words, not substrings.

`_keyword_matches` decides which bucket an article fills first in its day's
podcast feed, so a false hit promotes it over on-theme material. On 2026-10-23
the Friday (Wild Spaces) feed carried a B.C. election poll ("on the campaign
trail") and a Six Flags roller-coaster death ("amusement park regulations")
as keyword matches, and the show built its deep dive from them. Across the
week's pool the substring test also let "nation" hit "international", "mill"
hit "million", "zine" hit "magazine", "bat" hit "battery" and "park" hit
"spark". Every case below is real feed text from that week.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config_loader
import super_rss_curator_json as m


def _hits(text: str, keywords) -> int:
    return m._keyword_match_count(text, keywords)


def _day_keywords(day: str):
    return config_loader.load_podcast_schedule_config()['schedule'][day]['keywords']


class TestWholeWords:
    def test_inside_a_word_is_not_a_hit(self):
        assert _hits("international fake news ring targeting b.c. companies", ['nation']) == 0
        assert _hits("feds investing up to $50 million in transformer plant", ['mill']) == 0
        assert _hits("quanta magazine reports", ['zine']) == 0
        assert _hits("nasa batteries survive extreme cold", ['bat']) == 0
        assert _hits("grenade exercise sparked deadly fire", ['park']) == 0

    def test_plural_still_hits(self):
        assert _hits("national parks are offering free off-road wheelchairs", ['national park']) == 1
        assert _hits("wildfires impact air quality", ['wildfire']) == 1

    def test_star_matches_word_endings_from_the_start_of_a_word(self):
        assert _hits("researchers say", ['research*']) == 1
        assert _hits("flooding along the fraser", ['flood*']) == 1
        assert _hits("a revolutionary design", ['evolution*']) == 0

    def test_counts_keywords_not_occurrences(self):
        assert _hits("salmon, salmon and more salmon in the watershed", ['salmon', 'watershed']) == 2


class TestWildSpacesKeywords:
    """The two articles that reached the 2026-10-23 Friday deep dive."""

    def test_campaign_trail_is_not_a_trail(self):
        text = ("conservatives remain ahead in polls as b.c. election day nears b.c. conservative "
                "leader lorne doerkson (left) and b.c. ndp leader david eby on the campaign trail "
                "ahead of the provincial election")
        assert _hits(text, _day_keywords('friday')) == 0

    def test_amusement_park_is_not_a_park(self):
        text = ("a tragic death at six flags has exposed a terrifying truth: roller coasters have a "
                "hidden safety loophole after a fatal incident in georgia, questions are mounting "
                "about amusement park regulations, state inspections, and federal oversight.")
        assert _hits(text, _day_keywords('friday')) == 0

    def test_a_software_environment_is_not_the_environment(self):
        keywords = _day_keywords('friday')
        assert _hits("my proxmox server now runs a full dev environment for ai agents", keywords) == 0
        assert _hits("a proper environmental assessment of the mine", keywords) >= 1
        assert _hits("the united nations environment programme report", keywords) >= 1

    def test_outdoor_parks_and_trails_still_hit(self):
        keywords = _day_keywords('friday')
        assert _hits("tsútswecw provincial park ahead of the salute to the sockeye", keywords) >= 1
        assert _hits("kilian jornet’s nnormal pushes beyond trail running", keywords) >= 1
        assert _hits("tricouni berg lake backpacking trip", keywords) >= 1


class TestSecondSenses:
    def test_the_guardian_newspaper_is_not_a_guardian_program(self):
        assert _hits("told british newspaper the guardian that", _day_keywords('thursday')) == 0

    def test_likely_the_adverb_is_not_likely_the_town(self):
        assert _hits("teen girls are now more likely to vape than boys", ['Likely, B.C.']) == 0


def test_every_theme_keyword_compiles():
    for day, cfg in config_loader.load_podcast_schedule_config()['schedule'].items():
        for kw in cfg.get('keywords', []) + cfg.get('anti_keywords', []):
            assert m._keyword_pattern(kw).pattern, (day, kw)
