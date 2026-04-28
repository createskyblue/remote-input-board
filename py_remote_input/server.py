from __future__ import annotations

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
from urllib.parse import urlparse

from py_remote_input.logger import Logger
from py_remote_input.typer import press_key, type_text
from py_remote_input.web import handle_request


def get_local_urls(port: int) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    try:
        hostname = socket.gethostname()
        for family, _, _, _, sockaddr in socket.getaddrinfo(hostname, port, family=socket.AF_INET):
            if family != socket.AF_INET:
                continue
            address = sockaddr[0]
            if address.startswith("127.") or address in seen:
                continue
            seen.add(address)
            urls.append(f"http://{address}:{port}")
    except OSError:
        pass
    return urls


def build_history_recorder(history_file_path: Path):
    history_file_path.parent.mkdir(parents=True, exist_ok=True)

    def record_history(item: dict) -> None:
        payload = {
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            **item,
        }
        with history_file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return record_history


def build_handler(logger: Logger, record_history):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _handle(self) -> None:
            parsed = urlparse(self.path)
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length) if content_length else b""
            response = handle_request(
                self.command,
                parsed.path,
                body,
                type_text=type_text,
                logger=logger,
                press_key=press_key,
                record_history=record_history,
            )
            self.send_response(response.status_code)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(response.body)))
            self.end_headers()
            self.wfile.write(response.body)

    return RequestHandler


def serve() -> None:
    port = int(os.environ.get("PORT", "3210"))
    log_dir = Path.cwd() / "logs"
    logger = Logger(log_dir / "server.log")
    record_history = build_history_recorder(log_dir / "input-history.log")
    server = ThreadingHTTPServer(("0.0.0.0", port), build_handler(logger, record_history))

    logger.info(f"Remote input server is running on port {port}.")
    logger.info("Open one of these addresses on your phone:")
    for url in get_local_urls(port):
        logger.info(url)
    logger.info("Keep the target desktop app focused before sending text from your phone.")
    logger.info(f"Input history is written to {log_dir / 'input-history.log'}.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
    finally:
        server.server_close()
