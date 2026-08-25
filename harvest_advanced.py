#!/usr/bin/env python3
"""
Advanced Contract Harvester (Playwright)
Attempts to download the *exact* known PDFs using Playwright's headless browser 
network context to bypass TLS fingerprinting and Cloudflare 403s.
"""

import os
import urllib.parse
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATES_DIR = os.path.join(BASE_DIR, "states")

from harvest_contracts import STATE_MAP

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
    print(f"[*] Found {len(missing)} states missing PDFs: {missing}\n")
    if not missing:
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = context.new_page()
        
        for code in missing:
            config = STATE_MAP[code]
            state_dir = os.path.join(STATES_DIR, code)
            os.makedirs(state_dir, exist_ok=True)
            
            print(f"{'='*50}\n[{code}] Bargaining Unit: {config['unit']}")
            downloaded = 0
            
            # 1. First, aggressively try the exact known PDF URLs!
            for expected_filename, pdf_url in config.get('pdfs', []):
                print(f"[{code}] Fetching exact URL: {pdf_url}")
                try:
                    # Do NOT use page.goto() for files, it throws "Navigation interrupted by download"
                    # Instead, use the raw browser context request!
                    req_resp = context.request.get(pdf_url, timeout=30000)
                    
                    if req_resp.ok:
                        filepath = os.path.join(state_dir, expected_filename)
                        with open(filepath, 'wb') as f:
                            f.write(req_resp.body())
                        print(f"  ✓ Saved {expected_filename} ({len(req_resp.body()) // 1024} KB)")
                        downloaded += 1
                    else:
                        print(f"  ⚠ HTTP {req_resp.status} for {pdf_url}")
                except Exception as e:
                    print(f"  ⚠ Failed direct download: {str(e)[:100]}")
            
            # 2. If exact URLs failed, try scraping the portal page
            if downloaded == 0:
                print(f"[{code}] Direct URLs failed, falling back to portal scrape: {config['portal']}")
                try:
                    try:
                        page.goto(config['portal'], timeout=45000, wait_until='domcontentloaded')
                    except Exception as goto_e:
                        pass # sometimes it throws if a download triggers, but DOM is still loaded
                        
                    hrefs = page.eval_on_selector_all(
                        "a", "elements => elements.map(e => e.href).filter(h => h.toLowerCase().includes('.pdf'))"
                    )
                    for link in list(set(hrefs))[:3]:
                        print(f"  -> Scraping found link: {link}")
                        req_resp = context.request.get(link, timeout=20000)
                        if req_resp.ok:
                            filename = os.path.basename(urllib.parse.urlparse(link).path)
                            if not filename.lower().endswith('.pdf'): filename += '.pdf'
                            with open(os.path.join(state_dir, f"scraped_{filename}"), 'wb') as f:
                                f.write(req_resp.body())
                            print(f"  ✓ Saved scraped PDF: {filename}")
                            downloaded += 1
                except Exception as e:
                    print(f"  ⚠ Portal scrape failed: {str(e)[:100]}")
                    
        browser.close()
        
if __name__ == "__main__":
    main()
