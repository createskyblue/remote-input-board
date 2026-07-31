from __future__ import annotations

import json
from pathlib import Path
from threading import Lock


def _text_char_count(text: str) -> int:
    return len([*text])


def count_text_history_chars(history_file_path: Path) -> int:
    total = 0
    if not history_file_path.exists():
        return total

    with history_file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("kind") == "text" and isinstance(item.get("text"), str):
                total += _text_char_count(item["text"])
    return total


class TextStatsStore:
    def __init__(self, stats_file_path: Path, initial_total_chars: int = 0):
        self.stats_file_path = stats_file_path
        self._lock = Lock()
        self.stats_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.stats_file_path.exists():
            self._write_total(max(0, int(initial_total_chars)))

    def get_total_chars(self) -> int:
        with self._lock:
            return self._read_total()

    def add_text(self, text: str) -> int:
        with self._lock:
            total = self._read_total() + _text_char_count(text)
            self._write_total(total)
            return total

    def save_total_chars(self, total: int) -> int:
        """Store a phone-reported cumulative total (server acts as a backup mirror)."""
        with self._lock:
            total = max(0, int(total))
            self._write_total(total)
            return total

    def _read_total(self) -> int:
        try:
            payload = json.loads(self.stats_file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0
        total = payload.get("totalChars", 0)
        return total if isinstance(total, int) and total > 0 else 0

    def _write_total(self, total: int) -> None:
        self.stats_file_path.write_text(
            json.dumps({"totalChars": total}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
