#!/usr/bin/env python3
import re
import os
import csv
import pathlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse
import time
import hashlib

# ZÁKLADNÍ NASTAVENÍ
SUBSTACK_DIR = "/Users/patrickzandl/Documents/GitHub/brandys-pirati/substack"
POSTS_DIR = "/Users/patrickzandl/Documents/GitHub/brandys-pirati/_posts/mistostarosti"
ASSETS_DIR = "/Users/patrickzandl/Documents/GitHub/brandys-pirati/assets/mistostarosti"
POSTS_CSV = os.path.join(SUBSTACK_DIR, "posts.csv")
POSTS_HTML_DIR = os.path.join(SUBSTACK_DIR, "posts")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Jekyll-converter/1.0)"
}

def remove_diacritics(text):
    """Odstraní diakritiku z textu."""
    diacritic_map = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ā': 'a', 'ă': 'a', 'ą': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e', 'ē': 'e', 'ě': 'e', 'ę': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i', 'ī': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'ō': 'o', 'ø': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u', 'ū': 'u', 'ů': 'u',
        'ý': 'y', 'ÿ': 'y',
        'č': 'c', 'ć': 'c', 'ç': 'c',
        'ď': 'd',
        'ň': 'n', 'ñ': 'n',
        'ř': 'r',
        'š': 's', 'ś': 's',
        'ť': 't',
        'ž': 'z', 'ź': 'z', 'ż': 'z',
        'ľ': 'l', 'ł': 'l',
        # velká písmena
        'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A', 'Ā': 'A', 'Ă': 'A', 'Ą': 'A',
        'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E', 'Ē': 'E', 'Ě': 'E', 'Ę': 'E',
        'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I', 'Ī': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O', 'Ō': 'O', 'Ø': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U', 'Ū': 'U', 'Ů': 'U',
        'Ý': 'Y', 'Ÿ': 'Y',
        'Č': 'C', 'Ć': 'C', 'Ç': 'C',
        'Ď': 'D',
        'Ň': 'N', 'Ñ': 'N',
        'Ř': 'R',
        'Š': 'S', 'Ś': 'S',
        'Ť': 'T',
        'Ž': 'Z', 'Ź': 'Z', 'Ż': 'Z',
        'Ľ': 'L', 'Ł': 'L'
    }
    
    result = ''
    for char in text:
        result += diacritic_map.get(char, char)
    return result

def create_filename_from_title(title, date_str):
    """Vytvoří Jekyll filename ve formátu YYYY-MM-DD-nazev.md."""
    # parsuj datum z ISO formátu
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        jekyll_date = date_obj.strftime("%Y-%m-%d")
    except:
        jekyll_date = datetime.now().strftime("%Y-%m-%d")
    
    # vytvoř slug z titulku
    if title:
        title_no_diacritics = remove_diacritics(title)
        slug = re.sub(r'[^\w\s-]', '', title_no_diacritics.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        slug = slug[:50]  # omez délku
    else:
        slug = "mistostarosti"
    
    return f"{jekyll_date}-{slug}.md"

def download_image(img_url, filename):
    """Stáhne obrázek a uloží do assets/mistostarosti."""
    try:
        response = requests.get(img_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # vytvoř adresář pokud neexistuje
        os.makedirs(ASSETS_DIR, exist_ok=True)
        
        # ulož soubor
        filepath = os.path.join(ASSETS_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return f"/assets/mistostarosti/{filename}"
    except Exception as e:
        print(f"    Chyba při stahování obrázku {img_url}: {e}")
        return img_url  # vrať původní URL pokud se nepodařilo stáhnout

def process_images_in_html(soup, post_title):
    """Zpracuje obrázky v HTML a stáhne je do assets."""
    images = soup.find_all('img')
    
    for img in images:
        src = img.get('src')
        if src and ('substack-post-media.s3.amazonaws.com' in src or 'substackcdn.com' in src):
            # vytvoř název souboru bez diakritiky
            title_slug = remove_diacritics(post_title.lower())
            title_slug = re.sub(r'[^\w-]', '', title_slug)[:30]
            
            # vytvoř hash z URL pro jedinečnost
            url_hash = hashlib.md5(src.encode()).hexdigest()[:8]
            
            # zjisti příponu
            parsed_url = urllib.parse.urlparse(src)
            path = parsed_url.path
            ext = '.jpg'  # defaultní
            if '.' in path:
                ext = os.path.splitext(path)[1]
                if not ext:
                    ext = '.jpg'
            
            filename = f"{title_slug}-{url_hash}{ext}"
            
            # stáhni obrázek
            local_path = download_image(src, filename)
            
            # aktualizuj src v HTML
            img['src'] = local_path
            
            # odstraň všechny srcset atributy (obsahují externí URL)
            if img.get('srcset'):
                del img['srcset']
            
            print(f"    Obrázek stažen: {filename}")

def convert_table_to_markdown(table):
    """Převede HTML tabulku na Markdown."""
    rows = []
    
    # Najdi všechny řádky
    table_rows = table.find_all("tr")
    if not table_rows:
        return ""
    
    # Zpracuj řádky
    for i, row in enumerate(table_rows):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
            
        # Získej text z buněk
        cell_texts = []
        for cell in cells:
            # Rekurzivně zpracuj obsah buněk (může obsahovat odkazy, formátování)
            cell_text = ''.join(convert_element_to_markdown(child) for child in cell.children)
            if not cell_text.strip():
                cell_text = cell.get_text(" ", strip=True)
            # Escape pipes pro Markdown a vyčisti
            cell_text = cell_text.replace("|", "\\|").strip()
            cell_texts.append(cell_text)
        
        # Vytvoř řádek tabulky
        if cell_texts:
            row_md = "| " + " | ".join(cell_texts) + " |"
            rows.append(row_md)
            
            # Po prvním řádku (hlavička) přidej oddělovač
            if i == 0:
                separator = "| " + " | ".join(["---"] * len(cell_texts)) + " |"
                rows.append(separator)
    
    return "\n" + "\n".join(rows) + "\n" if rows else ""

def convert_element_to_markdown(element):
    """Rekurzivně konvertuje HTML element na markdown."""
    if element.name is None:  # text node
        return str(element)
    
    # inline elementy - zachovej formátování s mezerami
    if element.name == 'strong' or element.name == 'b':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        return f" **{inner_text.strip()}** "
    
    elif element.name == 'em' or element.name == 'i':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        return f" *{inner_text.strip()}* "
    
    elif element.name == 'a':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        href = element.get('href', '')
        if href and inner_text:
            return f" [{inner_text.strip()}]({href}) "
        else:
            return inner_text
    
    elif element.name == 'code':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        return f" `{inner_text.strip()}` "
    
    # block elementy
    elif element.name == 'p':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        return inner_text.strip()
    
    elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(element.name[1])
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        return '#' * level + ' ' + inner_text.strip()
    
    elif element.name == 'blockquote':
        inner_text = ''.join(convert_element_to_markdown(child) for child in element.children)
        lines = inner_text.strip().split('\n')
        quoted_lines = ['> ' + line for line in lines if line.strip()]
        return '\n'.join(quoted_lines)
    
    elif element.name == 'ul':
        items = []
        for li in element.find_all('li', recursive=False):
            item_text = ''.join(convert_element_to_markdown(child) for child in li.children)
            if item_text.strip():
                items.append(f"- {item_text.strip()}")
        return '\n'.join(items)
    
    elif element.name == 'ol':
        items = []
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            item_text = ''.join(convert_element_to_markdown(child) for child in li.children)
            if item_text.strip():
                items.append(f"{i}. {item_text.strip()}")
        return '\n'.join(items)
    
    elif element.name == 'br':
        return '\n'
    
    # zpracování tabulek
    elif element.name == 'table':
        return convert_table_to_markdown(element)
    
    # ignoruj inline styling elementy, ale zachovej obsah
    elif element.name in ['span', 'div']:
        return ''.join(convert_element_to_markdown(child) for child in element.children)
    
    # pro neznámé elementy vrať pouze text obsah
    else:
        return ''.join(convert_element_to_markdown(child) for child in element.children)

def convert_html_to_markdown(html_content):
    """Konvertuje Substack HTML na Jekyll markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # odstraň nepotřebné elementy
    try:
        elements_to_remove = []
        for element in soup.find_all(['div', 'span']):
            if element and hasattr(element, 'get') and element.get('class'):
                classes = element.get('class', [])
                if any(cls in str(classes) for cls in ['poll-embed', 'pencraft', 'image-link-expand', 'button-wrapper']):
                    elements_to_remove.append(element)
        
        for element in elements_to_remove:
            element.decompose()
    except Exception as e:
        print(f"    Chyba při čištění HTML: {e}")
        pass
    
    # konvertuj strukturované elementy
    markdown_parts = []
    content_found = False
    
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'ul', 'ol', 'figure', 'table']):
        try:
            if element.name == 'figure':
                # speciální zpracování obrázků
                img = element.find('img')
                if img and img.get('src'):
                    alt_text = img.get('alt', '') or ''
                    src = img.get('src', '')
                    
                    # najdi caption
                    caption = ''
                    figcaption = element.find('figcaption')
                    if figcaption:
                        caption = figcaption.get_text().strip()
                    
                    # vytvoř markdown pro obrázek
                    if caption:
                        markdown_parts.append(f"![{alt_text}]({src})")
                        markdown_parts.append(f"*{caption}*")
                    else:
                        markdown_parts.append(f"![{alt_text}]({src})")
                    content_found = True
            
            elif element.name == 'table':
                # speciální zpracování tabulek
                table_markdown = convert_table_to_markdown(element)
                if table_markdown.strip():
                    markdown_parts.append(table_markdown)
                    content_found = True
            
            else:
                # použij rekurzivní konverzi
                markdown_text = convert_element_to_markdown(element)
                if markdown_text.strip():
                    # filtruj spam obsah
                    if not any(skip in markdown_text.lower() for skip in ['leave a comment', 'subscribe']):
                        markdown_parts.append(markdown_text)
                        content_found = True
        
        except Exception as e:
            print(f"    Chyba při zpracování elementu {element.name}: {e}")
            continue
    
    # pokud nebyly nalezeny strukturované elementy, použij prostý text
    if not content_found or not markdown_parts:
        text = soup.get_text().strip()
        if text:
            text = re.sub(r'\s+', ' ', text)
            markdown_parts.append(text)
    
    # zkombinuj s odstavci
    if markdown_parts:
        markdown_content = '\n\n'.join(markdown_parts)
    else:
        markdown_content = soup.get_text().strip()
    
    # vyčisti nadbytečné prázdné řádky a mezery
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
    # vyčisti duplicitní mezery ale zachovej jednu mezeru kolem formátování
    markdown_content = re.sub(r'  +', ' ', markdown_content)
    # vyčisti mezery na začátku a konci řádků
    lines = markdown_content.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    markdown_content = '\n'.join(cleaned_lines)
    
    return markdown_content.strip()

def load_posts_metadata():
    """Načte metadata příspěvků z CSV."""
    posts = {}
    
    try:
        with open(POSTS_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                post_id = row['post_id']
                if post_id and row['is_published'] == 'true':
                    posts[post_id] = row
        
        print(f"[*] Načteno {len(posts)} publikovaných příspěvků z CSV")
        return posts
    
    except FileNotFoundError:
        print(f"[!] Soubor {POSTS_CSV} nebyl nalezen!")
        return {}

def process_post(post_id, metadata):
    """Zpracuje jeden příspěvek."""
    # najdi odpovídající HTML soubor
    html_files = [f for f in os.listdir(POSTS_HTML_DIR) 
                  if f.startswith(post_id.split('.')[0]) and f.endswith('.html')]
    
    if not html_files:
        print(f"    HTML soubor pro {post_id} nenalezen")
        return False
    
    html_file = html_files[0]
    html_path = os.path.join(POSTS_HTML_DIR, html_file)
    
    try:
        # načti HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # zpracuj obrázky (stáhni je)
        try:
            process_images_in_html(soup, metadata['title'])
        except Exception as img_error:
            print(f"    Varování: Chyba při zpracování obrázků: {img_error}")
        
        # konvertuj na markdown
        try:
            markdown_content = convert_html_to_markdown(str(soup))
        except Exception as md_error:
            print(f"    Varování: Chyba při konverzi markdown, používám prostý text: {md_error}")
            # fallback na prostý text
            markdown_content = soup.get_text().strip()
        
        # vytvoř Jekyll frontmatter
        title = metadata.get('title', '') or 'Místostarosti'
        subtitle = metadata.get('subtitle', '') or ''
        date_str = metadata.get('post_date', '')
        
        # parsuj datum
        try:
            if date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                jekyll_date = date_obj.strftime("%Y-%m-%d")
                jekyll_datetime = date_obj.strftime("%Y-%m-%d %H:%M:%S %z")
            else:
                jekyll_date = datetime.now().strftime("%Y-%m-%d")
                jekyll_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
        except Exception as date_error:
            print(f"    Varování: Chyba při parsování data: {date_error}")
            jekyll_date = datetime.now().strftime("%Y-%m-%d")
            jekyll_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
        
        # vytvoř název souboru
        filename = create_filename_from_title(title, date_str or jekyll_date)
        
        # vytvoř Jekyll frontmatter
        frontmatter = [
            "---",
            "layout: post",
            f'title: "{title.replace('"', '\\"')}"',
            f"date: {jekyll_datetime}",
            f'author: "Patrick Zandl"',
            f'category: "mistostarosti"'
        ]
        
        if subtitle:
            frontmatter.append(f'subtitle: "{subtitle.replace('"', '\\"')}"')
        
        # přidej odkaz na první obrázek jako náhled pro titulní stránku
        # najdi první obrázek v HTML a zjisti jeho lokální cestu
        first_image_path = None
        try:
            first_img = soup.find('img')
            if first_img and first_img.get('src'):
                src = first_img.get('src')
                if src.startswith('/assets/mistostarosti/'):
                    first_image_path = src
        except:
            pass
        
        if first_image_path:
            frontmatter.append(f'image: {first_image_path}')
        
        frontmatter.extend([
            f'source: "substack"',
            f'source_id: "{post_id}"',
            "---",
            ""
        ])
        
        # ulož markdown soubor
        os.makedirs(POSTS_DIR, exist_ok=True)
        output_path = os.path.join(POSTS_DIR, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(frontmatter))
            f.write(markdown_content)
        
        print(f"    ✓ {filename}")
        return True
        
    except Exception as e:
        print(f"    ✗ Chyba při zpracování {post_id}: {e}")
        import traceback
        print(f"    Debug info: {traceback.format_exc()}")
        return False

def main():
    print("[*] Konvertuji Substack příspěvky na Jekyll markdown...")
    
    # načti metadata
    posts_metadata = load_posts_metadata()
    
    if not posts_metadata:
        print("[!] Žádná metadata k zpracování!")
        return
    
    # zpracuj příspěvky
    processed = 0
    failed = 0
    
    for post_id, metadata in posts_metadata.items():
        print(f"[{processed + failed + 1}/{len(posts_metadata)}] {metadata['title'][:50]}...")
        
        if process_post(post_id, metadata):
            processed += 1
        else:
            failed += 1
        
        # krátká pauza mezi požadavky
        time.sleep(0.5)
    
    print(f"\n[*] Dokončeno!")
    print(f"    ✓ Úspěšně zpracováno: {processed} příspěvků")
    print(f"    ✗ Chyby: {failed} příspěvků")
    print(f"    📁 Soubory uloženy do: {POSTS_DIR}")
    print(f"    🖼️ Obrázky uloženy do: {ASSETS_DIR}")

if __name__ == "__main__":
    main()