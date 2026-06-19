import json
import time


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
