# Primary Source Document Gaps

**Updated:** 2026-08-25  
**Coverage:** 47 of 50 states have at least one verified primary source PDF

---

## Overview

An automated harvesting effort was run to collect official primary source documents (collective bargaining agreements, pay plans, salary schedules) for all 50 states. The scripts used:

1. **`harvest_contracts.py`** — Direct download via `curl_cffi` with Chromium impersonation, targeting known official URLs for each state.
2. **`harvest_advanced.py`** — Playwright headless browser fallback for portal scraping.
3. **`search_pdfs.py`** — DuckDuckGo search → PDF download fallback for states that failed above.
4. **`download_missing_playwright.py`** — Playwright-powered download of search results.

Despite multiple automated passes, **4 states** could not have their documents automatically retrieved:

---

## States Missing Primary Source PDFs

### Massachusetts (MA)
- **Bargaining Unit:** MCOFU — Massachusetts Correction Officers Federated Union (Unit 4)
- **Why blocked:** The MCOFU collective bargaining agreement is only accessible via the union's member portal. The state's Mass.gov collective bargaining page links to it, but the download itself requires a login.
- **Manual fix:** Visit [mass.gov/lists/current-collective-bargaining-agreements](https://www.mass.gov/lists/current-collective-bargaining-agreements) or contact MCOFU directly at (774) 396-6477.
- **Note:** The state profile `states/MA_massachusetts.md` contains verified salary data sourced from the MCOFU pay matrix (top-out ~$41.22/hr / $85,730/yr).

---

### New Hampshire (NH)
- **Bargaining Unit:** SEA / SEIU Local 1984 (Corrections Sub-Unit)
- **Why blocked:** The NH Department of Administrative Services (`das.nh.gov`) returns HTTP 403 Forbidden to all automated requests, including Playwright-based browser simulation.
- **Manual fix:** Visit [das.nh.gov/hr/agreements.aspx](https://das.nh.gov/hr/agreements.aspx) and navigate to "SEA/SEIU Local 1984 → Corrections Sub-Unit" to download the 2023–2025 agreement PDF.
- **Contract details:** The agreement covering corrections staff runs July 1, 2023 – June 30, 2025.

---

### Tennessee (TN)
- **Bargaining Unit:** Non-Union — TDOC; public sector collective bargaining is prohibited by TN Code § 49-5-610.
- **Why blocked:** Tennessee's `tn.gov` resets connections to automated requests. The pay plan PDF URL returns a connection reset error — the file may have been moved or removed.
- **Manual fix:** Visit [tn.gov/hr/employees/compensation.html](https://www.tn.gov/hr/employees/compensation.html) — the pay plan may be available as an interactive page or via a state employee portal.
- **Key data point:** As of February 2025, entry-level TDOC correctional officer salary is **$51,204/year**, rising to **$60,720** after 18 months, plus a $5,000 sign-on bonus.

---

### Wisconsin (WI)
- **Bargaining Unit:** Non-Union — WI DOC / DPM; collective bargaining for most state employees was eliminated by **Act 10 (2011)**.
- **Why blocked:** Both `dpm.wi.gov` and `doc.wi.gov` completely drop TCP connections from cloud server IP ranges.
- **Manual fix:** Visit [dpm.wi.gov/Pages/HR_Admin/CompBenefits.aspx](https://dpm.wi.gov/Pages/HR_Admin/CompBenefits.aspx) for the 2025–2027 State Compensation Plan, or [doc.wi.gov/Pages/Careers/SecurityCareer.aspx](https://doc.wi.gov/Pages/Careers/SecurityCareer.aspx) for the "2025 Correctional Officer Pay & Benefits" PDF.
- **Key data point:** WI correctional officers receive base pay **plus $4.00/hour** add-on for all hours in pay status, plus shift differentials ($0.80/hr nights, $0.80/hr weekends).

---

## Summary Table

| State | Union Status | Document Type Needed | Blocker |
|:---:|:---|:---|:---|
| **MA** | Unionized (MCOFU Unit 4) | Collective Bargaining Agreement | Member-only login portal |
| **NH** | Unionized (SEA/SEIU 1984) | Collective Bargaining Agreement | HTTP 403 — server blocks automated requests |
| **TN** | Non-Union (prohibited by statute) | State Pay Plan PDF | Connection reset — PDF may no longer be publicly hosted |
| **WI** | Non-Union (Act 10 eliminated CBA) | State Compensation Plan | IP-range block on cloud servers |

> **Note:** For all four states, salary and benefits data is still documented in the corresponding state markdown profiles under `states/`. Only the PDF source document is missing — not the data itself.

---

## What We Do Have

**47 of 50 states** have at least one verified primary source document in their `states/XX/` directory, including:

- Full collective bargaining agreements (PDF) for all major unionized states (CA CCPOA, NY NYSCOPBA, PA PSCOA, FL PBA, OH OCSEA, MN AFSCME, NM AFSCME, VT VSEA, and more)
- Official state pay plans and salary schedules for all non-union states (TX, GA, NC, AZ, ID, IN, ND, WY, etc.)
- Legislative documents establishing non-union status where applicable (e.g., TX Gov't Code § 617.002, NC G.S. § 95-98)
