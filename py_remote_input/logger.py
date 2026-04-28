from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


class Logger:
    def __init__(self, log_file_path: Path):
        self.log_file_path = log_file_path
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    def info(self, message: str, meta: dict | None = None) -> None:
        self._write("INFO", message, meta)

    def warn(self, message: str, meta: dict | None = None) -> None:
        self._write("WARN", message, meta)

    def error(self, message: str, meta: dict | None = None) -> None:
        self._write("ERROR", message, meta)

    def _write(self, level: str, message: str, meta: dict | None = None) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        suffix = f" {json.dumps(meta, ensure_ascii=False)}" if meta else ""
        line = f"[{timestamp}] {level} {message}{suffix}"
        print(line, flush=True)
        with self.log_file_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{line}\n")
