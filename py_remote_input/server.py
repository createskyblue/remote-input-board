from __future__ import annotations

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
from urllib.parse import urlparse

from py_remote_input.logger import Logger
from py_remote_input.settings_store import SettingsStore
from py_remote_input.snippets_store import SnippetsStore
from py_remote_input.stats import TextStatsStore, count_text_history_chars
from py_remote_input.typer import click_mouse, mouse_button, move_mouse, paste_text, press_key, scroll_mouse, type_text
from py_remote_input.web import handle_realtime_message, handle_request
from py_remote_input.websocket import build_websocket_accept, encode_websocket_frame, read_websocket_frame


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


def build_history_recorder(log_dir: Path, stats_file_path: Path | None = None):
    history_dir = log_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    if stats_file_path is None:
        stats_file_path = log_dir / "stats.json"
    text_stats = TextStatsStore(stats_file_path, initial_total_chars=count_text_history_chars(history_dir))

    def record_history(item: dict) -> None:
        now = datetime.now()
        day_dir = history_dir / now.strftime("%Y-%m-%d")
        day_dir.mkdir(parents=True, exist_ok=True)
        path = day_dir / (now.strftime("%H") + ".log")
        payload = {
            "createdAt": now.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            **item,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return record_history, text_stats


def _write_websocket_frame(writer, opcode: int, payload: bytes = b"") -> None:
    writer.write(encode_websocket_frame(opcode, payload))
    if hasattr(writer, "flush"):
        writer.flush()


def serve_websocket_messages(
    reader,
    writer,
    logger: Logger,
    press_key=None,
    move_mouse=None,
    scroll_mouse=None,
    click_mouse=None,
    mouse_button=None,
    type_text=None,
    paste_text=None,
    record_history=None,
    text_stats=None,
    settings_store=None,
    snippets_store=None,
) -> None:
    while True:
        try:
            frame = read_websocket_frame(reader)
            if frame is None:
                return
            if frame.opcode == 0x8:
                _write_websocket_frame(writer, 0x8)
                return
            if frame.opcode == 0x9:
                _write_websocket_frame(writer, 0xA, frame.payload)
                continue
            if frame.opcode != 0x1:
                continue

            try:
                payload = json.loads(frame.payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                _write_websocket_frame(
                    writer,
                    0x1,
                    json.dumps({"ok": False, "error": "Invalid realtime JSON."}).encode("utf-8"),
                )
                continue

            result = handle_realtime_message(
                payload,
                logger,
                press_key=press_key,
                move_mouse=move_mouse,
                scroll_mouse=scroll_mouse,
                click_mouse=click_mouse,
                mouse_button=mouse_button,
                type_text=type_text,
                paste_text=paste_text,
                record_history=record_history,
                text_stats=text_stats,
                settings_store=settings_store,
                snippets_store=snippets_store,
            )
            request_id = payload.get("id")
            if isinstance(request_id, (str, int)):
                result["id"] = request_id
            if not result.get("ok") or result.get("type") in {"pong", "settings", "type", "paste", "stats", "snippets"}:
                _write_websocket_frame(writer, 0x1, json.dumps(result, ensure_ascii=False).encode("utf-8"))
        except OSError as exc:
            logger.warn("WebSocket connection closed.", {"error": str(exc)})
            return


def build_handler(logger: Logger, record_history, text_stats, snippets_store=None, settings_store=None):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/ws" and self.headers.get("Upgrade", "").lower() == "websocket":
                self._handle_websocket()
                return
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._send_cors_headers()
            self.end_headers()

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _send_cors_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _handle_websocket(self) -> None:
            websocket_key = self.headers.get("Sec-WebSocket-Key", "")
            if not websocket_key:
                self.send_error(400, "Missing Sec-WebSocket-Key")
                return

            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", build_websocket_accept(websocket_key))
            self.end_headers()
            self.close_connection = True
            logger.info("WebSocket connected.")
            serve_websocket_messages(
                self.rfile,
                self.wfile,
                logger,
                press_key=press_key,
                move_mouse=move_mouse,
                scroll_mouse=scroll_mouse,
                click_mouse=click_mouse,
                mouse_button=mouse_button,
                type_text=type_text,
                paste_text=paste_text,
                record_history=record_history,
                text_stats=text_stats,
                settings_store=settings_store,
                snippets_store=snippets_store,
            )
            logger.info("WebSocket disconnected.")

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
                text_stats=text_stats,
                snippets_store=snippets_store,
                move_mouse=move_mouse,
                scroll_mouse=scroll_mouse,
                click_mouse=click_mouse,
                mouse_button=mouse_button,
            )
            self.send_response(response.status_code)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(response.body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(response.body)

    return RequestHandler


def serve() -> None:
    port = int(os.environ.get("PORT", "3210"))
    log_dir = Path.cwd() / "logs"
    logger = Logger(log_dir / "server.log")
    record_history, text_stats = build_history_recorder(log_dir, log_dir / "stats.json")
    snippets_store = SnippetsStore(log_dir / "snippets.json")
    settings_store = SettingsStore(log_dir / "settings.json")
    server = ThreadingHTTPServer(
        ("0.0.0.0", port), build_handler(logger, record_history, text_stats, snippets_store, settings_store)
    )

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
        text_stats.flush()
        server.server_close()
