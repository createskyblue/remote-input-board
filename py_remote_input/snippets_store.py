from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

DEFAULT_SNIPPETS = [
    {"id": "1", "text": "/compact"},
    {"id": "2", "text": "/resume"},
    {"id": "3", "text": ""},
]


class SnippetsStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._lock = Lock()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write(DEFAULT_SNIPPETS)

    def get_all(self) -> list[dict]:
        with self._lock:
            return self._read()

    def save_all(self, snippets: list[dict]) -> list[dict]:
        cleaned = []
        for s in snippets:
            if not isinstance(s, dict):
                continue
            text = s.get("text", "")
            if not isinstance(text, str):
                text = ""
            sid = s.get("id", "")
            if not isinstance(sid, str) or not sid:
                continue
            cleaned.append({"id": sid, "text": text})
        with self._lock:
            self._write(cleaned)
            return self._read()

    def _read(self) -> list[dict]:
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(payload, list):
            return [{"id": s["id"], "text": s.get("text", "")} for s in payload if isinstance(s, dict) and "id" in s]
        return []

    def _write(self, snippets: list[dict]) -> None:
        self.file_path.write_text(
            json.dumps(snippets, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
