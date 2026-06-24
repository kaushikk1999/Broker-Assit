"""Create tables (dev) and seed demo data. Idempotent; safe on every startup.

Production uses Alembic migrations instead of create_all (see alembic/). Tests use create_all."""
import hashlib
import os
from datetime import date

from app.db.base import Base, engine, SessionLocal
from app.db import models
from app.core.security import hash_api_key, key_prefix
from app.core.admin_security import hash_password


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


DEMO_WIDGET_KEY = "demo-public-key"
DEMO_DOMAINS = ["localhost", "127.0.0.1", "localhost:3000", "localhost:8123"]
ADMIN_EMAIL = "admin@brokerassist.local"

KB = [
    ("NALCO_IR", "NALCO Q4 FY25 Financial Results", "https://nalcoindia.com/investor/results",
     "Financial Results", date(2025, 5, 15),
     "NALCO reported higher revenue this quarter, led by stronger alumina realisations. "
     "Net profit rose versus the prior quarter."),
    ("NSE", "NALCO Board Meeting Outcome", "https://www.nseindia.com/corporate/NALCO",
     "Board Meeting", date(2025, 5, 15),
     "The NALCO board approved the audited financial results and recommended a final dividend "
     "for the financial year, subject to shareholder approval at the AGM."),
    ("NALCO_IR", "NALCO Dividend History", "https://nalcoindia.com/investor/dividend",
     "Dividend", date(2025, 5, 16),
     "NALCO has a consistent dividend track record, paying interim and final dividends in recent "
     "years. The latest recommended dividend is subject to AGM approval."),
    ("ALGO", "NSE retail algo: white-box vs black-box", "https://www.nseindia.com/algo-faq",
     "FAQ", date(2025, 9, 19),
     "A white-box algo discloses its logic to the user; a black-box algo does not. Under SEBI/NSE "
     "rules, black-box providers must register as Research Analysts and algos must be hosted on the "
     "broker's server."),
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Tenant + normalized api_key + domain allowlist
        tenant = db.query(models.Tenant).filter_by(name="Demo Brokerage").first()
        if not tenant:
            tenant = models.Tenant(name="Demo Brokerage", daily_quota=5000)
            db.add(tenant); db.flush()
            db.add(models.ApiKey(tenant_id=tenant.id, key_prefix=key_prefix(DEMO_WIDGET_KEY),
                                 key_hash=hash_api_key(DEMO_WIDGET_KEY), status="active"))
            for d in DEMO_DOMAINS:
                db.add(models.DomainAllowlist(tenant_id=tenant.id, domain=d))
            db.commit()

        # Superadmin user
        if not db.query(models.User).filter_by(email=ADMIN_EMAIL).first():
            pw = os.environ.get("BA_ADMIN_SEED_PASSWORD", "admin12345")
            db.add(models.User(email=ADMIN_EMAIL, password_hash=hash_password(pw), role="superadmin"))
            db.commit()

        # NALCO knowledge base + version/audit rows
        if db.query(models.Document).count() == 0:
            for source, title, url, ftype, fdate, txt in KB:
                doc = models.Document(source=source, title=title, url=url, filing_type=ftype,
                                      filing_date=fdate, company="NALCO" if "NALCO" in title else "",
                                      checksum=_checksum(txt))
                db.add(doc); db.flush()
                db.add(models.DocumentChunk(document_id=doc.id, chunk_index=0, text=txt, lang="en"))
                db.add(models.DocumentVersion(document_id=doc.id, version=1, checksum=_checksum(txt),
                                              change_note="initial"))
                db.add(models.DocumentAuditHistory(document_id=doc.id, action="registered",
                                                   actor="seed", detail={"title": title}))
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seeded demo tenant + api key + allowlist + admin user + NALCO knowledge base.")
