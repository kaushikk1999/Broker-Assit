# Phase 0 — Research Permissions Matrix

_Owner decision (2026-06-23): research scope = **Public web + screenshots**. No logins, no paid/licensed
tools. App-only or login-gated features remain scored "Not verified" in the feature matrix._

| Research Item | Allowed | Notes |
|---|---|---|
| Public website research | ✅ Yes | Marketing sites, help centers, docs, blog/case studies, app-store listings. |
| Login-based research | ❌ No | Do not create/use accounts. Login-gated chatbot, in-app assistant, and account-opening flows stay "Not verified". |
| Screenshot capture | ✅ Yes (public pages only) | Capture public pages/help-center/app-store screenshots for the findings log (#20). Store under `deliverables/phase_0/screenshots/`. |
| Pricing page review | ✅ Yes | Public pricing pages of AI platforms (Intercom/Fin outcome-based, etc.). |
| Account-opening flow review | ⚠️ Public-info only | Only what is publicly documented; do not actually open accounts. |
| Paid tools / licensed tools | ❌ No | No paid competitive-intelligence tools or paid datasets. |
| Internal documentation access | ✅ Owner-provided only | Roadmap, CSVs, NSE/NALCO reference files provided in the workspace. |
| Mobile browser testing | ⚠️ Public-only | Public mobile web pages; native-app behavior behind login stays "Not verified". |

## Methodology constraints
- Use the 0–5 rubric from `feature_matrix.csv`; never guess — unverified = "Not verified".
- Cite the source (URL + date accessed) and a confidence level for every claim.
- Vendor-claimed metrics (e.g., "80% autonomous resolution") flagged as vendor-reported.
- Respect each site's Terms of Service and `robots.txt`; no scraping behind auth.
