from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

DEFAULT_SETTINGS = {
    "inputMethod": "type",
}


class SettingsStore:
    """Server-persisted settings, stored as a flat dict in a JSON file.

    Only keys in DEFAULT_SETTINGS are kept; unknown keys and invalid values
    are dropped so the file can never grow out of control.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._lock = Lock()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load()

    def get_all(self) -> dict:
        with self._lock:
            return dict(self._cache)

    def save_all(self, incoming: dict) -> dict:
        with self._lock:
            self._cache = self._clean({**self._cache, **incoming})
            self.file_path.write_text(
                json.dumps(self._cache, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return dict(self._cache)

    def _load(self) -> dict:
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        return self._clean(payload)

    def _clean(self, incoming: dict) -> dict:
        cleaned = dict(DEFAULT_SETTINGS)
        for key, value in incoming.items():
            if key not in DEFAULT_SETTINGS:
                continue
            if key == "inputMethod" and value not in {"type", "paste"}:
                continue
            cleaned[key] = value
        return cleaned
