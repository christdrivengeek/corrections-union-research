with open('harvest_advanced.py', 'r') as f:
    content = f.read()
content = content.replace("page.goto(config['portal'], timeout=45000, wait_until='networkidle')", 
    "try: page.goto(config['portal'], timeout=45000, wait_until='domcontentloaded')\n                    except Exception: pass")
with open('harvest_advanced.py', 'w') as f:
    f.write(content)
