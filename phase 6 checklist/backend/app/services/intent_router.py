"""Intent classification + routing fork (roadmap Phase 6). Market-data intents go to the Market
Service (Redis-cached); only knowledge intents enter the RAG pipeline."""
import re

_MARKET_KEYWORDS = ("ltp", "price", "quote", "ohlc", "market depth", "option chain",
                    "trading at", "share price", "stock price", "last traded")
_KNOWN_SYMBOLS = {"NALCO", "TCS", "INFY", "RELIANCE", "HDFCBANK", "SBIN"}


def classify(message: str) -> dict:
    low = message.lower()
    is_market = any(k in low for k in _MARKET_KEYWORDS)
    symbol = None
    for tok in re.findall(r"[A-Za-z]{3,12}", message):
        if tok.upper() in _KNOWN_SYMBOLS:
            symbol = tok.upper()
            break
    if is_market and symbol:
        return {"branch": "market", "intent": "market_data", "symbol": symbol}
    # Knowledge sub-intents (for analytics/filters; all route to RAG).
    if "dividend" in low:
        intent = "filing_dividend"
    elif "algo" in low or "black box" in low or "white box" in low:
        intent = "algo_education"
    elif "board" in low:
        intent = "filing_board"
    else:
        intent = "knowledge_general"
    return {"branch": "knowledge", "intent": intent, "symbol": symbol}
