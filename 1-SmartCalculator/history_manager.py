"""Persistent calculation history and aggregate statistics."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


class HistoryManager:
    def __init__(self, file_name: str | Path | None = None) -> None:
        self.file_path = Path(file_name) if file_name else Path(__file__).with_name("history.json")
        self.history: list[dict[str, str]] = []
        self._load()

    def _load(self) -> None:
        if not self.file_path.exists():
            return
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self.history = data
        except (OSError, json.JSONDecodeError):
            self.history = []

    def _save(self) -> None:
        self.file_path.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def add(self, expression: str, result: str, category: str = "Výpočet") -> None:
        self.history.append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "category": category,
                "expression": expression,
                "result": str(result),
            }
        )
        self._save()

    def get_last(self, limit: int = 50) -> list[dict[str, str]]:
        return list(reversed(self.history[-limit:]))

    def clear(self) -> None:
        self.history = []
        self._save()

    def export_csv(self, target: str | Path) -> None:
        with Path(target).open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(
                file, fieldnames=("time", "category", "expression", "result")
            )
            writer.writeheader()
            writer.writerows(self.history)

    def statistics(self) -> dict[str, object]:
        categories = Counter(item.get("category", "Výpočet") for item in self.history)
        return {
            "total": len(self.history),
            "today": sum(item.get("time", "")[:10] == datetime.now().date().isoformat() for item in self.history),
            "categories": categories,
        }
