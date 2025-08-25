#!/usr/bin/env python3
import re
import os
import glob
import requests
import time
import json
from datetime import datetime

def load_env_file():
    """Načte proměnné ze souboru .env"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value

def read_markdown_file(filepath):
    """Načte markdown soubor a vrátí frontmatter a content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # oddělí frontmatter od obsahu
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
            return frontmatter, body
    
    return None, content

def write_markdown_file(filepath, frontmatter, body):
    """Zapíše markdown soubor s frontmatter a obsahem."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write(frontmatter)
        f.write('\n---\n\n')
        f.write(body)

def clean_content_for_ai(content):
    """Vyčistí markdown obsah pro AI analýzu."""
    # odstraní markdown formátování
    clean_content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # bold
    clean_content = re.sub(r'\*(.*?)\*', r'\1', clean_content)  # italic
    clean_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_content)  # links
    clean_content = re.sub(r'!\[.*?\]\(.*?\)', '', clean_content)  # images
    clean_content = re.sub(r'`(.*?)`', r'\1', clean_content)  # code
    clean_content = re.sub(r'#+\s*', '', clean_content)  # headers
    clean_content = re.sub(r'\n+', ' ', clean_content)  # newlines
    clean_content = clean_content.strip()
    
    # omez délku na rozumnou velikost pro API
    if len(clean_content) > 4000:
        clean_content = clean_content[:4000] + "..."
    
    return clean_content

def generate_excerpt_with_ai(title, content):
    """Vygeneruje excerpt pomocí OpenRouter API."""
    
    # OpenRouter API konfigurace - zkus různé názvy proměnných
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('openrouter_api_key')
    if not api_key:
        print("  Chyba: API klíč není nastaven v .env souboru (openrouter_api_key) nebo environment (OPENROUTER_API_KEY)!")
        return fallback_excerpt(title, content)
    
    clean_content = clean_content_for_ai(content)
    
    prompt = f"""Článek: {title}

{clean_content}

Vytvoř 3 až 4 věty souvislého textu jako souhrnu nejdůležitějších témat z tohoto článku. Jdi rovnou k věci, neprozrazuj, že jsi AI, buď stručný a věcný."""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://brandys.pirati.cz",
        "X-Title": "Brandys Piráti - Excerpt Generator"
    }
    
    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.3
    }
    
    # Retry logika pro rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 sekund
                    print(f"  Rate limit, čekám {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  Rate limit i po {max_retries} pokusech, používám fallback")
                    return fallback_excerpt(title, content)
            
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                excerpt = result['choices'][0]['message']['content'].strip()
                return excerpt
            else:
                print(f"  Varování: Neočekávaná odpověď API")
                return fallback_excerpt(title, content)
                
        except requests.exceptions.RequestException as e:
            print(f"  Chyba API (pokus {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return fallback_excerpt(title, content)
        except json.JSONDecodeError as e:
            print(f"  Chyba parsování JSON: {e}")
            return fallback_excerpt(title, content)
    
    return fallback_excerpt(title, content)

def fallback_excerpt(title, content):
    """Fallback excerpt pokud API selže."""
    clean_content = clean_content_for_ai(content)
    sentences = re.split(r'[.!?]+', clean_content)
    context = '. '.join([s.strip() for s in sentences[:3] if s.strip()])
    if len(context) > 200:
        context = context[:200] + "..."
    return f"Patrick Zandl ve svém newsletteru Místostarosti přináší pozorování z komunální politiky Brandýsa-Boleslavi. {context}"

def process_mistostarosti_files(limit=None):
    """Zpracuje všechny soubory Místostarosti a přidá excerpty."""
    posts_dir = "/Users/imac/Github/brandys-pirati/_posts/mistostarosti"
    
    if not os.path.exists(posts_dir):
        print(f"Adresář {posts_dir} neexistuje!")
        return
    
    # zkontroluj API klíč
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('openrouter_api_key')
    if not api_key:
        print("⚠️  OpenRouter API klíč není nastaven!")
        print("   Přidej do .env souboru: openrouter_api_key = 'your-key-here'")
        print("   Nebo nastav environment: export OPENROUTER_API_KEY='your-key-here'")
        print("   Script bude používat fallback funkce")
        
    markdown_files = glob.glob(os.path.join(posts_dir, "*.md"))
    
    # omez počet souborů pro testování
    if limit:
        markdown_files = markdown_files[:limit]
        print(f"Testovací režim: zpracovávám pouze {limit} souborů")
    
    processed = 0
    
    for filepath in markdown_files:
        print(f"Zpracovávám: {os.path.basename(filepath)}")
        
        frontmatter, body = read_markdown_file(filepath)
        if not frontmatter:
            print(f"  Přeskakuji - chybí frontmatter")
            continue
        
        # zkontroluj, jestli už má excerpt a jestli ho chceme přepsat
        force_regenerate = True  # změň na False, pokud nechceš přepisovat existující
        if 'excerpt:' in frontmatter and not force_regenerate:
            print(f"  Přeskakuji - už má excerpt")
            continue
        
        # najdi title v frontmatter
        title_match = re.search(r'title:\s*["\'](.+?)["\']', frontmatter)
        if not title_match:
            print(f"  Přeskakuji - nenalezen title")
            continue
        
        title = title_match.group(1)
        print(f"  Generuji excerpt pomocí AI...")
        excerpt = generate_excerpt_with_ai(title, body)
        
        # krátká pauza mezi API voláními (zvýšena kvůli free tier rate limits)
        time.sleep(3)
        
        # přidej nebo nahraď excerpt do frontmatter
        frontmatter_lines = frontmatter.split('\n')
        
        # zkontroluj, jestli už excerpt existuje
        excerpt_exists = False
        for i, line in enumerate(frontmatter_lines):
            if line.startswith('excerpt:'):
                # nahraď existující
                frontmatter_lines[i] = f'excerpt: "{excerpt}"'
                excerpt_exists = True
                break
        
        if not excerpt_exists:
            # najdi místo pro vložení excerpta (po title)
            insert_index = -1
            for i, line in enumerate(frontmatter_lines):
                if line.startswith('title:'):
                    insert_index = i + 1
                    break
            
            if insert_index > 0:
                frontmatter_lines.insert(insert_index, f'excerpt: "{excerpt}"')
            else:
                print(f"  Chyba - nenalezena pozice pro excerpt")
                continue
        
        new_frontmatter = '\n'.join(frontmatter_lines)
        
        # ulož soubor
        write_markdown_file(filepath, new_frontmatter, body)
        print(f"  ✓ {'Nahrazen' if excerpt_exists else 'Přidán'} AI excerpt")
        processed += 1
    
    print(f"\nZpracováno {processed} souborů")

if __name__ == "__main__":
    import sys
    
    # načti proměnné ze souboru .env
    load_env_file()
    
    print("Generuji AI excerpty pro články Místostarosti...")
    
    # možnost spustit pouze s několika soubory pro test
    limit = None
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        limit = 3
    
    process_mistostarosti_files(limit=limit)
    print("Hotovo!")