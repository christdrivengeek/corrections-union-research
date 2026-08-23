#!/usr/bin/env python3
"""
50-State Direct Labor Portal Contract Harvester
Goes directly to each state's official Office of Employee Relations /
Office of Collective Bargaining portal — not generic Google search.
"""

import os, sys, time, json, logging
from datetime import datetime
from curl_cffi import requests as c_requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATES_DIR = os.path.join(BASE_DIR, "states")
LOG_FILE   = os.path.join(BASE_DIR, "contract_harvest.log")
PROG_FILE  = os.path.join(BASE_DIR, "contract_progress.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ── Direct official URLs for every state ─────────────────────────────────────
STATE_MAP = {
    "AK": {
        "unit": "Alaska Correctional Officers Association (ACOA)",
        "portal": "https://doa.alaska.gov/dop/laborRelations/contracts/",
        "pdfs": [
            ("ACOA_Corrections_Contract_2022_2025.pdf",
             "https://doa.alaska.gov/dop/fileadmin/LaborRelations/pdf/agreements/ACOA_2022-2025.pdf"),
        ]
    },
    "AL": {
        "unit": "Non-Union (ADOC — Alabama Personnel Rules)",
        "portal": "https://www.personnel.alabama.gov/",
        "pdfs": [
            ("AL_Personnel_Rules.pdf",
             "https://www.personnel.alabama.gov/Docs/PersonnelRules.pdf"),
            ("AL_Pay_Plan.pdf",
             "https://www.personnel.alabama.gov/Docs/PayPlan.pdf"),
        ]
    },
    "AR": {
        "unit": "Non-Union (ADC — AR Office of Personnel Management)",
        "portal": "https://www.dfa.arkansas.gov/human-resources/",
        "pdfs": [
            ("AR_Classification_Pay_Plan.pdf",
             "https://www.dfa.arkansas.gov/images/uploads/officeOfPersonnelManagement/classifications/PayPlan.pdf"),
        ]
    },
    "AZ": {
        "unit": "Non-Union (ADCRR — AZ HR Merit System)",
        "portal": "https://hr.az.gov/content/employee-pay-and-benefits",
        "pdfs": [
            ("AZ_State_Pay_Plan_FY2024.pdf",
             "https://hr.az.gov/sites/default/files/media/file/2024/01/fy2024_pay_plan.pdf"),
        ]
    },
    "CA": {
        "unit": "CCPOA — CA Correctional Peace Officers Assoc. (BU 6)",
        "portal": "https://www.calhr.ca.gov/labor-relations/Pages/bargaining-unit-06.aspx",
        "pdfs": [
            ("CCPOA_BU6_MOU_2023_2026.pdf",
             "https://www.calhr.ca.gov/labor-relations/Documents/mou-20230703-20260702-bu06.pdf"),
            ("CalHR_Pay_Scale_Section14.pdf",
             "https://www.calhr.ca.gov/Pay%20Scales%20Library/PS_Sec_14.pdf"),
        ]
    },
    "CO": {
        "unit": "CPOA / Colorado PERA",
        "portal": "https://dhr.colorado.gov/state-employees/total-compensation",
        "pdfs": [
            ("CO_Salary_Schedule.pdf",
             "https://dhr.colorado.gov/sites/dhr/files/documents/SalarySchedule.pdf"),
        ]
    },
    "CT": {
        "unit": "AFSCME NP-4 Security Services",
        "portal": "https://portal.ct.gov/OLR/Contract-Agreements",
        "pdfs": [
            ("CT_NP4_Security_Contract_2021_2024.pdf",
             "https://portal.ct.gov/-/media/OLR/contracts/np4/NP4-2021-2024.pdf"),
        ]
    },
    "DE": {
        "unit": "AFSCME Local 1579 (Delaware DOC)",
        "portal": "https://dhr.delaware.gov/laborrelations/agreements.shtml",
        "pdfs": [
            ("DE_AFSCME_1579_Corrections_Contract.pdf",
             "https://dhr.delaware.gov/laborrelations/documents/agreements/afscme-council81-lu1579.pdf"),
        ]
    },
    "FL": {
        "unit": "PBA Security Services Unit",
        "portal": "https://www.dms.myflorida.com/workforce_operations/human_resource_management/for_state_employees/labor_agreements",
        "pdfs": [
            ("FL_PBA_Security_Services_2023_2026.pdf",
             "https://www.dms.myflorida.com/content/download/196785/1177977"),
        ]
    },
    "GA": {
        "unit": "Non-Union (GDC — Georgia DOAS State Pay Plan)",
        "portal": "https://doas.ga.gov/human-resources-administration/compensation/pay-grades-and-salary-ranges",
        "pdfs": [
            ("GA_Statewide_Salary_Plan.pdf",
             "https://doas.ga.gov/assets/Human%20Resources%20Administration/Compensation/StatewideSalaryPlan.pdf"),
        ]
    },
    "HI": {
        "unit": "HGEA BU-10 Institutional Care Workers",
        "portal": "https://dhrd.hawaii.gov/state-employees/labor-relations/labor-agreements/",
        "pdfs": [
            ("HI_HGEA_BU10_Contract_2023_2027.pdf",
             "https://dhrd.hawaii.gov/wp-content/uploads/2023/01/BU10-2023-2027-Agreement.pdf"),
        ]
    },
    "IA": {
        "unit": "AFSCME Iowa Council 61",
        "portal": "https://das.iowa.gov/human-resources/labor-relations/contract-agreements",
        "pdfs": [
            ("IA_AFSCME_Master_Contract_2023_2025.pdf",
             "https://das.iowa.gov/sites/default/files/hr/documents/labor_relations/contracts/afscme_contract_2023-2025.pdf"),
        ]
    },
    "ID": {
        "unit": "Non-Union (IDOC — Idaho DHR Pay Plan)",
        "portal": "https://dhr.idaho.gov/compensation/pay-plan/",
        "pdfs": [
            ("ID_State_Pay_Plan.pdf",
             "https://dhr.idaho.gov/wp-content/uploads/Pay-Plan.pdf"),
        ]
    },
    "IL": {
        "unit": "AFSCME Council 31 — RC-6 / RC-9 (Corrections)",
        "portal": "https://www2.illinois.gov/cms/Employees/labor/Pages/Contracts.aspx",
        "pdfs": [
            ("IL_AFSCME_RC6_Contract.pdf",
             "https://www2.illinois.gov/cms/Employees/labor/Documents/RC6contract.pdf"),
            ("IL_AFSCME_RC9_Contract.pdf",
             "https://www2.illinois.gov/cms/Employees/labor/Documents/RC9contract.pdf"),
        ]
    },
    "IN": {
        "unit": "Non-Union (IDOC — Indiana SPD Pay Plan)",
        "portal": "https://www.in.gov/spd/compensation-and-classification/",
        "pdfs": [
            ("IN_State_Pay_Plan.pdf",
             "https://www.in.gov/spd/files/payplan.pdf"),
        ]
    },
    "KS": {
        "unit": "Non-Union (KDOC — Kansas DHR Pay Plan)",
        "portal": "https://admin.ks.gov/offices/personnel-services/compensation",
        "pdfs": [
            ("KS_State_Pay_Plan.pdf",
             "https://admin.ks.gov/docs/default-source/personnel-services/compensation/pay-plan.pdf"),
        ]
    },
    "KY": {
        "unit": "Non-Union (KY DOC — Personnel Cabinet Pay Plan)",
        "portal": "https://personnel.ky.gov/Pages/Compensation.aspx",
        "pdfs": [
            ("KY_State_Pay_Plan.pdf",
             "https://personnel.ky.gov/Lists/Pay%20Grades/PayPlan.pdf"),
        ]
    },
    "LA": {
        "unit": "Non-Union (LDPSC — LA Civil Service Pay Plan)",
        "portal": "https://www.civilservice.louisiana.gov/Compensation-Pay",
        "pdfs": [
            ("LA_Civil_Service_Pay_Plan.pdf",
             "https://www.civilservice.louisiana.gov/Portals/0/Documents/Compensation/PayPlan.pdf"),
        ]
    },
    "MA": {
        "unit": "NAGE Local 282 / MassCO (MA DOC Corrections)",
        "portal": "https://www.mass.gov/lists/current-collective-bargaining-agreements",
        "pdfs": [
            ("MA_NAGE_Corrections_Contract.pdf",
             "https://www.mass.gov/doc/nage-corrections-officers-2021-2024/download"),
        ]
    },
    "MD": {
        "unit": "AFSCME Maryland Council 3",
        "portal": "https://dbm.maryland.gov/employees/Pages/LaborRelationsContracts.aspx",
        "pdfs": [
            ("MD_AFSCME_Council3_Security_Contract.pdf",
             "https://dbm.maryland.gov/employees/Documents/LaborRelations/AFSCME_C3_Security_Agreement.pdf"),
        ]
    },
    "ME": {
        "unit": "MSEA-SEIU Local 1989",
        "portal": "https://www.maine.gov/bhr/labor-relations/labor-agreements",
        "pdfs": [
            ("ME_MSEA_Corrections_Contract.pdf",
             "https://www.maine.gov/bhr/sites/maine.gov.bhr/files/inline-files/MSEA_Supervisory_Agreement.pdf"),
        ]
    },
    "MI": {
        "unit": "MCO — Michigan Corrections Organization",
        "portal": "https://www.michigan.gov/mco",
        "pdfs": [
            ("MI_MCO_Contract_2022_2024.pdf",
             "https://www.michigan.gov/mco/-/media/Project/Websites/mco/Documents/2022-2024-MCO-Contract.pdf"),
        ]
    },
    "MN": {
        "unit": "AFSCME Council 5, Unit 8 (Corrections) — VERIFIED",
        "portal": "https://mn.gov/mmb/employee-relations/labor-relations/labor/afscme.jsp",
        "pdfs": [
            ("AFSCME_Unit_8_Corrections_Contract_2025_2027.pdf",
             "https://mn.gov/mmb-stat/000/az/labor-relations/afscme/unit8/2025-2027/afscme-unit-8-contract-2025-2027.pdf"),
            ("AFSCME_Master_Agreement_MultiUnit_2025_2027.pdf",
             "https://mn.gov/mmb-stat/000/az/labor-relations/afscme/contract/2025-2027/AFSCME-MultiUnit-2025-2027-Contract.pdf"),
            ("MN_MMB_Salary_Plan_LR0067.pdf",
             "https://mn.gov/mmb-stat/hr-toolbox/002-class-and-compensation/003-compensation/current-class-and-salary-range-report.pdf"),
        ]
    },
    "MO": {
        "unit": "Non-Union (MODOC — MO OA Merit System Pay Plan)",
        "portal": "https://oa.mo.gov/personnel/pay-grades-step-schedules",
        "pdfs": [
            ("MO_State_Pay_Plan.pdf",
             "https://oa.mo.gov/sites/default/files/payplan.pdf"),
        ]
    },
    "MS": {
        "unit": "Non-Union (MDOC — MS State Personnel Board)",
        "portal": "https://www.spb.ms.gov/compensation/",
        "pdfs": [
            ("MS_State_Pay_Plan.pdf",
             "https://www.spb.ms.gov/wp-content/uploads/2023/07/PayPlan.pdf"),
        ]
    },
    "MT": {
        "unit": "MPEA / AFSCME (limited)",
        "portal": "https://hr.mt.gov/Employees/compensation",
        "pdfs": [
            ("MT_State_Pay_Plan_2023_2025.pdf",
             "https://hr.mt.gov/Portals/78/docs/compclass/2023-2025_Pay_Plan.pdf"),
        ]
    },
    "NC": {
        "unit": "Non-Union (NCDAC — OSHR; collective bargaining prohibited by G.S. § 95-98)",
        "portal": "https://oshr.nc.gov/state-employee-resources/compensation",
        "pdfs": [
            ("NC_Salary_Schedule_2024.pdf",
             "https://oshr.nc.gov/sites/default/files/documents/files/2024-Salary-Schedules.pdf"),
            ("NC_GS_95_98_CBA_Prohibition_Statute.pdf",
             "https://www.ncleg.net/enactedlegislation/statutes/pdf/bychapter/Chapter_95.pdf"),
        ]
    },
    "ND": {
        "unit": "Non-Union (NDDOCR — ND HRMS Pay Plan)",
        "portal": "https://www.nd.gov/hrms/comp/",
        "pdfs": [
            ("ND_State_Pay_Plan.pdf",
             "https://www.nd.gov/hrms/docs/payplan.pdf"),
        ]
    },
    "NE": {
        "unit": "Non-Union (NDCS — NE DAS Personnel Pay Plan)",
        "portal": "https://das.nebraska.gov/personnel/payplan.html",
        "pdfs": [
            ("NE_State_Pay_Plan.pdf",
             "https://das.nebraska.gov/personnel/documents/payplan.pdf"),
        ]
    },
    "NH": {
        "unit": "SEA/SEIU Local 1984",
        "portal": "https://das.nh.gov/hr/collective-bargaining/",
        "pdfs": [
            ("NH_SEA_State_Employees_Contract.pdf",
             "https://das.nh.gov/hr/documents/contracts/SEA_Contract.pdf"),
        ]
    },
    "NJ": {
        "unit": "PBA Local 105 / CWA (NJ DOC)",
        "portal": "https://www.nj.gov/csc/employees/labor/agreements/",
        "pdfs": [
            ("NJ_PBA_Corrections_Contract.pdf",
             "https://www.nj.gov/csc/employees/labor/agreements/pdf/pba105.pdf"),
        ]
    },
    "NM": {
        "unit": "AFSCME Local 3022 / NMCD State Pay Plan",
        "portal": "https://www.spo.state.nm.us/compensation.aspx",
        "pdfs": [
            ("NM_State_Pay_Plan.pdf",
             "https://www.spo.state.nm.us/uploads/FileLinks/PayPlan.pdf"),
        ]
    },
    "NV": {
        "unit": "AFSCME Nevada (limited CBA) / PERS",
        "portal": "https://hr.nv.gov/Employees/Compensation/",
        "pdfs": [
            ("NV_State_Pay_Plan.pdf",
             "https://hr.nv.gov/uploadedFiles/hrnvgov/Content/Employees/Compensation/documents/BiweeklyPayGrades.pdf"),
        ]
    },
    "NY": {
        "unit": "NYSCOPBA — NY State Correctional Officers & Police Benevolent Assoc.",
        "portal": "https://oer.ny.gov/contracts",
        "pdfs": [
            ("NYSCOPBA_Security_Services_Contract_2023_2026.pdf",
             "https://oer.ny.gov/system/files/documents/2023/11/nyscopba-contract-2023-2026.pdf"),
            ("NY_Security_Hiring_Job_Rate_Salary.pdf",
             "https://oer.ny.gov/system/files/documents/2024/04/security-services-hiring-job-rate.pdf"),
        ]
    },
    "OH": {
        "unit": "OCSEA/AFSCME Local 11 — Unit 3 (Corrections)",
        "portal": "https://das.ohio.gov/employee-relations/collective-bargaining-agreements",
        "pdfs": [
            ("OH_OCSEA_Unit3_Corrections_Contract_2023_2026.pdf",
             "https://das.ohio.gov/static/er/contracts/OCSEA-Contract-2023-2026.pdf"),
        ]
    },
    "OK": {
        "unit": "Non-Union (ODOC — OMES HR; CBA prohibited by OK statute)",
        "portal": "https://omes.ok.gov/services/human-resources/compensation",
        "pdfs": [
            ("OK_State_Pay_Plan.pdf",
             "https://omes.ok.gov/sites/g/files/gargs686/f/documents/PayPlan.pdf"),
        ]
    },
    "OR": {
        "unit": "AFSCME Council 75 Unit 17 (Corrections)",
        "portal": "https://www.oregon.gov/das/hr/pages/labor_relations.aspx",
        "pdfs": [
            ("OR_AFSCME_C75_Unit17_Corrections_Contract.pdf",
             "https://www.oregon.gov/das/hr/Documents/AFSCME_Unit_17_Corrections.pdf"),
        ]
    },
    "PA": {
        "unit": "PSCOA — PA State Corrections Officers Assoc. (H-1 Unit)",
        "portal": "https://www.oa.pa.gov/Employees/LaborRelations/Pages/default.aspx",
        "pdfs": [
            ("PSCOA_H1_Contract_2023_2026.pdf",
             "https://www.oa.pa.gov/Employees/Labor%20Relations/Documents/PSCOA%202023-2026.pdf"),
        ]
    },
    "RI": {
        "unit": "RIJLEA / AFSCME Council 94 (RI DOC Corrections)",
        "portal": "https://doa.ri.gov/personnel/labor-relations",
        "pdfs": [
            ("RI_Council94_Corrections_Contract.pdf",
             "https://doa.ri.gov/sites/g/files/xkgbur421/files/documents/personnel/labor-relations/Council94_Corrections_Agreement.pdf"),
        ]
    },
    "SC": {
        "unit": "Non-Union (SCDC — SC Admin; CBA prohibited by SC Code § 8-17-10)",
        "portal": "https://www.admin.sc.gov/humanresources/compensation",
        "pdfs": [
            ("SC_State_Pay_Plan.pdf",
             "https://www.admin.sc.gov/sites/default/files/Documents/HumanResources/PayPlan.pdf"),
        ]
    },
    "SD": {
        "unit": "Non-Union (SD DOC — Bureau of HR Pay Plan)",
        "portal": "https://bhr.sd.gov/employee-resources/compensation/",
        "pdfs": [
            ("SD_State_Pay_Plan.pdf",
             "https://bhr.sd.gov/employee-resources/compensation/documents/PayPlan.pdf"),
        ]
    },
    "TN": {
        "unit": "Non-Union (TDOC — TN DHA; public sector CBA prohibited by TN Code § 49-5-610)",
        "portal": "https://www.tn.gov/hr/employees/compensation.html",
        "pdfs": [
            ("TN_State_Pay_Plan.pdf",
             "https://www.tn.gov/content/dam/tn/hr/documents/pay-plan.pdf"),
        ]
    },
    "TX": {
        "unit": "Non-Union (TDCJ — Schedule C Law Enforcement Pay; CBA prohibited by TX Gov't Code § 617.002)",
        "portal": "https://www.tdcj.texas.gov/divisions/hr/coinfo/cosalary.html",
        "pdfs": [
            ("TX_TDCJ_Salary_Schedule_C.html",
             "https://www.tdcj.texas.gov/divisions/hr/coinfo/cosalary.html"),
            ("TX_TDCJ_CO_Pay_Schedule.pdf",
             "https://www.tdcj.texas.gov/divisions/hr/hr-home/documents/salary_schedules.pdf"),
        ]
    },
    "UT": {
        "unit": "Non-Union (UDC — UT DHRM Pay Plan)",
        "portal": "https://dhrm.utah.gov/pay-and-benefits/pay-plans/",
        "pdfs": [
            ("UT_State_Pay_Plan.pdf",
             "https://dhrm.utah.gov/wp-content/uploads/Pay-Plan.pdf"),
        ]
    },
    "VA": {
        "unit": "Non-Union (VADOC — VA DHRM Pay Band Policy; limited local CBA rights post-2021)",
        "portal": "https://www.dhrm.virginia.gov/compensationbenefits",
        "pdfs": [
            ("VA_Pay_Band_Salary_Ranges.pdf",
             "https://www.dhrm.virginia.gov/docs/default-source/compensationpolicyandadmin/compensation/comp-payband-salary-ranges.pdf"),
        ]
    },
    "VT": {
        "unit": "VSEA — Vermont State Employees Association",
        "portal": "https://humanresources.vermont.gov/labor-relations/collective-bargaining-agreements",
        "pdfs": [
            ("VT_VSEA_Corrections_Contract.pdf",
             "https://humanresources.vermont.gov/sites/humanresources/files/documents/Labor_Relations/contracts/VSEA_Contract.pdf"),
        ]
    },
    "WA": {
        "unit": "Teamsters Local 117 (WA DOC Corrections)",
        "portal": "https://ofm.wa.gov/labor/agreements",
        "pdfs": [
            ("WA_Teamsters117_DOC_Contract_2021_2023.pdf",
             "https://ofm.wa.gov/sites/default/files/public/labor/agreements/21-23/Teamsters_117_general.pdf"),
        ]
    },
    "WI": {
        "unit": "Non-Union (WI DOC — DPM; collective bargaining eliminated by Act 10/2011)",
        "portal": "https://dpm.wi.gov/Pages/HR_Admin/CompBenefits.aspx",
        "pdfs": [
            ("WI_State_Pay_Plan.pdf",
             "https://dpm.wi.gov/Documents/Publications/comp_group.pdf"),
            ("WI_Act10_2011_CBA_Elimination.pdf",
             "https://docs.legis.wisconsin.gov/2011/related/acts/10.pdf"),
        ]
    },
    "WV": {
        "unit": "WVDCR / AFSCME WV (limited CBA rights)",
        "portal": "https://personnel.wv.gov/compensation/pages/default.aspx",
        "pdfs": [
            ("WV_State_Pay_Plan.pdf",
             "https://personnel.wv.gov/compensation/documents/PaySchedule.pdf"),
        ]
    },
    "WY": {
        "unit": "Non-Union (WDOC — WY HR Pay Scale; no public sector CBA in Wyoming)",
        "portal": "https://ai.wyo.gov/hr/compensation",
        "pdfs": [
            ("WY_State_Pay_Scale_FY2025.pdf",
             "https://ai.wyo.gov/hr/documents/compensation/PayPlanFY2025.pdf"),
        ]
    },
}


def load_progress():
    if os.path.exists(PROG_FILE):
        with open(PROG_FILE) as f:
            return json.load(f)
    return {"completed": [], "failed": {}}


def save_progress(p):
    with open(PROG_FILE, "w") as f:
        json.dump(p, f, indent=2)


def download_file(url, dest, code):
    if os.path.exists(dest) and os.path.getsize(dest) > 500:
        log.info(f"[{code}] Already exists: {os.path.basename(dest)}")
        return True
    try:
        resp = c_requests.get(url, impersonate="chrome124", timeout=25)
        if resp.status_code == 200 and len(resp.content) > 200:
            with open(dest, "wb") as f:
                f.write(resp.content)
            log.info(f"[{code}] ✓ {os.path.basename(dest)} ({len(resp.content)//1024} KB)")
            return True
        log.warning(f"[{code}] HTTP {resp.status_code}: {url}")
    except Exception as e:
        log.warning(f"[{code}] Error on {url}: {e}")
    return False


def scrape_portal(code, portal_url, state_dir):
    try:
        resp = c_requests.get(portal_url, impersonate="chrome124", timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        from urllib.parse import urlparse, urljoin
        base = portal_url
        found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".pdf" not in href.lower():
                continue
            full_url = urljoin(base, href)
            label = "".join(c if c.isalnum() else "_" for c in a.get_text(strip=True)[:50]).strip("_").lower() or f"doc_{found}"
            dest = os.path.join(state_dir, f"portal_{label}.pdf")
            if download_file(full_url, dest, code):
                found += 1
                time.sleep(1)
            if found >= 4:
                break
    except Exception as e:
        log.warning(f"[{code}] Portal scrape error: {e}")


def write_source_info(code, config, state_dir):
    path = os.path.join(state_dir, "SOURCE_INFO.md")
    files = sorted(os.listdir(state_dir))
    with open(path, "w") as f:
        f.write(f"# {code} — Primary Contract Source Index\n\n")
        f.write(f"**Bargaining Unit:** {config['unit']}\n\n")
        f.write(f"**Official Portal:** [{config['portal']}]({config['portal']})\n\n")
        f.write(f"**Harvested:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write("## Files:\n")
        for fn in files:
            if fn == "SOURCE_INFO.md":
                continue
            size = os.path.getsize(os.path.join(state_dir, fn))
            f.write(f"- `{fn}` ({size // 1024} KB)\n")


def git_push(batch):
    try:
        os.system(
            f'cd {BASE_DIR} && git add states/ && '
            f'git commit -m "Contract harvest: {batch}" && '
            f'git push origin main'
        )
    except Exception as e:
        log.warning(f"Git push failed: {e}")


def process_state(code, config, progress):
    if code in progress["completed"]:
        log.info(f"[{code}] Already done, skipping.")
        return
    state_dir = os.path.join(STATES_DIR, code)
    os.makedirs(state_dir, exist_ok=True)
    log.info(f"\n{'='*55}\n[{code}] {config['unit']}")

    for filename, url in config.get("pdfs", []):
        download_file(url, os.path.join(state_dir, filename), code)
        time.sleep(1.5)

    # fallback portal scrape if nothing useful downloaded
    existing_pdfs = [f for f in os.listdir(state_dir) if f.endswith(".pdf")]
    if not existing_pdfs:
        log.info(f"[{code}] No PDFs yet — scraping portal page...")
        scrape_portal(code, config["portal"], state_dir)

    write_source_info(code, config, state_dir)
    progress["completed"].append(code)
    save_progress(progress)
    log.info(f"[{code}] ✅ Complete.")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", help="Single state code")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    if args.reset and os.path.exists(PROG_FILE):
        os.remove(PROG_FILE)

    progress = load_progress()
    log.info(f"Harvest started: {datetime.now()} | Done so far: {len(progress['completed'])}")

    if args.state:
        code = args.state.upper()
        process_state(code, STATE_MAP[code], progress)
        git_push(code)
        return

    targets = [k for k in STATE_MAP if k not in progress["completed"]]
    log.info(f"Processing {len(targets)} remaining states...")

    batch = []
    for code in targets:
        try:
            process_state(code, STATE_MAP[code], progress)
            batch.append(code)
            if len(batch) >= 5:
                git_push(", ".join(batch))
                batch = []
        except Exception as e:
            log.error(f"[{code}] Unexpected error: {e}")
            progress["failed"][code] = str(e)
            save_progress(progress)
        time.sleep(2)

    if batch:
        git_push(", ".join(batch))

    log.info(f"\nHARVEST COMPLETE | Done: {len(progress['completed'])} | Failed: {list(progress['failed'].keys())}")


if __name__ == "__main__":
    main()
