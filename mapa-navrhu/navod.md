---
layout: page
title: Návod k mapě návrhů
---

# Návod k používání mapy návrhů

## Pro veřejnost - zobrazení návrhů

### Jak procházet mapu
1. **Otevřete [Mapu návrhů](/mapa-navrhu/)**
2. **Ovládání mapy:**
   - Myš: tažení pro posunutí, kolečko pro zoom
   - Touch: gesta pro posunutí a zoom
   - Tlačítka: 🎯 Brandýs pro vycentrování

### Filtry a vyhledávání
- **Status návrhu:** Filtrování podle fáze realizace
- **Kategorie:** Typ návrhu (infrastruktura, zeleň, doprava...)
- **Vyhledávání:** Fulltextové vyhledání v názvech a popisech

### Značky na mapě
- 🔵 **Návrh** - nová myšlenka
- 🟡 **Schváleno** - rada/zastupitelstvo schválilo
- 🟣 **V realizaci** - probíhá implementace
- 🟢 **Hotovo** - dokončeno
- 🔴 **Zamítnuto** - návrh byl odmítnut

### Typy označení
- **📍 Bod** - konkrétní místo (lavička, zastávka)
- **➖ Linie** - cesta nebo trasa (cyklistická stezka)
- **🔷 Polygon** - oblast (park, parkoviště)

## Pro editory - vytváření návrhů

### Přístup do editoru
1. Otevřete [Editor návrhů](/mapa-navrhu/editor/)
2. Zadejte heslo pro přístup
3. Heslo získáte od správce webu

### Vytvoření nového návrhu

#### 1. Označení na mapě
1. **Vyberte nástroj kreslení:**
   - 📍 **Bod** - pro konkrétní místa
   - ➖ **Linie** - pro cesty (klikat body, dvojklik = konec)
   - 🔷 **Oblast** - pro plochy (klikar rohy, dvojklik = konec)

2. **Označte místo na mapě** podle vybraného nástroje

3. **Katastrální podklad** - zobrazuje parcely a budovy

#### 2. Vyplnění formuláře
**Povinné údaje:**
- Název návrhu
- Autor návrhu  
- Kategorie
- Popis

**Volitelné údaje:**
- Status (výchozí: Návrh)
- Rozpočet
- Adresa (doplní se automaticky)

#### 3. Export
- **💾 Vygenerovat .md soubor** - stáhne Markdown pro web
- **👁️ Náhled** - ukáže jak bude vypadat
- **🔄 Vymazat vše** - reset formuláře

### Umístění souborů
Vygenerovaný `.md` soubor vložte do složky `_proposals/` v GitHub repozitáři.

### Publikování
Po commitu do GitHub se návrh automaticky zobrazí na webu.

## Kategorie návrhů

- 🏗️ **Infrastruktura** - silnice, chodníky, inženýrské sítě
- 🌳 **Veřejná zeleň** - parky, stromy, květinové záhony  
- 🚌 **Doprava** - MHD, parkoviště, cyklistika
- 🎮 **Sportoviště** - hřiště, tělocvična, fitness
- 🏢 **Veřejné budovy** - školy, úřady, kulturní zařízení
- 💡 **Smart city** - digitalizace, WiFi, elektronické služby
- ♻️ **Životní prostředí** - odpady, energetika, ekologie

## Workflow návrhů

```
🔵 Návrh → 🟡 Schváleno → 🟣 V realizaci → 🟢 Hotovo
           ↘️ 🔴 Zamítnuto
```

## Technické informace

- **Mapa:** OpenStreetMap + katastrální vrstva ČÚZK
- **Souřadnicový systém:** WGS84 (GPS)
- **Podporované formáty:** Point, LineString, Polygon
- **Export:** Markdown s YAML front matter
- **Integrace:** Jekyll static site generator

## Kontakt

Při problémech s mapou kontaktujte správce webu.