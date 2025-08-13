# Analýza nepoužívaných souborů šablon v Jekyll projektu

## Proces analýzy

1. **Analýza layoutů**: Prohledány všechny references v front matter, `_config.yml` a layout dědičnost
2. **Analýza includes**: Prohledány všechny `{% include %}` direktivy v HTML souborech  
3. **Analýza SCSS**: Prohledány všechny `@import` direktivy v SASS souborech
4. **Křížová reference**: Identifikovány soubory, které se používají pouze z jiných nepoužívaných souborů

## Výsledky

### Přesunuté nepoužívané soubory do `/smazat/`

#### Layouty (4 soubory):
- `compress.html` - layout pro komprese HTML (nepoužívaný)
- `landing.html` - landing page layout (nepoužívaný)  
- `redirected.html` - layout pro redirecty (nepoužívaný)
- `team.html` - layout pro týmy (nepoužívaný)

#### Includes (22 souborů):
- **accordeon/** (2 soubory)
  - `accordeon-column.html` - nepoužívaný
  - `accordeon.html` - používaný jen z accordeon-column.html
- **article-list/** (4 soubory) 
  - `featured_article.html` - nepoužívaný
  - `list-3col.html` - nepoužívaný
  - `pagination.html` - nepoužívaný
  - `standard_article.html` - používaný jen z list-3col.html
- **root level** (2 soubory)
  - `footer.html` - starý footer, nahrazen footer-md3.html
  - `header.html` - starý header, nahrazen header-md3.html
- **js/** (2 soubory)
  - `ga.js` - Google Analytics (nepoužívaný)
  - `gtm-head.html` - Google Tag Manager head (nepoužívaný)
- **kontakt/** (1 soubor)
  - `contact-card.html` - nepoužívaný
- **page/** (1 soubor) 
  - `relatives.html` - nepoužívaný
- **people/** (5 souborů)
  - `carousel.html` - nepoužívaný
  - `kandidat-small.html` - nepoužívaný
  - `kandidat.html` - nepoužívaný
  - `list-2col.html` - nepoužívaný  
  - `profiles.html` - nepoužívaný
- **right-bar/** (1 soubor)
  - `social-bar.html` - nepoužívaný
- **team/** (3 soubory)
  - `card.html` - nepoužívaný
  - `item.html` - používaný jen z list-3col.html
  - `list-3col.html` - nepoužívaný
- **title/** (1 soubor)
  - `title_header.html` - nepoužívaný

#### SASS (1 soubor):
- `_sprites.scss` - nepoužívaný sprite soubor

## Celkový souhrn

- **Celkem analyzovaných souborů**: ~100+ šablon a stylů
- **Identifikovaných nepoužívaných souborů**: 27
- **Všechny nepoužívané soubory přesunuty do**: `/smazat/` se zachováním původní adresářové struktury

## Bezpečnostní přístup

- Žádné soubory nebyly smazány definitivně
- Všechny nepoužívané soubory jsou dostupné v `/smazat/` pro případné obnovení
- Zachována původní adresářová struktura pro snadnou orientaci
- Pokud se ukáže, že některý soubor je přece jen potřeba, lze ho snadno vrátit zpět

## Doporučení

1. Otestovat web po změnách, zda všechno funguje správně
2. Po ověření funkčnosti lze adresář `/smazat/` později smazat definitivně
3. V případě problémů lze kterékoli soubory rychle obnovit z `/smazat/`