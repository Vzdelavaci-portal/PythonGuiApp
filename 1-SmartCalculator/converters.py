"""Offline unit conversion and online currency conversion with cached fallback rates."""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path


UNITS = {
    "Délka": {
        "metr": 1.0, "kilometr": 1000.0, "centimetr": 0.01, "milimetr": 0.001,
        "míle": 1609.344, "yard": 0.9144, "stopa": 0.3048, "palec": 0.0254,
    },
    "Hmotnost": {
        "kilogram": 1.0, "gram": 0.001, "miligram": 0.000001,
        "tuna": 1000.0, "libra": 0.45359237, "unce": 0.028349523125,
    },
    "Objem": {
        "litr": 1.0, "mililitr": 0.001, "m³": 1000.0,
        "US galon": 3.785411784, "US pint": 0.473176473,
    },
    "Rychlost": {
        "m/s": 1.0, "km/h": 1 / 3.6, "mph": 0.44704, "uzel": 0.514444,
    },
    "Čas": {
        "sekunda": 1.0, "minuta": 60.0, "hodina": 3600.0,
        "den": 86400.0, "týden": 604800.0,
    },
}

TEMPERATURES = ("Celsius", "Fahrenheit", "Kelvin")


def convert_unit(category: str, value: float, source: str, target: str) -> float:
    if category == "Teplota":
        celsius = {
            "Celsius": lambda v: v,
            "Fahrenheit": lambda v: (v - 32) * 5 / 9,
            "Kelvin": lambda v: v - 273.15,
        }[source](value)
        return {
            "Celsius": lambda v: v,
            "Fahrenheit": lambda v: v * 9 / 5 + 32,
            "Kelvin": lambda v: v + 273.15,
        }[target](celsius)
    factors = UNITS[category]
    return value * factors[source] / factors[target]


class CurrencyService:
    CURRENCIES = ("CZK", "EUR", "USD", "GBP", "PLN", "CHF", "JPY", "CAD", "AUD")
    FALLBACK_EUR = {
        "EUR": 1.0, "CZK": 25.05, "USD": 1.08, "GBP": 0.85, "PLN": 4.28,
        "CHF": 0.96, "JPY": 164.0, "CAD": 1.47, "AUD": 1.65,
    }

    def __init__(self) -> None:
        self.cache_path = Path(__file__).with_name("currency_cache.json")

    def _load_rates(self) -> tuple[dict[str, float], str]:
        try:
            with urllib.request.urlopen(
                "https://api.frankfurter.app/latest?from=EUR", timeout=4
            ) as response:
                payload = json.load(response)
            rates = {"EUR": 1.0, **payload["rates"]}
            data = {"timestamp": time.time(), "rates": rates}
            self.cache_path.write_text(json.dumps(data), encoding="utf-8")
            return rates, f"Online kurz · {payload.get('date', 'dnes')}"
        except (OSError, ValueError, KeyError):
            try:
                cached = json.loads(self.cache_path.read_text(encoding="utf-8"))
                if time.time() - cached["timestamp"] < 7 * 86400:
                    return cached["rates"], "Offline · poslední uložený kurz"
            except (OSError, ValueError, KeyError, TypeError):
                pass
            return self.FALLBACK_EUR, "Offline · orientační kurz"

    def convert(self, value: float, source: str, target: str) -> tuple[float, str]:
        rates, status = self._load_rates()
        result = value / rates[source] * rates[target]
        return result, status
