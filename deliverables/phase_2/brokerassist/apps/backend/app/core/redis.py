"""Redis layer: session cache, chat context, rate-limit/quota counters.

Real Redis when BA_REDIS_URL is set and reachable; otherwise a process-local in-memory fallback with
the same interface (so dev/tests run with zero infra). Counters use atomic INCR + EXPIRE on first hit."""
from __future__ import annotations
import json
import time
import threading

from app.config import settings

NS = "ba"  # namespace prefix → ba:ratelimit:..., ba:quota:..., ba:session:..., ba:chatctx:...


def k(*parts: str) -> str:
    return ":".join([NS, *parts])


class _MemoryBackend:
    """In-memory stand-in. Not durable, not shared across processes — dev/test only."""
    name = "memory"

    def __init__(self) -> None:
        self._v: dict[str, tuple[str, float | None]] = {}
        self._counts: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def _expired(self, exp: float | None) -> bool:
        return exp is not None and exp < time.time()

    def incr(self, key: str, ttl: int) -> int:
        with self._lock:
            now = time.time()
            val, exp = self._counts.get(key, (0, now + ttl))
            if exp < now:
                val, exp = 0, now + ttl
            val += 1
            self._counts[key] = (val, exp)
            return val

    def set_json(self, key: str, obj, ttl: int | None = None) -> None:
        with self._lock:
            self._v[key] = (json.dumps(obj), (time.time() + ttl) if ttl else None)

    def get_json(self, key: str):
        with self._lock:
            hit = self._v.get(key)
            if not hit or self._expired(hit[1]):
                self._v.pop(key, None)
                return None
            return json.loads(hit[0])

    def delete(self, key: str) -> None:
        with self._lock:
            self._v.pop(key, None)
            self._counts.pop(key, None)

    def ping(self) -> bool:
        return True


class _RedisBackend:
    name = "redis"

    def __init__(self, client) -> None:
        self._r = client

    def incr(self, key: str, ttl: int) -> int:
        pipe = self._r.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        val, cur_ttl = pipe.execute()
        if cur_ttl is None or cur_ttl < 0:  # first hit (or no expiry yet) → set the window
            self._r.expire(key, ttl)
        return int(val)

    def set_json(self, key: str, obj, ttl: int | None = None) -> None:
        self._r.set(key, json.dumps(obj), ex=ttl)

    def get_json(self, key: str):
        raw = self._r.get(key)
        return json.loads(raw) if raw else None

    def delete(self, key: str) -> None:
        self._r.delete(key)

    def ping(self) -> bool:
        try:
            return bool(self._r.ping())
        except Exception:
            return False


def _build_backend():
    if settings.redis_url:
        try:
            import redis  # imported lazily so the dep is optional in dev
            client = redis.Redis.from_url(settings.redis_url, decode_responses=True,
                                          socket_connect_timeout=2)
            client.ping()
            return _RedisBackend(client)
        except Exception as e:  # unreachable → fall back, don't crash the app
            print(f"[redis] BA_REDIS_URL set but unreachable ({e}); using in-memory fallback")
    return _MemoryBackend()


cache = _build_backend()
