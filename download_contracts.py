import os
import sys
import time
import requests
from ddgs import DDGS
from curl_cffi import requests as c_requests
from rich.console import Console

console = Console()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATES_DIR = os.path.join(BASE_DIR, "states")

from state_data import STATES_DATA

# Known direct primary document links for high-priority benchmark states
DIRECT_CONTRACT_URLS = {
    "MN": [
        ("afscme_unit8_master_agreement.pdf", "https://mn.gov/mmb-stat/hr-toolbox/002-class-and-compensation/003-compensation/current-class-and-salary-range-report.pdf"),
        ("mmb_labor_relations_overview.html", "https://mn.gov/mmb/employee-relations/labor-relations/labor/"),
    ],
    "CA": [
        ("ccpoa_bu06_mou_contract.pdf", "https://www.calhr.ca.gov/labor-relations/Documents/mou-20230703-20260702-bu06.pdf"),
        ("calhr_pay_scale_section14.pdf", "https://www.calhr.ca.gov/Pay%20Scales%20Library/PS_Sec_14.pdf"),
    ],
    "TX": [
        ("tdcj_co_salary_schedule.html", "https://www.tdcj.texas.gov/divisions/hr/coinfo/cosalary.html"),
        ("tdcj_salary_schedule_c.html", "https://www.tdcj.texas.gov/divisions/hr/hr-home/salary.html"),
    ],
    "NY": [
        ("nyscopba_unit_agreement.pdf", "https://oer.ny.gov/system/files/documents/2023/11/nyscopba-contract-2023-2026.pdf"),
    ],
    "IL": [
        ("il_afscme_master_agreement.pdf", "https://cms.illinois.gov/content/dam/soi/en/web/cms/personnel/benefits/documents/afscme-contract.pdf"),
    ],
    "FL": [
        ("fl_pba_security_services_cba.pdf", "https://www.dms.myflorida.com/content/download/156477/1039864/Security_Services_Unit_2023-2026_Agreement.pdf"),
        ("fl_fdc_pay_plan.html", "https://www.fdc.myflorida.com/employment/careers/correctional-officer"),
    ],
    "MI": [
        ("mco_corrections_cba.pdf", "https://www.michigan.gov/mco/-/media/Project/Websites/mco/Documents/2022-2024-MCO-Contract.pdf"),
    ],
    "PA": [
        ("pscoa_h1_cba.pdf", "https://www.oa.pa.gov/Employees/Labor%20Relations/Documents/PSCOA%202023-2026.pdf"),
    ],
    "GA": [
        ("gdc_compensation_policy.html", "https://gdc.georgia.gov/careers/correctional-officer-career-path"),
    ],
    "AL": [
        ("adoc_salary_matrix.html", "http://doc.alabama.gov/Employment"),
    ]
}


def download_file(url: str, dest_path: str) -> bool:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        if url.endswith(".pdf") or "pdf" in url.lower():
            resp = c_requests.get(url, impersonate="chrome124", timeout=20)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(dest_path, "wb") as f:
                    f.write(resp.content)
                console.print(f"[green]✓ Downloaded PDF ({len(resp.content)//1024} KB): {os.path.basename(dest_path)}[/green]")
                return True
        else:
            resp = c_requests.get(url, impersonate="chrome124", timeout=15)
            if resp.status_code == 200:
                with open(dest_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(resp.text)
                console.print(f"[green]✓ Saved HTML ({len(resp.text)//1024} KB): {os.path.basename(dest_path)}[/green]")
                return True
    except Exception as e:
        console.print(f"[yellow]Failed to download {url}: {e}[/yellow]")
    return False


def discover_and_download_for_state(state_code: str, state_name: str, agency: str):
    state_dir = os.path.join(STATES_DIR, state_code)
    os.makedirs(state_dir, exist_ok=True)
    
    console.print(f"\n[bold blue]=== Harvesting Primary Documents: {state_name} ({state_code}) ===[/bold blue]")
    
    # 1. Download known direct links if available
    if state_code in DIRECT_CONTRACT_URLS:
        for filename, url in DIRECT_CONTRACT_URLS[state_code]:
            dest = os.path.join(state_dir, filename)
            if not os.path.exists(dest):
                download_file(url, dest)
                time.sleep(1)

    # 2. Perform live search for CBA PDFs / State Pay Plans
    queries = [
        f'"{agency}" "collective bargaining agreement" OR "memorandum of understanding" filetype:pdf',
        f'"{state_name}" correctional officer "pay schedule" OR "salary schedule" OR "step scale" filetype:pdf',
        f'"{agency}" correctional officer policy manual pay benefits filetype:pdf'
    ]
    
    with DDGS() as ddgs:
        for q in queries:
            try:
                results = list(ddgs.text(q, max_results=3))
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "document")
                    if url and (".pdf" in url.lower() or "contract" in url.lower() or "salary" in url.lower()):
                        clean_name = "".join([c if c.isalnum() else "_" for c in title[:40]]).strip("_").lower()
                        ext = ".pdf" if ".pdf" in url.lower() else ".html"
                        dest = os.path.join(state_dir, f"{clean_name}{ext}")
                        
                        if not os.path.exists(dest):
                            download_file(url, dest)
                            time.sleep(1)
            except Exception as e:
                console.print(f"[yellow]Search error for {state_name}: {e}[/yellow]")
            time.sleep(0.5)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Primary Contract & Statute Downloader for All 50 States")
    parser.add_argument("--state", type=str, help="Download for a single state (e.g. MN, CA, TX)")
    parser.add_argument("--all", action="store_true", help="Download primary contracts for all 50 states")
    args = parser.parse_args()

    if args.state:
        target = next((s for s in STATES_DATA if s["code"].upper() == args.state.upper()), None)
        if target:
            discover_and_download_for_state(target["code"], target["name"], target["agency"])
        return

    targets = STATES_DATA if args.all else [s for s in STATES_DATA if s["code"] in ["MN", "CA", "TX", "NY", "FL", "IL", "MI", "PA", "GA", "AL"]]
    for s in targets:
        discover_and_download_for_state(s["code"], s["name"], s["agency"])


if __name__ == "__main__":
    main()
