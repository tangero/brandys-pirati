#!/usr/bin/env python3
import re
import os
import time
import urllib.parse
import pathlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

# ZÁKLADNÍ NASTAVENÍ
WAYBACK_START = "https://web.archive.org/web/20230330073311/https://www.piratibrandys.cz/"
OUT_DIR = "/Users/patrickzandl/Documents/GitHub/brandys-pirati/piratibrandys_markdown"
IMAGES_CSV = "/Users/patrickzandl/Documents/GitHub/brandys-pirati/extracted_images.csv"
ONLY_URL_REGEX = re.compile(r"/clanek/20")  # filtr článků

# selektory typické pro WordPress
TITLE_SEL = ["h1.entry-title", "h1"]
CONTENT_SEL = [
    "div.entry-content",
    "article .entry-content",
    "article .post-content",
    "article",
    "main",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PBL-archiver/1.0; +https://example.org)"
}

def absolutize(base, href):
    if not href:
        return None
    return urllib.parse.urljoin(base, href)

def get_soup(url, retries=5):
    """Stáhne stránku s retry logikou."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=120)  # zvýšeno z 30 na 120 sekund
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError) as e:
            print(f"    Pokus {attempt + 1}/{retries} selhal pro {url}: {e}")
            if attempt < retries - 1:
                wait_time = min(60, 5 * (2 ** attempt))  # exponential backoff, max 60 sekund
                print(f"    Čekám {wait_time} sekund před dalším pokusem...")
                time.sleep(wait_time)
            else:
                raise

def discover_archive_month_links(start_url):
    """Z homepage načte sekci 'Archivy' a vrátí jejich odkazy (Wayback URL)."""
    soup = get_soup(start_url)
    links = []
    # Vpravo je widget Archivy – hledej všechny odkazy obsahující /web/…/https://www.piratibrandys.cz/
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "web.archive.org" in href and "piratibrandys.cz" in href:
            # archivy mívají /category/… i /YYYY/MM… — vezmeme vše, projdeme a vyfiltrujeme až články
            if "/web/" in href:
                links.append(href)
    # deduplikace
    links = list(dict.fromkeys(links))
    return links

def discover_article_links(list_url):
    """Z libovolné stránky (seznam, archiv, štítky) vytáhne odkazy na články odpovídající filtru /clanek/20…"""
    soup = get_soup(list_url)
    found = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/clanek/" in href and ONLY_URL_REGEX.search(href):
            # uchovej plnou wayback URL (jak je), kvůli stabilitě a obsahu
            found.add(href)
    return found

def text_or_none(el):
    return el.get_text(strip=True) if el else None

def parse_czech_date(date_str):
    """Převede české datum z formátu DD.MM.YYYY na YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        # očistí mezery a parsuje
        clean_date = re.sub(r'\s+', '', date_str.strip())
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', clean_date)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None

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

def extract_images_from_content(content_node, base_url):
    """Vytáhne všechny obrázky z obsahu a vrátí jejich URL."""
    images = []
    for img in content_node.find_all("img"):
        src = img.get("src")
        if src:
            # absolutizuj URL
            abs_url = absolutize(base_url, src)
            if abs_url:
                images.append({
                    'url': abs_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
    return images

def create_jekyll_filename(title, date_str):
    """Vytvoří Jekyll filename ve formátu YYYY-MM-DD-nazev-clanku.md."""
    # parsuj datum
    jekyll_date = parse_czech_date(date_str)
    if not jekyll_date:
        # fallback na dnešní datum
        jekyll_date = datetime.now().strftime("%Y-%m-%d")
    
    # vytvoř slug z titulku
    if title:
        # nejprve odstraň diakritiku
        title_no_diacritics = remove_diacritics(title)
        slug = re.sub(r'[^\w\s-]', '', title_no_diacritics.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        slug = slug[:50]  # omez délku
    else:
        slug = "clanek"
    
    return f"{jekyll_date}-{slug}.md"

def extract_article(url):
    """Vytáhne titulek, datum, autora, obsah a obrázky."""
    soup = get_soup(url)

    # titulek
    title = None
    for sel in TITLE_SEL:
        h = soup.select_one(sel)
        if h:
            title = text_or_none(h)
            break
    if not title:
        # fallback: první h1
        h = soup.find("h1")
        title = text_or_none(h)

    # datum & autor – WordPress to často má poblíž title
    date = None
    author = None

    # zkus najít "Publikováno" a "Autor" u stejné stránky
    text = soup.get_text(" ", strip=True)
    # hrubé regexy (bez diakritiky i s diakritikou)
    m_date = re.search(r"Publikováno:\s*([0-9]{1,2}\.\s*[0-9]{1,2}\.\s*[0-9]{4})", text)
    if not m_date:
        m_date = re.search(r"([0-9]{1,2}\.\s*[0-9]{1,2}\.\s*[0-9]{4})", text)
    if m_date:
        date = m_date.group(1)

    m_author = re.search(r"Autor:\s*([A-Za-zÁÉÍÓÚÝČĎĚŇŘŠŤŽáéíóúýčďěňřšťž\-\s]+)", text)
    if m_author:
        author = m_author.group(1).strip()

    # obsah
    content_node = None
    for sel in CONTENT_SEL:
        node = soup.select_one(sel)
        if node:
            content_node = node
            break
    if not content_node:
        # fallback: vezmi hlavní <article>
        content_node = soup.find("article") or soup

    # odstraň komentáře formulář, navigace atp.
    for bad_sel in [
        "form", ".comment-respond", "#comments", ".comments-area",
        ".post-navigation", ".nav-links", "nav", "aside", "footer",
        ".wp-block-archives", ".widget_archive", ".widget"
    ]:
        for bad in content_node.select(bad_sel):
            bad.decompose()

    # vytáhni obrázky PŘED jejich odstraněním
    images = extract_images_from_content(content_node, url)

    # vyčistit obrázky (chceš „jen texty a URL")
    for img in content_node.find_all("img"):
        img.decompose()

    # převod na jednoduchý markdown-like text:
    # (aby nebyla závislost na extra balíčcích; prostý text s prázdnými řádky)
    paragraphs = []
    for p in content_node.find_all(["p", "li", "h2", "h3", "h4", "blockquote"]):
        txt = p.get_text(" ", strip=True)
        if txt:
            paragraphs.append(txt)

    body = "\n\n".join(paragraphs).strip()

    return {
        "title": title or "",
        "date": date or "",
        "author": author or "",
        "body": body or "",
        "images": images,
    }

def write_markdown(meta, wayback_url):
    pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # použij Jekyll konvenci názvu
    filename = create_jekyll_filename(meta["title"], meta["date"])
    dst = pathlib.Path(OUT_DIR) / filename
    
    # parsuj datum pro Jekyll frontmatter
    jekyll_date = parse_czech_date(meta["date"])
    if not jekyll_date:
        jekyll_date = datetime.now().strftime("%Y-%m-%d")
    
    # escapování uvozovek pro YAML
    title_escaped = meta["title"].replace('"', '\\"')
    author_escaped = meta["author"].replace('"', '\\"')
    
    frontmatter = [
        "---",
        "layout: post",
        f'title: "{title_escaped}"',
        f"date: {jekyll_date}",
        f'author: "{author_escaped}"',
        f'source_url: "{wayback_url}"',
        "---",
        "",
    ]
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter))
        f.write(meta["body"])
        f.write("\n")
    return str(dst)

def save_images_to_csv(images_data):
    """Uloží informace o obrázcích do CSV souboru."""
    with open(IMAGES_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['article_title', 'image_url', 'alt_text', 'title_text', 'article_source']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in images_data:
            writer.writerow(row)

def save_urls_to_file(urls, filename="urls_to_download.txt"):
    """Uloží seznam všech URL do textového souboru."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Seznam URL k stažení - celkem {len(urls)} článků\n")
        f.write(f"# Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for i, url in enumerate(urls, 1):
            f.write(f"{i:3d}. {url}\n")
    print(f"[*] Seznam {len(urls)} URL uložen do {filename}")

def append_url_to_file(url, filename="discovered_urls.txt"):
    """Připojí jednu URL do souboru s průběžnými výsledky."""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{url}\n")

def init_progress_files():
    """Inicializuje soubory pro průběžné ukládání."""
    # vymaž staré soubory průběhu
    for filename in ["discovered_urls.txt", "processed_articles.txt"]:
        if os.path.exists(filename):
            os.remove(filename)
    
    # vytvoř hlavičky
    with open("discovered_urls.txt", 'w', encoding='utf-8') as f:
        f.write(f"# Průběžně objevované URL - spuštěno {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    with open("processed_articles.txt", 'w', encoding='utf-8') as f:
        f.write(f"# Zpracované články - spuštěno {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_processed_article(title, url, filename="processed_articles.txt"):
    """Zaznamená zpracovaný článek."""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {title} - {url}\n")

def load_urls_from_file(filename="kestazeni.txt"):
    """Načte seznam URL ze souboru."""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # přeskočí prázdné řádky a komentáře
                    urls.append(line)
        print(f"[*] Načteno {len(urls)} URL ze souboru {filename}")
        return urls
    except FileNotFoundError:
        print(f"[!] Soubor {filename} nebyl nalezen!")
        return []

def main():
    # inicializuj soubory pro průběžné ukládání
    init_progress_files()
    
    # načti URL ze souboru místo hledání na webu
    print("[*] Načítám URL ze souboru kestazeni.txt…")
    urls_to_process = load_urls_from_file("kestazeni.txt")
    
    if not urls_to_process:
        print("[!] Žádné URL k zpracování!")
        return
    
    # ulož seznam URL do textového souboru (pro záznam)
    save_urls_to_file(urls_to_process, "urls_from_file.txt")
    
    # seznam pro obrázky
    all_images = []

    print(f"[*] Zpracovávám {len(urls_to_process)} článků...")
    for j, url in enumerate(urls_to_process, 1):
        try:
            meta = extract_article(url)
            path = write_markdown(meta, url)
            
            # zaznamenej zpracovaný článek
            log_processed_article(meta["title"], url)
            
            # přidej obrázky do seznamu
            for img in meta["images"]:
                all_images.append({
                    'article_title': meta["title"],
                    'image_url': img['url'],
                    'alt_text': img['alt'],
                    'title_text': img['title'],
                    'article_source': url
                })
            
            print(f"    [{j}/{len(urls_to_process)}] OK -> {path} ({len(meta['images'])} obrázků)")
            time.sleep(2.0)  # pauza mezi požadavky
        except Exception as e:
            print(f"    [{j}/{len(urls_to_process)}] CHYBA pro {url}: {e}")
            # zaznamenej i chybu
            log_processed_article(f"CHYBA: {e}", url)
    
    # ulož obrázky do CSV
    if all_images:
        save_images_to_csv(all_images)
        print(f"[*] Uloženo {len(all_images)} obrázků do {IMAGES_CSV}")
    else:
        print("[*] Žádné obrázky nebyly nalezeny.")
    
    print(f"[*] Dokončeno! Zpracováno {len(urls_to_process)} URL.")

if __name__ == "__main__":
    main()