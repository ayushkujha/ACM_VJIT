import re
import base64
import os

os.makedirs('assets/pdf', exist_ok=True)

with open('assets/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

matches = re.finditer(r"([a-zA-Z0-9_]+):\s*\{\s*title:\s*'([^']+)',\s*b64:\s*'([^']+)'", js)
count = 0
for m in matches:
    key = m.group(1)
    title = m.group(2)
    b64 = m.group(3)
    
    with open(f'assets/pdf/{key}.pdf', 'wb') as f:
        f.write(base64.b64decode(b64))
    count += 1
    
    # replace base64 assignment with url
    js = js.replace(f"b64: '{b64}'", f"url: 'assets/pdf/{key}.pdf'")

if count > 0:
    # replace the PDF_DATA loader
    js = re.sub(r"'data:application/pdf;base64,'\s*\+\s*PDF_DATA\[([^\]]+)\]\.b64", r"PDF_DATA[\1].url", js)
    
    with open('assets/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js)

print(f"Extracted {count} PDFs")
