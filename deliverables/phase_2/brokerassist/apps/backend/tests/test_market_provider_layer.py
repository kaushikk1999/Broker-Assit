"""Phase 4 — Market Data Provider Layer completion (Source 2A). The full roadmap interface (LTP, OHLC,
market depth, option chain, tick subscription) is implemented by the mock and resolves via the factory.
Market data never enters Qdrant — this is a cached, non-vector branch."""
from app.adapters import get_marketdata
from app.adapters.base import MarketDataProvider
from app.adapters.mocks import MockMarketData


def test_factory_returns_provider_implementing_full_interface():
    provider = get_marketdata()
    assert isinstance(provider, MarketDataProvider)
    for method in ("get_ltp", "get_ohlc", "get_market_depth", "get_option_chain", "subscribe_ticks"):
        assert callable(getattr(provider, method))


def test_ltp_and_ohlc_are_deterministic():
    p = MockMarketData()
    assert p.get_ltp("NALCO") == p.get_ltp("NALCO")
    ohlc = p.get_ohlc("NALCO")
    assert ohlc["low"] <= ohlc["open"] <= ohlc["high"]


def test_market_depth_has_five_levels_each_side():
    depth = MockMarketData().get_market_depth("NALCO")
    assert len(depth["bids"]) == 5 and len(depth["asks"]) == 5
    assert depth["bids"][0]["price"] < depth["asks"][0]["price"]   # spread is non-crossed


def test_option_chain_is_centred_on_the_underlying():
    chain = MockMarketData().get_option_chain("NALCO")
    strikes = [s["strike"] for s in chain["strikes"]]
    assert len(strikes) == 5 and strikes == sorted(strikes)
    assert min(strikes) <= chain["underlying"] <= max(strikes)


def test_subscribe_ticks_returns_requested_count():
    ticks = MockMarketData().subscribe_ticks("NALCO", count=3)
    assert len(ticks) == 3 and [t["seq"] for t in ticks] == [0, 1, 2]
