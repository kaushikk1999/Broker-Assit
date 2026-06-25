"""Branch A — Market Data Service. Reads from a MarketDataProvider, caches in Redis (in-memory
fallback). These requests never touch Qdrant and never enter the RAG pipeline."""
import time

from app.adapters import get_marketdata, get_language

# Tiny TTL cache standing in for Redis (key -> (value, expires_at)).
_cache: dict[str, tuple[dict, float]] = {}
_TTL = 5.0


def _cached(key: str):
    hit = _cache.get(key)
    if hit and hit[1] > time.time():
        return hit[0]
    return None


def handle_market(symbol: str, user_lang: str) -> dict:
    provider = get_marketdata()
    key = f"ltp:{symbol}"
    data = _cached(key)
    cache_hit = data is not None
    if not data:
        data = provider.get_ltp(symbol)
        _cache[key] = (data, time.time() + _TTL)

    answer_en = f"{data['symbol']} is trading at {data['ltp']} {data['currency']} (last traded price)."
    answer = get_language().translate(answer_en, target=user_lang) if user_lang != "en" else answer_en
    return {
        "answer": answer,
        "data": data,
        "cache_hit": cache_hit,
    }
