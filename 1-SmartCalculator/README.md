# Nexus Calc

[English version](README.en.md)

Moderní desktopová kalkulačka vytvořená v Pythonu. Kombinuje běžné a vědecké
výpočty, vykreslování funkcí, převody měn a jednotek, historii výpočtů
a několik vizuálních motivů v jednom rozhraní.

> Projekt je určený jako ukázka moderní GUI aplikace postavené na
> `CustomTkinter`.

## Náhled aplikace

V přípravě

## Funkce

- standardní a vědecké matematické výpočty;
- bezpečné zpracování výrazů bez použití `eval()`;
- trigonometrické funkce v režimech DEG a RAD;
- vykreslování matematických funkcí pomocí Matplotlib;
- online převod měn s uloženou a orientační offline zálohou;
- převody délky, hmotnosti, objemu, rychlosti, času a teploty;
- motivy Dark, Light a Neon;
- historie výpočtů uložená lokálně;
- export historie do CSV;
- statistiky podle typu provedené operace;
- zvuková odezva tlačítek;
- animace výsledku;
- vlastní ikona a splash screen.

## Požadavky

- Python 3.10 nebo novější;
- operační systém Windows, macOS nebo Linux;
- internetové připojení pouze pro načtení aktuálních měnových kurzů.

## Instalace

Naklonuj nebo stáhni projekt a přejdi do jeho složky:

```powershell
cd 1-SmartCalculator
```

Volitelně vytvoř virtuální prostředí:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nainstaluj závislosti:

```powershell
py -m pip install -r requirements.txt
```

Spusť aplikaci:

```powershell
py main.py
```

Na macOS nebo Linuxu může být místo příkazu `py` potřeba použít `python3`.

## Použití

Do vstupního pole lze zapisovat například:

```text
2 + 3 * 4
sin(45) + sqrt(16)
log(1000)
fact(6)
2^10
```

Podporované konstanty:

- `pi` nebo `π`;
- `e`;
- `tau`;
- `ans` pro poslední výsledek.

Klávesové zkratky:

| Zkratka | Akce |
|---|---|
| `Enter` | Vypočítat výraz |
| `Escape` | Vymazat vstup |
| `Ctrl + L` | Zaměřit vstupní pole |

## Měnové kurzy

Aktuální kurzy poskytuje veřejné
[Frankfurter API](https://www.frankfurter.app/). Pokud služba nebo internetové
připojení nejsou dostupné, aplikace použije:

1. poslední uložené kurzy, pokud nejsou starší než sedm dní;
2. vestavěné orientační kurzy jako poslední zálohu.

Offline kurzy proto nemusí odpovídat aktuální tržní hodnotě a nejsou vhodné
pro finanční rozhodování.

## Ukládání dat

- historie se ukládá do `history.json`;
- měnová cache se vytváří jako `currency_cache.json`;
- oba soubory vznikají lokálně ve složce aplikace;
- historie může být z aplikace exportována do CSV.

## Struktura projektu

```text
1-SmartCalculator/
├── assets/
│   ├── nexus-calc.ico
│   └── nexus-calc-splash.png
├── docs/
│   └── screenshots/
├── calculator_engine.py   # bezpečné matematické jádro
├── converters.py          # převody měn a jednotek
├── history_manager.py     # historie, statistiky a CSV
├── theme_manager.py       # barevné motivy
├── ui.py                  # uživatelské rozhraní
├── main.py                # vstupní bod aplikace
└── requirements.txt
```

## Řešení problémů

### Python nenajde modul

Ověř, že byly závislosti nainstalovány do stejného prostředí, ze kterého
aplikaci spouštíš:

```powershell
py -m pip install -r requirements.txt
```

### Graf se nezobrazí

Přeinstaluj Matplotlib:

```powershell
py -m pip install --upgrade matplotlib
```

### Převod měn používá offline kurz

Zkontroluj připojení k internetu a dostupnost `api.frankfurter.app`.
Aplikace se v tomto stavu nezastaví, pouze přejde na záložní data.

## Použité technologie

- Python
- CustomTkinter
- Tkinter
- Matplotlib
- Pillow
- Frankfurter API

## Další možné rozšíření

- balíček pro Windows ve formátu `.exe`;
- vlastní uživatelské motivy;
- více funkcí v jednom grafu;
- import a synchronizace historie;
- lokalizace rozhraní do více jazyků.

