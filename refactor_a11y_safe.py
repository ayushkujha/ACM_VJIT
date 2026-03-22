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

# Extract base64 images without catastrophic backtracking
parts = html.split('data:image/')
img_count = 0
if len(parts) > 1:
    new_html = parts[0]
    for part in parts[1:]:
        end_idx = part.find('"')
        end_idx2 = part.find("'")
        if end_idx == -1 or (end_idx2 != -1 and end_idx2 < end_idx):
            end_idx = end_idx2
            
        if end_idx != -1:
            data = part[:end_idx]
            rest = part[end_idx:]
            if ';base64,' in data:
                ext, b64 = data.split(';base64,')
                img_name = f'team_{img_count}.{ext}'
                img_count += 1
                with open(f'assets/images/team/{img_name}', 'wb') as img_f:
                    img_f.write(base64.b64decode(b64))
                new_html += f'assets/images/team/{img_name}' + rest
            else:
                new_html += 'data:image/' + part
        else:
            new_html += 'data:image/' + part
    html = new_html

print(f"Extracted {img_count} images from HTML")

# adding alt to images
img_tags = re.findall(r'<img[^>]*>', html, flags=re.IGNORECASE)
for tag in img_tags:
    if 'alt=' not in tag.lower():
        new_tag = tag.replace('<img ', '<img alt="Image" ')
        html = html.replace(tag, new_tag)

# adding type="button"
btn_tags = re.findall(r'<button[^>]*>', html, flags=re.IGNORECASE)
for tag in btn_tags:
    if 'type=' not in tag.lower():
        new_tag = tag.replace('<button ', '<button type="button" ')
        html = html.replace(tag, new_tag)

# adding aria-label
a_tags = re.findall(r'<a[^>]*class=["\'][^"\']*ftm-member-social-btn[^"\']*["\'][^>]*>', html, flags=re.IGNORECASE)
for tag in a_tags:
    if 'aria-label=' not in tag.lower():
        title_match = re.search(r'title=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if title_match:
            new_tag = tag[:-1] + f' aria-label="{title_match.group(1)}">'
        else:
            new_tag = tag[:-1] + ' aria-label="Social Link">'
        html = html.replace(tag, new_tag)

if '<meta name="description"' not in html:
    html = html.replace('</head>', '  <meta name="description" content="ACM VJIT Student Chapter - Fostering computing culture and technical excellence at VJIT.">\n</head>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Finished SEO and A11y adjustments")
