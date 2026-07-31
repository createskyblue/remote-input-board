from __future__ import annotations

import json
from pathlib import Path
import threading
import time


def _text_char_count(text: str) -> int:
    return len([*text])


def count_text_history_chars(history_dir: Path) -> int:
    """Sum the text chars across every history file under a history directory."""
    total = 0
    if not history_dir.exists():
        return total
    for path in sorted(history_dir.rglob("*.log")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if item.get("kind") == "text" and isinstance(item.get("text"), str):
                    total += _text_char_count(item["text"])
    return total


class TextStatsStore:
    """Cumulative char count, cached in memory and flushed to disk periodically.

    The value only ever grows, so the server acts as a backup mirror of the
    phone's count; disk writes are batched (default every 5 minutes) instead of
    happening on every send.
    """

    def __init__(self, stats_file_path: Path, initial_total_chars: int = 0, flush_interval: float = 300.0):
        self.stats_file_path = stats_file_path
        self._flush_interval = flush_interval
        self._lock = threading.Lock()
        self.stats_file_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache = max(0, int(initial_total_chars))
        if self.stats_file_path.exists():
            self._cache = max(self._cache, self._read_total())
        else:
            self._write_total(self._cache)
        self._dirty = False
        self._last_flush = time.monotonic()
        if flush_interval > 0:
            self._start_flusher()

    def get_total_chars(self) -> int:
        with self._lock:
            self._flush_if_due()
            return self._cache

    def add_text(self, text: str) -> int:
        with self._lock:
            self._cache += _text_char_count(text)
            self._dirty = True
            self._flush_if_due()
            return self._cache

    def save_total_chars(self, total: int) -> int:
        with self._lock:
            self._cache = max(0, int(total))
            self._dirty = True
            self._flush_if_due()
            return self._cache

    def flush(self) -> None:
        with self._lock:
            self._write_total(self._cache)
            self._dirty = False
            self._last_flush = time.monotonic()

    def _flush_if_due(self) -> None:
        if self._dirty and time.monotonic() - self._last_flush >= self._flush_interval:
            self._write_total(self._cache)
            self._dirty = False
            self._last_flush = time.monotonic()

    def _start_flusher(self) -> None:
        def loop() -> None:
            while True:
                time.sleep(self._flush_interval)
                with self._lock:
                    if self._dirty:
                        self._write_total(self._cache)
                        self._dirty = False
                        self._last_flush = time.monotonic()

        thread = threading.Thread(target=loop, daemon=True, name="stats-flusher")
        thread.start()

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
