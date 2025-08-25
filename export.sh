#!/bin/bash

# Export script pro stahování článků z Wayback Machine
# Pro macOS - automaticky nainstaluje závislosti a spustí export

set -e  # Ukončit při chybě

# Barvy pro výpis
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Export článků z Wayback Machine${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Kontrola, zda existuje Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 není nainstalován!${NC}"
    echo "Nainstaluj Python 3 pomocí Homebrew:"
    echo "  brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python nalezen: $PYTHON_VERSION"

# Kontrola, zda existuje soubor kestazeni.txt
if [ ! -f "kestazeni.txt" ]; then
    echo -e "${RED}❌ Soubor kestazeni.txt neexistuje!${NC}"
    echo "Vytvoř soubor kestazeni.txt s URL adresami k exportu."
    echo "Každá URL musí být na samostatném řádku."
    exit 1
fi

# Spočítej kolik je URL k zpracování
TOTAL_URLS=$(grep -v '^#' kestazeni.txt | grep -v '^$' | wc -l | tr -d ' ')
DONE_URLS=$(grep '^# DONE:' kestazeni.txt | wc -l | tr -d ' ')
ERROR_URLS=$(grep '^# ERROR:' kestazeni.txt | wc -l | tr -d ' ')
PENDING_URLS=$((TOTAL_URLS - DONE_URLS - ERROR_URLS))

echo -e "${YELLOW}📊 Statistika URL:${NC}"
echo "   Celkem:        $TOTAL_URLS"
echo "   Zpracováno:    $DONE_URLS"
echo "   S chybou:      $ERROR_URLS"
echo "   Čeká na zpracování: $PENDING_URLS"
echo ""

# Kontrola a vytvoření virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🔧 Vytváření virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment vytvořen"
else
    echo -e "${GREEN}✓${NC} Virtual environment již existuje"
fi

# Aktivace virtual environment
echo -e "${YELLOW}🔧 Aktivace virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}🔧 Aktualizace pip...${NC}"
pip install --quiet --upgrade pip

# Kontrola a instalace závislostí
echo -e "${YELLOW}🔧 Kontrola závislostí...${NC}"

DEPS_MISSING=false

# Kontrola requests
if ! python -c "import requests" 2>/dev/null; then
    echo "   - Instaluji requests..."
    pip install --quiet requests
    DEPS_MISSING=true
else
    echo -e "   ${GREEN}✓${NC} requests nainstalován"
fi

# Kontrola beautifulsoup4
if ! python -c "from bs4 import BeautifulSoup" 2>/dev/null; then
    echo "   - Instaluji beautifulsoup4..."
    pip install --quiet beautifulsoup4
    DEPS_MISSING=true
else
    echo -e "   ${GREEN}✓${NC} beautifulsoup4 nainstalován"
fi

if [ "$DEPS_MISSING" = false ]; then
    echo -e "${GREEN}✓${NC} Všechny závislosti jsou nainstalovány"
fi

# Vytvoření výstupního adresáře
if [ ! -d "export_wayback" ]; then
    echo -e "${YELLOW}🔧 Vytváření výstupního adresáře...${NC}"
    mkdir -p export_wayback
    echo -e "${GREEN}✓${NC} Adresář export_wayback vytvořen"
else
    echo -e "${GREEN}✓${NC} Výstupní adresář již existuje"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Spouštím export...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Spuštění export scriptu
python export.py

# Kontrola výsledku
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ Export dokončen úspěšně!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Zobraz statistiky výsledků
    if [ -f "export_wayback/processed_articles.txt" ]; then
        EXPORTED=$(grep -v '^#' export_wayback/processed_articles.txt | grep -v 'CHYBA' | wc -l | tr -d ' ')
        echo ""
        echo -e "${YELLOW}📁 Výsledky:${NC}"
        echo "   Exportované články: $EXPORTED"
        echo "   Umístění: export_wayback/"
        
        # Seznam souborů
        MD_FILES=$(ls -1 export_wayback/*.md 2>/dev/null | wc -l | tr -d ' ')
        if [ "$MD_FILES" -gt 0 ]; then
            echo "   Markdown soubory: $MD_FILES"
        fi
        
        # Info o obrázcích
        if [ -f "export_wayback/extracted_images.csv" ]; then
            IMG_COUNT=$(tail -n +2 export_wayback/extracted_images.csv | wc -l | tr -d ' ')
            echo "   Nalezené obrázky: $IMG_COUNT (uloženo v extracted_images.csv)"
        fi
    fi
else
    echo ""
    echo -e "${RED}❌ Export skončil s chybou${NC}"
    echo "Zkontroluj chybové hlášky výše."
    exit 1
fi

# Deaktivace virtual environment
deactivate

echo ""
echo -e "${YELLOW}💡 Tip:${NC}"
echo "   Pro opakované spuštění stačí zavolat: ./export.sh"
echo "   Script automaticky přeskočí již zpracované URL."
echo ""