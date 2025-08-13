# Generování AI excerptů pro články Místostarosti

Tento script vygeneruje kvalitní souhrny článků pomocí AI prostřednictvím OpenRouter API.

## Instalace

```bash
# Aktivuj virtual environment
source venv/bin/activate

# Ujisti se, že máš nainstalované závislosti
pip install requests beautifulsoup4
```

## Nastavení API klíče

1. Jdi na [OpenRouter.ai](https://openrouter.ai/) a vytvoř si účet
2. Vygeneruj API klíč
3. Přidej ho do `.env` souboru v root adresáři:

```
openrouter_api_key = sk-or-v1-your-key-here
```

Nebo alternativně nastav jako environment proměnnou:
```bash
export OPENROUTER_API_KEY='sk-or-v1-your-key-here'
```

## Použití

### Vygenerování všech excerptů
```bash
python3 generate_excerpts.py
```

### Testovací režim (pouze 3 soubory)
```bash
python3 generate_excerpts.py --test
```

## Jak to funguje

1. Script projde všechny `.md` soubory v `/Users/patrickzandl/Documents/GitHub/brandys-pirati/_posts/mistostarosti/`
2. Pro každý článek:
   - Vyčistí markdown formátování
   - Pošle obsah článku do AI (DeepSeek Chat v3 via OpenRouter)
   - Použije prompt: "Vytvoř 3 až 4 věty souhrnu nejdůležitějších témat z tohoto článku. Jdi rovnou k věci, neprozrazuj, že jsi AI, buď stručný a věcný."
   - Přidá/nahradí `excerpt:` pole v YAML hlavičce článku

3. Má retry logiku pro rate limiting (3s pauza mezi požadavky, až 3 pokusy)
4. Pokud API klíč není nastaven nebo API selže, použije se fallback funkce

## Cena

- DeepSeek Chat v3 přes OpenRouter: **ZDARMA** (free tier)
- Pro 64 článků: $0.00

## Výsledek

Každý článek bude mít v YAML hlavičce kvalitní excerpt:

```yaml
---
title: "Článek o dopravě"
excerpt: "Patrick Zandl analyzuje dopravní situaci v Brandýse-Boleslavi po dokončení rekonstrukce hlavní silnice. Článek se zabývá dopadem na místní obchody a potřebou nových parkovacích míst. Diskutuje také o plánované cyklostezce a jejím přínosu pro obyvatele města."
---
```