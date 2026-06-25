"""Intent classification + routing fork (roadmap Phase 6).

Market-data intents (Stock Query → LTP/OHLC/depth/option-chain) go to the Market Service
(Redis-cached, never Qdrant). Knowledge intents (Disclosure / Navigation / FAQ / Algo) enter the RAG
pipeline. Knowledge classification also derives a high-precision retrieval metadata filter (company),
applied AT retrieval on both Qdrant branches.

`filing_type` is intentionally NOT auto-derived here: the pilot corpus is small and filing-type
taxonomies overlap (e.g. "Quarterly Results" vs "Financial Results"), so an auto filing_type filter
would over-filter and drop the correct document. Explicit filters (e.g. the /filings module) are still
honored downstream."""
import re

_MARKET_KEYWORDS = ("ltp", "price", "quote", "ohlc", "market depth", "option chain",
                    "trading at", "share price", "stock price", "last traded")
_KNOWN_SYMBOLS = {"NALCO", "TCS", "INFY", "RELIANCE", "HDFCBANK", "SBIN"}

# Only the pilot company is auto-filtered: it is the one company actually present in the registry, so
# a company filter is high-precision. Other detected symbols are returned for analytics but not filtered
# (we have no documents for them → filtering would empty the candidate set).
_COMPANY_TERMS = ("nalco", "national aluminium")

_ALGO_TERMS = ("algo", "algos", "algorithmic", "black box", "white box", "black-box", "white-box")
_NAV_TERMS = ("navigate", "navigation", "where do i", "where can i", "how do i", "open an account",
              "open account", "sign up", "register", "website", "which page", "menu", "log in", "login")
_DISCLOSURE_TERMS = ("dividend", "result", "results", "earnings", "board", "filing", "filings",
                     "annual report", "disclosure", "shareholding", "financial", "quarterly")
_FAQ_STARTS = ("what", "how", "why", "when", "who", "explain", "tell", "is ", "are ", "can ", "does ")


def _detect_company(message: str) -> str | None:
    """Return the canonical pilot company if mentioned (Latin or English name), else None."""
    low = message.lower()
    if any(term in low for term in _COMPANY_TERMS):
        return "NALCO"
    for tok in re.findall(r"[A-Za-z]{3,12}", message):
        if tok.upper() == "NALCO":
            return "NALCO"
    return None


def _knowledge_intent(low: str) -> str:
    if any(t in low for t in _ALGO_TERMS):
        return "algo"
    if any(t in low for t in _NAV_TERMS):
        return "navigation"
    if any(t in low for t in _DISCLOSURE_TERMS):
        return "disclosure"
    if low.strip().endswith("?") or low.lstrip().startswith(_FAQ_STARTS):
        return "faq"
    return "knowledge_general"


def classify(message: str) -> dict:
    """Return {branch, intent, symbol, filters}. Market branch carries no RAG filters."""
    low = message.lower()
    is_market = any(k in low for k in _MARKET_KEYWORDS)
    symbol = None
    for tok in re.findall(r"[A-Za-z]{3,12}", message):
        if tok.upper() in _KNOWN_SYMBOLS:
            symbol = tok.upper()
            break
    if is_market and symbol:
        return {"branch": "market", "intent": "market_data", "symbol": symbol, "filters": None}

    company = _detect_company(message)
    filters: dict = {}
    if company:
        filters["company"] = company
    return {"branch": "knowledge", "intent": _knowledge_intent(low), "symbol": symbol,
            "filters": filters or None}
