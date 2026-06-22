# Nexus Calc

[Česká verze](README.md)

Nexus Calc is a modern Python desktop calculator that combines standard and
scientific calculations, function plotting, currency and unit conversion,
calculation history, statistics, and multiple visual themes in one interface.

> This project demonstrates a modern desktop GUI built with `CustomTkinter`.

## Application preview

Comming Soon 

## Features

- standard and scientific calculations;
- safe expression processing without `eval()`;
- trigonometric functions in DEG and RAD modes;
- mathematical function plotting with Matplotlib;
- online currency conversion with cached and built-in offline fallbacks;
- length, mass, volume, speed, time, and temperature conversions;
- Dark, Light, and Neon themes;
- locally persisted calculation history;
- CSV history export;
- usage statistics grouped by operation type;
- button sound feedback;
- result animations;
- custom application icon and splash screen.

## Requirements

- Python 3.10 or newer;
- Windows, macOS, or Linux;
- an internet connection only for current currency exchange rates.

## Installation

Download or clone the project and enter its directory:

```powershell
cd 1-SmartCalculator
```

Optionally create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
py -m pip install -r requirements.txt
```

Run the application:

```powershell
py main.py
```

On macOS or Linux, use `python3` instead of `py` if required.

## Usage

Example expressions:

```text
2 + 3 * 4
sin(45) + sqrt(16)
log(1000)
fact(6)
2^10
```

Supported constants:

- `pi` or `π`;
- `e`;
- `tau`;
- `ans` for the previous result.

Keyboard shortcuts:

| Shortcut | Action |
|---|---|
| `Enter` | Calculate the expression |
| `Escape` | Clear the input |
| `Ctrl + L` | Focus the expression input |

## Currency exchange rates

Current exchange rates are provided by the public
[Frankfurter API](https://www.frankfurter.app/). If the service or internet
connection is unavailable, the application uses:

1. the latest cached rates when they are less than seven days old;
2. built-in approximate rates as a final fallback.

Offline rates may not match current market values and must not be used for
financial decisions.

## Local data

- calculation history is stored in `history.json`;
- the currency cache is created as `currency_cache.json`;
- both files are stored locally in the application directory;
- history can be exported to CSV from the application.

## Project structure

```text
1-SmartCalculator/
├── assets/
│   ├── nexus-calc.ico
│   └── nexus-calc-splash.png
├── docs/
│   └── screenshots/
├── calculator_engine.py   # safe calculation engine
├── converters.py          # currency and unit conversions
├── history_manager.py     # history, statistics, and CSV export
├── theme_manager.py       # application color themes
├── ui.py                  # graphical user interface
├── main.py                # application entry point
└── requirements.txt
```

## Troubleshooting

### Python cannot find a module

Make sure the dependencies were installed into the same Python environment
used to run the application:

```powershell
py -m pip install -r requirements.txt
```

### The graph is not displayed

Upgrade or reinstall Matplotlib:

```powershell
py -m pip install --upgrade matplotlib
```

### Currency conversion reports an offline rate

Check your internet connection and access to `api.frankfurter.app`.
The application remains functional and automatically uses fallback data.

## Technology

- Python
- CustomTkinter
- Tkinter
- Matplotlib
- Pillow
- Frankfurter API

## Possible future improvements

- a packaged Windows `.exe` release;
- user-defined themes;
- multiple functions in one graph;
- history import and synchronization;
- additional interface languages.

