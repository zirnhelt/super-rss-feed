"""review.html's "How was the episode?" card saves `rating: 'episode'` rows into the same
feedback/YYYY-MM-DD.json as the article ratings. Article ratings grade story choice; only a
per-episode verdict can grade the writing, so the rows must reach the podcast's weekly review
without ever counting as an article rating anywhere in this repo."""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import article_review_audit
import feedback_archive
import feedback_trainer
import super_rss_curator_json as m

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / 'review.html').read_text(encoding='utf-8')

EPISODE = {'rating': 'episode', 'episode_date': '2026-10-12', 'episode_verdict': 'keep',
           'episode_reasons': ['Writing'], 'rated_at': '2026-10-13T14:00:00.000Z'}


def _article(url, rating='good', **extra):
    return {'url': url, 'title': f'Title {url}', 'rating': rating, 'source': 'S',
            'category': 'news', 'rated_at': '2026-10-13T13:00:00.000Z', **extra}


def _write_day(directory: Path, date: str, rows) -> None:
    directory.mkdir(exist_ok=True)
    (directory / f'{date}.json').write_text(json.dumps({'date': date, 'ratings': rows}))


class TestEpisodeRowsAreNotArticleRatings:
    def test_review_stats_ignore_them(self, tmp_path, monkeypatch):
        fb = tmp_path / 'feedback'
        _write_day(fb, '2026-10-12', [_article('u1'), _article('u2', 'bad')])
        # A day with only an episode verdict is not a day of article review.
        _write_day(fb, '2026-10-13', [EPISODE])
        monkeypatch.chdir(tmp_path)

        stats = m.review_history_stats('2026-10-13')

        assert stats['all_time'] == {'good': 1, 'bad': 1}
        assert stats['recent'] == {'good': 1, 'bad': 1}
        assert stats['days_reviewed'] == 1
        assert stats['streak'] == 1   # Oct 13 holds no article ratings: counted from the 12th

    def test_the_trainer_does_not_count_them_toward_a_qualifying_file(self, tmp_path, monkeypatch):
        today = datetime.now(timezone.utc).date()
        fb = tmp_path / 'feedback'
        four = [_article(f'u{i}') for i in range(feedback_trainer.MIN_RATINGS_PER - 1)]
        _write_day(fb, (today - timedelta(days=1)).isoformat(), four + [EPISODE])
        _write_day(fb, today.isoformat(), four + [_article('extra')])
        monkeypatch.setattr(feedback_trainer, 'FEEDBACK_DIR', fb)

        files, ratings = feedback_trainer.load_feedback(30)

        assert files == [f'{today.isoformat()}.json']
        assert all(r.get('rating') != 'episode' for r in ratings)

    def test_the_audit_skips_them(self, tmp_path):
        fb = tmp_path / 'feedback'
        _write_day(fb, '2026-10-12', [_article('u1'), EPISODE])

        loaded = article_review_audit.load_ratings(fb)

        assert [r['url'] for r in loaded] == ['u1']

    def test_the_archive_rollup_and_distillation_skip_them(self):
        rollup = feedback_archive.empty_rollup()
        absorbed = feedback_archive.fold_into_rollup(rollup, [_article('u1'), EPISODE])

        assert absorbed == 1
        assert 'episode' not in rollup['totals']
        assert feedback_archive.title_lines([EPISODE]) == []

    def test_a_row_without_a_url_never_becomes_a_reviewed_url(self, tmp_path, monkeypatch):
        _write_day(tmp_path / 'feedback', '2026-10-12', [_article('u1'), EPISODE])
        monkeypatch.chdir(tmp_path)

        assert m.load_reviewed_urls() == {'u1'}


def _between(start: str, end: str) -> str:
    i = PAGE.index(start)
    return PAGE[i:PAGE.index(end, i)]


class TestThePageContract:
    def test_the_card_does_not_depend_on_the_article_batch(self):
        """It is static markup outside the grid and the loading/empty/error boxes, rendered
        before init() runs, so an empty or failed batch cannot hide it."""
        card = PAGE.index('id="episode-box"')
        assert card < PAGE.index('id="loading-msg"')
        assert card < PAGE.index('id="article-grid"')
        boot = _between("window.addEventListener('DOMContentLoaded'", 'function populateExemplarCategories')
        assert boot.index('renderEpisodeCard()') < boot.index('init();')
        # A card failure must not stop the article flow.
        assert re.search(r'try \{ renderEpisodeCard\(\); \} catch', boot)

    def test_it_saves_the_agreed_row_shape(self):
        entry = _between('const entry = {\n        rating:          \'episode\'', '};')
        for field in ("rating:          'episode'", 'episode_date:', 'episode_verdict:',
                      'episode_reasons:', 'rated_at:'):
            assert field in entry, field
        # The verdict lives beside `rating`, never in it: 'skip' is already an article verdict.
        assert "episode_verdict: episodePick.verdict" in entry

    def test_the_verdicts_and_reasons_are_the_agreed_sets(self):
        assert "['keep', '👍 Keep'" in PAGE and "['meh', '😐 Meh'" in PAGE and "['skip', '👎 Skip'" in PAGE
        reasons = re.search(r"const EPISODE_REASONS\s*=\s*\[([^\]]*)\]", PAGE).group(1)
        assert re.findall(r"'([^']+)'", reasons) == [
            'Stories', 'Writing', 'Wrong fact', 'Too long', 'Repetitive', 'Hosts']

    def test_yesterday_is_the_default_of_the_last_three_dates(self):
        assert 'const EPISODE_DAYS     = 3;' in PAGE
        assert 'const EPISODE_DEFAULT  = 1;' in PAGE

    def test_dates_come_from_calendar_arithmetic_not_timestamps(self):
        """24 hours before a time just after midnight is the wrong date on the two days a
        year the clocks change."""
        body = _between('function episodeDates()', 'function episodeDateLabel')
        assert 'Date.UTC(y, m - 1, d - back)' in body
        assert 'Date.now()' not in body

    def test_dates_are_read_at_use_time_not_at_load(self):
        """The installed app is resumed, not reloaded: dates fixed at load kept offering the
        previous day's episodes, with that day's "yesterday" preselected, after midnight."""
        body = _between('function episodeDates()', 'function episodeDateLabel')
        code = re.sub(r'//[^\n]*', '', body)          # the comment explains the old way by name
        assert 'getTodayKey()' in code and 'todayKey' not in code.replace('getTodayKey', '')

    def test_a_page_resumed_on_a_new_day_deals_the_dates_again(self):
        handler = _between('function refreshEpisodeDates()', "document.addEventListener('visibilitychange'")
        assert 'episodeDates()[0]' in handler and 'episodePick.reasons.clear()' in handler
        assert "document.addEventListener('visibilitychange', refreshEpisodeDates)" in PAGE
        assert "window.addEventListener('pageshow', refreshEpisodeDates)" in PAGE
        # Re-rendering must not bind the click handler a second time.
        assert "box.dataset.wired" in _between('function renderEpisodeCard', 'function refreshEpisodeDates')

    def test_tapping_the_selected_date_again_keeps_the_answer(self):
        body = _between('function onEpisodeClick', 'function syncEpisodeCard')
        assert 'if (btn.dataset.date === episodePick.date) return;' in body
        assert body.index('=== episodePick.date) return') < body.index('episodePick.verdict = null')

    def test_every_github_call_on_the_save_path_can_time_out(self):
        """A request that never answered left the Save button disabled until a reload."""
        save = _between('async function saveFeedbackEntries', 'async function submitFeedback')
        assert 'await fetch(' not in save
        assert save.count('await githubFetch(') == 2
        helper = _between('async function githubFetch', '// What a saved row is merged on.')
        assert 'AbortSignal.timeout(SAVE_TIMEOUT_MS)' in helper
        # Older browsers have no AbortSignal.timeout: the call must still work, only unlimited.
        assert "typeof AbortSignal.timeout === 'function'" in helper
        assert "e?.name === 'TimeoutError'" in helper

    def test_rows_without_a_url_are_merged_by_date(self):
        """Every url-less row used to collapse onto the key `undefined`, so a second verdict
        saved the same day replaced the first."""
        assert 'merged.set(r.url' not in PAGE
        key = _between('function feedbackKey', '// Merges `entries`')
        assert "return `episode:${r.episode_date}`" in key
        save = _between('async function saveFeedbackEntries', 'async function submitFeedback')
        assert 'feedbackKey(r, `prior${i}`)' in save and 'feedbackKey(r, `new${i}`)' in save

    def test_it_asks_for_a_verdict_and_cannot_double_submit(self):
        body = _between('async function submitEpisodeVerdict', '// User-submitted exemplar')
        assert 'Pick Keep, Meh or Skip first.' in body
        assert 'episodePick.saving = true' in body and 'finally' in body

    def test_choices_are_exposed_to_assistive_tech(self):
        assert 'role="radiogroup" aria-label="Which episode"' in PAGE
        assert 'role="radiogroup" aria-label="Your verdict"' in PAGE
        assert 'aria-pressed' in _between('function renderEpisodeCard', 'function onEpisodeClick')
        assert 'role="status" aria-live="polite"' in _between('id="episode-box"', 'id="exemplar-box"')

    def test_nothing_third_party_reaches_the_card(self):
        """Every string in it is a constant of this page or a computed date; the labels still
        go through the page's escapers."""
        render = _between('function episodeDateLabel', 'function onEpisodeClick')
        assert 'escHtml(' in render and 'escAttr(' in render


@pytest.mark.parametrize('rating', ['good', 'bad', 'exemplar'])
def test_an_article_row_is_still_keyed_by_url(rating):
    """The merge change must leave every existing row type alone."""
    assert "if (typeof r?.url === 'string') return r.url;" in PAGE
