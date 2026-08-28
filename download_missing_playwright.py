import os
import time
from ddgs import DDGS
from playwright.sync_api import sync_playwright
from harvest_contracts import STATE_MAP

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATES_DIR = os.path.join(BASE_DIR, "states")

def get_missing_states():
    missing = []
    for code in STATE_MAP.keys():
        d = os.path.join(STATES_DIR, code)
        pdfs = [f for f in os.listdir(d) if f.lower().endswith('.pdf')] if os.path.exists(d) else []
        if not pdfs:
            missing.append(code)
    return missing

def main():
    missing = get_missing_states()
    print(f"Missing states: {missing}")
    
    state_names = {
        "AZ": "Arizona", "IA": "Iowa", "LA": "Louisiana", "MA": "Massachusetts",
        "MD": "Maryland", "MI": "Michigan", "MS": "Mississippi", "NH": "New Hampshire",
        "NJ": "New Jersey", "NM": "New Mexico", "OH": "Ohio", "RI": "Rhode Island",
        "TN": "Tennessee", "WI": "Wisconsin", "WV": "West Virginia"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        
        with DDGS() as ddgs:
            for code in missing:
                config = STATE_MAP[code]
                unit = config['unit']
                name = state_names.get(code, code)
                
                if "Non-Union" in unit:
                    query = f"{name} state employee pay plan compensation schedule filetype:pdf"
                else:
                    if code == 'MA':
                        query = "Massachusetts MCOFU collective bargaining agreement filetype:pdf"
                    else:
                        query = f"{name} state corrections collective bargaining agreement filetype:pdf"
                    
                print(f"[{code}] Searching: {query}")
                try:
                    results = list(ddgs.text(query, max_results=5))
                    pdf_url = None
                    for res in results:
                        href = res.get('href', '')
                        if href.lower().endswith('.pdf'):
                            pdf_url = href
                            break
                    
                    if pdf_url:
                        print(f"  -> Found PDF: {pdf_url}")
                        
                        # Download with Playwright context request
                        req_resp = context.request.get(pdf_url, timeout=30000)
                        if req_resp.ok:
                            dest = os.path.join(STATES_DIR, code, f"search_found_pw_{code}.pdf")
                            with open(dest, "wb") as f:
                                f.write(req_resp.body())
                            print(f"  ✓ Downloaded to {dest}")
                        else:
                            print(f"  ⚠ Failed Playwright download: HTTP {req_resp.status}")
                    else:
                        print("  ⚠ No PDF found in search results.")
                except Exception as e:
                    print(f"  ⚠ Error for {code}: {e}")
                
                time.sleep(2)
        
        browser.close()

if __name__ == '__main__':
    main()
