"""Offline fixture corpus — realistic raw payloads for each source, used by the mock sources.

Each entry is a dict matching ``base.RawDocument`` fields. ``content`` is intentionally raw (HTML with
tags, or plain text) so the parsers do real work. Content is deterministic, so re-ingesting the same
corpus is idempotent (identical checksums => duplicates, no new chunks)."""
from __future__ import annotations

from datetime import date

# Source 1 — Broker website (HTML pages discovered via sitemap crawl). FAQ-type knowledge.
_BROKER = [
    {
        "url": "https://broker.example.com/faq/open-account",
        "title": "How do I open a Demat and trading account?",
        "content_type": "text/html",
        "filing_type": "FAQ",
        "content": (
            "<html><head><title>Open Account</title><style>.x{color:red}</style></head><body>"
            "<h1>How do I open a Demat account?</h1>"
            "<p>Opening an account is fully online. Keep your PAN, Aadhaar and a cancelled cheque ready.</p>"
            "<p>Complete e-KYC with an OTP, e-sign the form, and your account is usually active within "
            "24 hours.</p><script>track('faq')</script></body></html>"
        ),
    },
    {
        "url": "https://broker.example.com/pricing",
        "title": "Brokerage pricing and charges",
        "content_type": "text/html",
        "filing_type": "FAQ",
        "content": (
            "<html><body><h2>Pricing</h2><p>Equity delivery is brokerage-free. Intraday and F&O are "
            "charged a flat fee per executed order. Standard statutory charges such as STT, GST and "
            "exchange transaction charges apply.</p></body></html>"
        ),
    },
]

# Source 2B — NSE corporate filings (structured text). Knowledge documents -> registry -> chunks.
_NSE = [
    {
        "url": "https://www.nseindia.com/corporates/NALCO/board-outcome-q4fy25",
        "title": "NALCO Board Meeting Outcome — Q4 FY25",
        "content_type": "text/plain",
        "filing_type": "Board Meeting",
        "company": "NALCO",
        "filing_date": date(2025, 5, 15),
        "content": (
            "National Aluminium Company Limited — Outcome of Board Meeting. The Board of Directors "
            "approved the audited financial results for the quarter and year ended 31 March 2025 and "
            "recommended a final dividend, subject to shareholder approval at the ensuing AGM."
        ),
    },
    {
        "url": "https://www.nseindia.com/corporates/NALCO/quarterly-results-q4fy25",
        "title": "NALCO Quarterly Results Q4 FY25",
        "content_type": "text/plain",
        "filing_type": "Quarterly Results",
        "company": "NALCO",
        "filing_date": date(2025, 5, 15),
        "content": (
            "NALCO reported higher revenue for the quarter, led by stronger alumina realisations. "
            "Net profit rose versus the prior quarter on improved operating margins and steady "
            "production volumes."
        ),
    },
]

# Source 3 — BSE India (structured crawl). Corporate actions / disclosures.
_BSE = [
    {
        "url": "https://www.bseindia.com/corporates/NALCO/dividend-fy25",
        "title": "NALCO Final Dividend Record Date",
        "content_type": "text/plain",
        "filing_type": "Corporate Action",
        "company": "NALCO",
        "filing_date": date(2025, 7, 1),
        "content": (
            "NALCO has fixed the record date for the final dividend for FY25. Shareholders on the "
            "register as of the record date are eligible. The dividend is subject to AGM approval."
        ),
    },
]

# Source 4 — NALCO Investor Relations (website crawl). Annual reports, presentations.
_NALCO_IR = [
    {
        "url": "https://nalcoindia.com/investor/annual-report-fy25",
        "title": "NALCO Annual Report FY25 — Highlights",
        "content_type": "text/html",
        "filing_type": "Annual Report",
        "company": "NALCO",
        "filing_date": date(2025, 6, 30),
        "content": (
            "<html><body><h1>Annual Report FY25</h1><p>NALCO delivered resilient full-year performance "
            "with strong alumina exports and disciplined cost control.</p><p>The company continued "
            "investments in mining capacity and renewable power to support long-term growth.</p>"
            "</body></html>"
        ),
    },
    {
        "url": "https://nalcoindia.com/investor/q4fy25-presentation",
        "title": "NALCO Investor Presentation Q4 FY25",
        "content_type": "text/html",
        "filing_type": "Presentation",
        "company": "NALCO",
        "filing_date": date(2025, 5, 16),
        "content": (
            "<html><body><h2>Investor Presentation</h2><p>Key themes: alumina realisations, cost "
            "leadership, and capacity expansion. Outlook remains positive on stable demand.</p>"
            "</body></html>"
        ),
    },
]

# Source 5 — Google Drive knowledge repository (PDF/DOCX/PPTX/XLSX in production; markdown fixtures
# here). Brokerage FAQs, policies, research — including non-English knowledge to exercise EN/HI/TA.
_GDRIVE = [
    {
        "url": "gdrive://knowledge/algo-trading-basics.md",
        "title": "White-box vs black-box algorithms",
        "content_type": "text/markdown",
        "filing_type": "FAQ",
        "content": (
            "# Algo trading basics\n\nA white-box algo discloses its logic to the user; a black-box "
            "algo does not. Under SEBI/NSE rules, black-box providers must register as Research "
            "Analysts and algos must be hosted on the broker's server."
        ),
    },
    {
        "url": "gdrive://knowledge/kyc-hindi.md",
        "title": "खाता खोलने की प्रक्रिया",
        "content_type": "text/markdown",
        "filing_type": "FAQ",
        "lang": "hi",
        "content": (
            "# खाता खोलना\n\nखाता खोलना पूरी तरह ऑनलाइन है। पैन, आधार और एक रद्द किया हुआ चेक तैयार रखें। "
            "ओटीपी के साथ ई-केवाईसी पूरा करें।"
        ),
    },
]

FIXTURES: dict[str, list[dict]] = {
    "broker_site": _BROKER,
    "nse": _NSE,
    "bse": _BSE,
    "nalco_ir": _NALCO_IR,
    "gdrive": _GDRIVE,
}
