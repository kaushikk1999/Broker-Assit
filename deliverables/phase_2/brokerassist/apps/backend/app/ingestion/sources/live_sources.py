"""Live source adapters (opt-in) — real crawl / NSE / BSE / NALCO IR / Google Drive.

These are gated behind ``BA_INGEST_LIVE=true`` and require per-source configuration (URLs / Drive
credentials). They are deliberately NOT exercised on the default mocks-first path: with the flag off,
``base.get_source`` never constructs them, so CI stays credential- and network-free.

NSE and BSE corporate filings are fetched from each exchange's official JSON endpoint (roadmap p. 13:
"Official APIs where available"). No browser/Playwright is needed — both return structured JSON — which
keeps the live path lean and matches the no-heavy-deps spirit of the base image. Filings are KNOWLEDGE
documents: they flow discover -> parse -> registry -> chunk -> embed -> Qdrant. They are NOT market data
(market data stays on the separate cached, non-Qdrant Market Service branch).

The remaining adapters (broker site / NALCO IR / Google Drive) are still thin seams: they raise a clear
NotImplementedError until wired, so enabling them is an explicit, localized change."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime

from app.config import settings
from app.core.observability import log
from app.ingestion.base import IngestionSource, RawDocument

# A real browser UA + Accept header is enough to clear NSE/BSE's basic bot filter; some NSE symbol
# queries also need session cookies, which we seed by hitting the site root first (see _nse_client).
_BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}
# Cap how many filings we pull per source on a single pass (keeps a test run fast and bounded).
_MAX_ITEMS = 30


class LiveSourceNotConfigured(RuntimeError):
    """A live source is enabled (BA_INGEST_LIVE) but its endpoint/credentials are missing."""


class _BaseLiveSource(IngestionSource):
    mode = "live"
    endpoint_setting = ""   # which settings attr must be non-empty
    human_name = ""

    def __init__(self, name: str):
        self.name = name

    def _require_endpoint(self) -> str:
        value = getattr(settings, self.endpoint_setting, "") if self.endpoint_setting else ""
        if not value:
            raise LiveSourceNotConfigured(
                f"{self.human_name}: set BA_{self.endpoint_setting.upper()} to enable live ingestion")
        return value

    def discover(self) -> list[RawDocument]:  # pragma: no cover - real network, off by default
        endpoint = self._require_endpoint()
        raise NotImplementedError(
            f"{self.human_name} live fetch from {endpoint!r} is not wired yet — implement the real "
            f"crawler/API call here. Until then run with BA_INGEST_LIVE=false (fixtures).")


_LI_RE = re.compile(r"<li[^>]*>(.*?)</li>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_YEAR_RE = re.compile(r"20\d\d")
_DMY_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")


def _extract_dated_items(html: str) -> list[str]:
    """Pull list items that look like real dated notices (skip short nav/menu entries). Each becomes
    one knowledge document. Strips tags, collapses whitespace, drops &nbsp; padding."""
    out: list[str] = []
    for raw in _LI_RE.findall(html or ""):
        text = _WS_RE.sub(" ", _TAG_RE.sub(" ", raw)).replace("\xa0", " ").strip(" |")
        text = _WS_RE.sub(" ", text).strip()
        if len(text) > 30 and _YEAR_RE.search(text):
            out.append(text[:600])
    return out


def _first_date(text: str) -> date | None:
    m = _DMY_RE.search(text or "")
    return _parse_exchange_date(m.group(1)) if m else None


def _parse_exchange_date(value) -> date | None:
    """Parse the date strings the exchanges return ('26-Jun-2026 12:08:00', '26 Jun 2026', ISO...)."""
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%d-%b-%Y %H:%M:%S", "%d-%b-%Y", "%d %b %Y", "%d/%m/%Y", "%d-%m-%Y",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


# --------------------------------------------------------------------------- NSE corporate filings
class NseLive(_BaseLiveSource):
    """NSE corporate announcements via the official JSON API. Pulls the fresh general equities feed
    plus a NALCO-symbol query (pilot focus), de-duplicated. Each announcement becomes one knowledge
    document; ``attchmntText`` is the human-readable filing summary used as content."""
    endpoint_setting = "nse_base_url"
    human_name = "NSE corporate filings"

    def _client(self):
        import httpx  # lazy import — only needed on the live path

        base = self._require_endpoint().rstrip("/")
        c = httpx.Client(headers={**_BROWSER_HEADERS, "Referer": f"{base}/"},
                         timeout=settings.embedding_timeout_seconds, follow_redirects=True)
        try:  # seed session cookies the way a browser would (symbol queries 403 without them)
            c.get(f"{base}/")
            c.get(f"{base}/get-quotes/equity?symbol=NALCO")
        except Exception as e:  # non-fatal — the general feed often works cookie-less
            log.warning("NSE cookie seed failed (continuing): %s", e)
        return base, c

    def discover(self) -> list[RawDocument]:
        base, client = self._client()
        seen: set[str] = set()
        docs: list[RawDocument] = []
        endpoints = [
            f"{base}/api/corporate-announcements?index=equities",              # fresh, all equities
            f"{base}/api/corporate-announcements?index=equities&symbol=NALCO",  # pilot
        ]
        try:
            for url in endpoints:
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                    rows = resp.json()
                except Exception as e:  # one endpoint failing must not sink the rest
                    log.warning("NSE fetch failed (%s): %s", url, e)
                    continue
                rows = rows if isinstance(rows, list) else rows.get("data", [])
                for row in rows:
                    doc = self._to_doc(row)
                    if doc is None:
                        continue
                    key = (row.get("seq_id") or doc.url or doc.title)
                    if key in seen:
                        continue
                    seen.add(key)
                    docs.append(doc)
                    if len(docs) >= _MAX_ITEMS:
                        break
                if len(docs) >= _MAX_ITEMS:
                    break
        finally:
            client.close()
        log.info("NSE live discover: %d announcement(s)", len(docs))
        return docs

    @staticmethod
    def _to_doc(row: dict) -> RawDocument | None:
        symbol = (row.get("symbol") or "").strip()
        desc = (row.get("desc") or "").strip()
        text = (row.get("attchmntText") or "").strip()
        company_name = (row.get("sm_name") or "").strip()
        body = " ".join(p for p in (company_name, desc, text) if p).strip()
        if not body:
            return None
        # Prefer the filing's own PDF URL; else synthesize a unique one (registry dedups on source+url,
        # so a constant fallback would collapse multiple filings into one document).
        seq = str(row.get("seq_id") or hashlib.md5(body.encode("utf-8")).hexdigest()[:10])
        url = (row.get("attchmntFile") or "").strip() or (
            f"https://www.nseindia.com/companies-listing/corporate-filings-announcements#{seq}")
        return RawDocument(
            source="nse",
            url=url,
            title=f"{symbol or company_name}: {desc}".strip(": ").strip(),
            content=body,
            content_type="text/plain",
            filing_type=desc,                       # canonicalized downstream by metadata.extract
            filing_date=_parse_exchange_date(row.get("an_dt") or row.get("sort_date")),
            company=symbol or company_name,         # NSE ticker (e.g. "NALCO") -> RAG company filter
            lang="en",
        )


# --------------------------------------------------------------------------- BSE corporate filings
class BseLive(_BaseLiveSource):
    """BSE corporate announcements via a Playwright browser context (roadmap-recommended tool for
    anti-bot pages). A real browser is used so the AnnGetData API call carries authentic cookies.

    NOTE: BSE fronts its site with Akamai Bot Manager, which blocks datacenter / non-IN IPs at the edge
    ("You don't have permission to access ... edgesuite.net") regardless of the browser. When that
    happens (or Playwright is absent) we log and return [] — the run never fails, and the same code
    works unchanged from an allow-listed IP or residential proxy."""
    endpoint_setting = "bse_base_url"
    human_name = "BSE filings"
    _API = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"

    def discover(self) -> list[RawDocument]:
        try:
            from playwright.sync_api import sync_playwright  # lazy — only on the live path
        except ImportError:
            log.warning("BSE live needs Playwright (pip install -r requirements-ingest.txt); 0 docs")
            return []

        base = self._require_endpoint().rstrip("/")
        today = date.today()
        query = (f"?pageno=1&strCat=-1&strPrevDate={today.replace(month=1, day=1):%Y%m%d}"
                 f"&strScrip=&strSearch=P&strToDate={today:%Y%m%d}&strType=C")
        rows: list = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(user_agent=_BROWSER_HEADERS["User-Agent"])
                page = ctx.new_page()
                page.goto(f"{base}/corporates/ann.html", timeout=45000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)  # let the edge set cookies / JS settle
                resp = ctx.request.get(self._API + query,
                                       headers={"Referer": f"{base}/", "Accept": "application/json"})
                if resp.ok:
                    data = resp.json()
                    rows = data.get("Table", []) if isinstance(data, dict) else []
                browser.close()
        except Exception as e:
            log.warning("BSE Playwright fetch failed (continuing with 0 docs): %s", e)
            return []
        if not rows:
            log.info("BSE live discover: 0 records (Akamai edge blocks this IP; works from an "
                     "allow-listed IP / residential proxy)")
            return []
        docs = [d for d in (self._to_doc(r) for r in rows[:_MAX_ITEMS]) if d is not None]
        log.info("BSE live discover: %d announcement(s)", len(docs))
        return docs

    @staticmethod
    def _to_doc(row: dict) -> RawDocument | None:
        headline = (row.get("HEADLINE") or row.get("NEWSSUB") or "").strip()
        company_name = (row.get("SLONGNAME") or row.get("SCRIP_NAME") or "").strip()
        category = (row.get("CATEGORYNAME") or row.get("NEWS_SUBCAT") or "").strip()
        body = " ".join(p for p in (company_name, category, headline) if p).strip()
        if not body:
            return None
        scrip = str(row.get("SCRIP_CD") or "").strip()
        return RawDocument(
            source="bse",
            url=(row.get("ATTACHMENTNAME") and f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{row['ATTACHMENTNAME']}")
                or "https://www.bseindia.com/corporates/ann.html",
            title=f"{company_name}: {headline}".strip(": ").strip()[:300],
            content=body,
            content_type="text/plain",
            filing_type=category or headline,
            filing_date=_parse_exchange_date(row.get("NEWS_DT") or row.get("DT_TM")),
            company=company_name,
            lang="en",
        )


class BrokerSiteLive(_BaseLiveSource):
    endpoint_setting = "broker_site_url"
    human_name = "Broker website crawler"


class NalcoIrLive(_BaseLiveSource):
    """NALCO Investor Relations (nalcoindia.com). The IR pages are server-rendered, so a plain HTTPS
    fetch returns the full HTML (no browser needed); we extract the dated notice/list items as knowledge
    documents tagged company=NALCO. Playwright stays available for sources that need JS rendering."""
    endpoint_setting = "nalco_ir_url"
    human_name = "NALCO Investor Relations"
    # IR sub-pages worth crawling (press releases, results, annual reports, shareholder notices).
    _PAGES = (
        "/investor-services/press-release/",
        "/investor-services/financial-results/",
        "/investor-services/annual-reports/",
        "/investor-services/shareholders-information/",
    )

    def discover(self) -> list[RawDocument]:
        import httpx  # lazy import — only needed on the live path

        base = self._require_endpoint().rstrip("/")
        headers = {"User-Agent": _BROWSER_HEADERS["User-Agent"]}
        seen: set[str] = set()
        docs: list[RawDocument] = []
        with httpx.Client(headers=headers, timeout=settings.embedding_timeout_seconds,
                          follow_redirects=True) as client:
            for path in self._PAGES:
                try:
                    resp = client.get(base + path)
                    resp.raise_for_status()
                except Exception as e:  # one page failing must not sink the rest
                    log.warning("NALCO IR fetch failed (%s): %s", path, e)
                    continue
                for item in _extract_dated_items(resp.text):
                    key = item[:80].lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    # Each list item is its own logical document, so it needs a unique URL (the registry
                    # dedups on source+url). A stable content fragment keeps re-runs idempotent.
                    frag = hashlib.md5(item.encode("utf-8")).hexdigest()[:10]
                    docs.append(RawDocument(
                        source="nalco_ir", url=f"{base}{path}#{frag}",
                        title=item[:120], content=f"NALCO {item}", content_type="text/plain",
                        filing_type="", filing_date=_first_date(item), company="NALCO", lang="en"))
                    if len(docs) >= _MAX_ITEMS:
                        break
                if len(docs) >= _MAX_ITEMS:
                    break
        log.info("NALCO IR live discover: %d item(s)", len(docs))
        return docs


class GDriveLive(_BaseLiveSource):
    endpoint_setting = "gdrive_folder_id"
    human_name = "Google Drive knowledge repository"


_LIVE = {
    "broker_site": BrokerSiteLive,
    "nse": NseLive,
    "bse": BseLive,
    "nalco_ir": NalcoIrLive,
    "gdrive": GDriveLive,
}


def get_live_source(name: str) -> IngestionSource:
    cls = _LIVE.get(name)
    if cls is None:
        raise ValueError(f"no live adapter for source {name!r}")
    return cls(name)
