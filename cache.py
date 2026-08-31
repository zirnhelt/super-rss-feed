import json
import time
from email.utils import parsedate_to_datetime
from typing import Optional


class Cache:
    """Generic JSON cache backed by a file, with optional TTL pruning.

    Values may be dicts (TTL checked via ts_field) or raw floats (TTL is the
    value itself — used for {url: timestamp} caches like shown_articles).
    """

    def __init__(self, path: str, ttl_hours: float = None, ts_field: str = 'timestamp'):
        self.path = path
        self.ttl_sec = ttl_hours * 3600 if ttl_hours is not None else None
        self.ts_field = ts_field

    def load(self) -> dict:
        try:
            with open(self.path) as f:
                data = json.load(f)
            if self.ttl_sec is not None:
                cutoff = time.time() - self.ttl_sec
                data = {
                    k: v for k, v in data.items()
                    if (v.get(self.ts_field, 0) if isinstance(v, dict) else v) > cutoff
                }
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, data: dict) -> None:
        try:
            with open(self.path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save {self.path}: {e}")


class FeedHTTPCache:
    """Per-feed HTTP caching state for conditional GET and poll-skip logic.

    Stores ETag, Last-Modified, and skip_until (from Cache-Control max-age or
    Retry-After) keyed by feed URL. Keeps feed polling respectful and cheap.
    """

    def __init__(self, path: str):
        self.path = path
        self._data: dict = {}

    def load(self) -> None:
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}

    def save(self) -> None:
        try:
            with open(self.path, 'w') as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save {self.path}: {e}")

    def should_skip(self, url: str) -> bool:
        """True if Cache-Control max-age or Retry-After says it's too early to poll."""
        skip_until = self._data.get(url, {}).get('skip_until')
        return skip_until is not None and time.time() < skip_until

    def request_headers(self, url: str) -> dict:
        """Return conditional GET headers for this URL.

        Sends only one of If-None-Match or If-Modified-Since — some servers
        return a full body when both are present.
        """
        entry = self._data.get(url, {})
        if entry.get('etag'):
            return {'If-None-Match': entry['etag']}
        if entry.get('last_modified'):
            return {'If-Modified-Since': entry['last_modified']}
        return {}

    def update_from_response(self, url: str, response) -> None:
        """Store caching headers from a 200 response."""
        entry = self._data.get(url, {})

        etag = response.headers.get('ETag')
        last_modified = response.headers.get('Last-Modified')
        cache_control = response.headers.get('Cache-Control', '')

        if etag:
            entry['etag'] = etag
        else:
            entry.pop('etag', None)

        if last_modified:
            entry['last_modified'] = last_modified

        max_age = None
        for part in cache_control.split(','):
            part = part.strip()
            if part.startswith('max-age='):
                try:
                    max_age = int(part[8:])
                except ValueError:
                    pass

        if max_age and max_age > 0:
            entry['skip_until'] = time.time() + max_age
        else:
            entry.pop('skip_until', None)

        self._data[url] = entry

    # --- Failure memory ------------------------------------------------
    #
    # A feed that fails does so for one of three reasons, and they want very
    # different treatment: a transient blip is worth retrying immediately, a
    # bot-block is worth retrying with a different identity, and a dead
    # domain is worth not retrying at all. Without memory across runs every
    # failure looks transient, so a permanently dead feed burns a Brave and a
    # Kagi call on every run forever. Tracking consecutive failures lets the
    # caller escalate: retry, then stop paying, then stop polling.

    # Beyond this many consecutive failures, a feed stops being worth paid
    # search fallbacks — the free ones still run.
    PAID_FALLBACK_FAILURE_LIMIT = 3

    # Escalating poll backoff for failures that cannot resolve themselves
    # (dead DNS, feed permanently gone). Keyed by consecutive-failure count,
    # applied as the largest threshold met.
    _BACKOFF_LADDER = ((8, 72 * 3600), (4, 24 * 3600), (2, 6 * 3600))

    def record_failure(self, url: str, kind: str) -> int:
        """Note a failed fetch. Returns the new consecutive-failure count."""
        entry = self._data.get(url, {})
        entry['failures'] = entry.get('failures', 0) + 1
        entry['failure_kind'] = kind
        entry['last_failure'] = time.time()
        # A count alone cannot distinguish "failed 4 times in one bad afternoon"
        # from "failed every run for a week". Retirement decisions need the
        # latter, so remember when the current failure streak started.
        entry.setdefault('first_failure', entry['last_failure'])
        self._data[url] = entry
        return entry['failures']

    def record_success(self, url: str) -> None:
        """Clear failure state after any fetch that produced a usable feed."""
        entry = self._data.get(url)
        if not entry:
            return
        for key in ('failures', 'failure_kind', 'last_failure', 'first_failure'):
            entry.pop(key, None)

    def entry(self, url: str) -> dict:
        """Read-only view of one feed's cached state ({} if untracked)."""
        return dict(self._data.get(url, {}))

    def failure_age_days(self, url: str) -> float:
        """Days since the current failure streak began (0.0 if not failing).

        Falls back to last_failure for entries written before first_failure
        was tracked, which reads as a brand-new streak — deliberately
        conservative, since it can only delay a retirement, never rush one.
        """
        entry = self._data.get(url, {})
        if not entry.get('failures'):
            return 0.0
        started = entry.get('first_failure') or entry.get('last_failure')
        if not started:
            return 0.0
        return max(0.0, (time.time() - started) / 86400)

    def prune_to(self, known_urls) -> int:
        """Drop state for feeds no longer in the OPML. Returns entries removed.

        Entries are keyed on the OPML URL, so a feed that is renamed, retired,
        or relocated by the health agent leaves its old key behind. Without
        this the file grows forever and, worse, a feed restored under its old
        URL would inherit a stale failure streak it never earned.
        """
        known = set(known_urls)
        stale = [url for url in self._data if url not in known]
        for url in stale:
            del self._data[url]
        return len(stale)

    def failure_count(self, url: str) -> int:
        return self._data.get(url, {}).get('failures', 0)

    def should_skip_paid_fallback(self, url: str) -> bool:
        """True once a feed has failed often enough that paid search is waste."""
        return self.failure_count(url) >= self.PAID_FALLBACK_FAILURE_LIMIT

    def set_failure_backoff(self, url: str) -> Optional[int]:
        """Back off polling a feed whose failure cannot resolve on its own.

        Returns the backoff in seconds, or None if the feed has not failed
        enough times to earn one yet.
        """
        failures = self.failure_count(url)
        for threshold, seconds in self._BACKOFF_LADDER:
            if failures >= threshold:
                entry = self._data.get(url, {})
                entry['skip_until'] = time.time() + seconds
                self._data[url] = entry
                return seconds
        return None

    # --- Rediscovered feed URLs -----------------------------------------
    #
    # When autodiscovery finds a feed's new home, remember it here rather
    # than rewriting feeds.opml: the OPML is user-curated (and rewritten by
    # integrate_discoveries.py), while this cache is committed by CI after
    # every run, so the redirect survives without touching curated state.

    def set_resolved_url(self, url: str, resolved: str) -> None:
        entry = self._data.get(url, {})
        entry['resolved_url'] = resolved
        entry['resolved_at'] = time.time()
        # ETag/Last-Modified describe whichever URL we last fetched. Pointing
        # the feed at a different one invalidates them: a stale validator can
        # draw a 304 that we would read as "no new articles" indefinitely.
        entry.pop('etag', None)
        entry.pop('last_modified', None)
        self._data[url] = entry

    def resolved_url(self, url: str) -> Optional[str]:
        resolved = self._data.get(url, {}).get('resolved_url')
        return resolved if resolved and resolved != url else None

    def clear_resolved_url(self, url: str) -> None:
        """Forget a rediscovered URL that has itself stopped working."""
        entry = self._data.get(url)
        if entry:
            for key in ('resolved_url', 'resolved_at', 'etag', 'last_modified'):
                entry.pop(key, None)

    def set_retry_after(self, url: str, retry_after: str) -> None:
        """Parse a Retry-After header (seconds or HTTP-date) and store skip_until."""
        entry = self._data.get(url, {})
        try:
            entry['skip_until'] = time.time() + int(retry_after)
        except ValueError:
            try:
                entry['skip_until'] = parsedate_to_datetime(retry_after).timestamp()
            except Exception:
                pass
        self._data[url] = entry
