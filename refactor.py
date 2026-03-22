import os
import re
import base64

os.makedirs('assets/css', exist_ok=True)
os.makedirs('assets/js', exist_ok=True)
os.makedirs('assets/pdf', exist_ok=True)
os.makedirs('assets/images/team', exist_ok=True)

with open('acm_vjit_updated (11).html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract PDF_DATA
pdf_pattern = r"([a-zA-Z0-9_]+):\s*\{\s*title:\s*'([^']+)',\s*b64:\s*'([^']+)'\s*\}"
def pdf_repl(match):
    key = match.group(1)
    title = match.group(2)
    b64_data = match.group(3)
    
    with open(f'assets/pdf/{key}.pdf', 'wb') as pdf_file:
        pdf_file.write(base64.b64decode(b64_data))
        
    return f"{key}: {{ title: '{title}', url: 'assets/pdf/{key}.pdf' }}"

html_no_pdf = re.sub(pdf_pattern, pdf_repl, html)

# Replace the base64 JS assignment
html_no_pdf = re.sub(r"'data:application/pdf;base64,'\s*\+\s*PDF_DATA\[([^\]]+)\]\.b64", r"PDF_DATA[\1].url", html_no_pdf)

# Extract CSS
style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html_no_pdf, flags=re.DOTALL | re.IGNORECASE)
with open('assets/css/style.css', 'w', encoding='utf-8') as f:
    f.write('\n'.join(style_blocks).strip())

html_no_css = re.sub(r'<style[^>]*>.*?</style>', '', html_no_pdf, flags=re.DOTALL | re.IGNORECASE)

# Ensure there is a </head> to replace, if not, append to top
if '</head>' in html_no_css:
    html_no_css = html_no_css.replace('</head>', '  <link rel="stylesheet" href="assets/css/style.css">\n</head>')
else:
    html_no_css = '<link rel="stylesheet" href="assets/css/style.css">\n' + html_no_css

# Extract JS
script_blocks = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html_no_css, flags=re.DOTALL | re.IGNORECASE)
with open('assets/js/main.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(script_blocks).strip())

html_no_js = re.sub(r'<script(?![^>]*src=)[^>]*>.*?</script>', '', html_no_css, flags=re.DOTALL | re.IGNORECASE)

# Ensure there is a </body> to replace
if '</body>' in html_no_js:
    html_final = html_no_js.replace('</body>', '  <script src="assets/js/main.js" defer></script>\n</body>')
else:
    html_final = html_no_js + '\n<script src="assets/js/main.js" defer></script>'

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

print("Extraction complete. New file is index.html")
