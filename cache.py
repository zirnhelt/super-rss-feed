import json
import time
from email.utils import parsedate_to_datetime


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
