import os
import re
import base64

with open('assets/js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

if 'PDF_DATA' in js_content:
    print("Found PDF_DATA in JS!")
    pdf_pattern = r"([a-zA-Z0-9_]+):\s*\{\s*title:\s*['\"]([^'^\"]+)['\"],\s*b64:\s*['\"]([^'^\"]+)['\"]\s*\}"
    def pdf_repl(match):
        key = match.group(1)
        title = match.group(2)
        b64_data = match.group(3)
        with open(f'assets/pdf/{key}.pdf', 'wb') as pdf_file:
            pdf_file.write(base64.b64decode(b64_data))
        return f"{key}: {{ title: '{title}', url: 'assets/pdf/{key}.pdf' }}"

    js_no_pdf = re.sub(pdf_pattern, pdf_repl, js_content)
    js_no_pdf = re.sub(r"['\"]data:application/pdf;base64,['\"]\s*\+\s*PDF_DATA\[([^\]]+)\]\.b64", r"PDF_DATA[\1].url", js_no_pdf)
    with open('assets/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js_no_pdf)
    print("Extracted PDFs from main.js")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract base64 images from HTML
img_pattern = r'<img\s+([^>]*)src=["\']data:image/([^;]+);base64,([^"\']+)["\']([^>]*)>'
img_count = 0
def img_repl(m):
    global img_count
    attrs_before = m.group(1)
    ext = m.group(2)
    b64 = m.group(3)
    attrs_after = m.group(4)
    img_name = f'team_{img_count}.{ext}'
    img_count += 1
    with open(f'assets/images/team/{img_name}', 'wb') as img_f:
        img_f.write(base64.b64decode(b64))
    return f'<img {attrs_before}src="assets/images/team/{img_name}"{attrs_after}>'

html = re.sub(img_pattern, img_repl, html, flags=re.IGNORECASE)
print(f"Extracted {img_count} images from HTML")

# adding alt to images
html = re.sub(r'(<img *(?![^>]*alt=)[^>]*)>', r'\1 alt="Image">', html, flags=re.IGNORECASE)

# adding type="button" 
html = re.sub(r'(<button *(?![^>]*type=)[^>]*)>', r'\1 type="button">', html, flags=re.IGNORECASE)

# adding aria-label to social links
def aria_repl(match):
    full_tag = match.group(0)
    if 'aria-label=' not in full_tag:
        title_match = re.search(r'title=["\']([^"\']+)["\']', full_tag, re.IGNORECASE)
        if title_match:
            return full_tag[:-1] + f' aria-label="{title_match.group(1)}">'
        return full_tag[:-1] + ' aria-label="Social Link">'
    return full_tag

html = re.sub(r'<a[^>]*class=["\'][^"\']*ftm-member-social-btn[^"\']*["\'][^>]*>', aria_repl, html, flags=re.IGNORECASE)

# adding SEO meta if missing
if '<meta name="description"' not in html:
    html = html.replace('</head>', '  <meta name="description" content="ACM VJIT Student Chapter - Fostering computing culture and technical excellence at VJIT.">\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Finished SEO and A11y adjustments")
