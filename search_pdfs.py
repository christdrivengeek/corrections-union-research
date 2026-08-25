import os
import time
import requests
from ddgs import DDGS
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

def search_and_download():
    missing = get_missing_states()
    print(f"Missing states: {missing}")
    
    with DDGS() as ddgs:
        for code in missing:
            config = STATE_MAP[code]
            unit = config['unit']
            
            # Determine search query based on if it's a union or non-union
            if "Non-Union" in unit:
                query = f"{code} state employee pay plan compensation schedule filetype:pdf"
            else:
                query = f"{code} state corrections collective bargaining agreement {unit.split('-')[0]} filetype:pdf"
                
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
                    resp = requests.get(pdf_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        dest = os.path.join(STATES_DIR, code, f"search_found_{code}.pdf")
                        with open(dest, "wb") as f:
                            f.write(resp.content)
                        print(f"  ✓ Downloaded to {dest}")
                    else:
                        print(f"  ⚠ Failed to download (Status {resp.status_code})")
                else:
                    print("  ⚠ No PDF found in search results.")
            except Exception as e:
                print(f"  ⚠ Error searching for {code}: {e}")
            
            time.sleep(2) # rate limit

if __name__ == '__main__':
    search_and_download()
