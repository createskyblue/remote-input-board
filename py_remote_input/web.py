from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import json


def load_html_page() -> str:
    return resources.files(__package__).joinpath("templates", "index.html").read_text(encoding="utf-8")


HTML_PAGE = load_html_page()


@dataclass
class Response:
    status_code: int
    content_type: str
    body: bytes


def json_response(status_code: int, payload: dict) -> Response:
    return Response(
        status_code=status_code,
        content_type="application/json; charset=utf-8",
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )


def handle_request(method: str, path: str, body: bytes, type_text, logger, press_key=None, record_history=None) -> Response:
    if method == "GET" and path == "/":
        logger.info("Served mobile page.")
        return Response(200, "text/html; charset=utf-8", HTML_PAGE.encode("utf-8"))

    if method == "POST" and path == "/api/type":
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            logger.warn("Rejected invalid JSON body.")
            return json_response(400, {"error": "Invalid JSON body."})

        text = payload.get("text", "")
        if not isinstance(text, str) or not text.strip():
            logger.warn("Rejected empty text submission.")
            return json_response(400, {"error": "Text is required."})

        logger.info("Received typing request.", {"textLength": len(text)})
        try:
            result = type_text(text)
            if record_history is not None:
                record_history({"kind": "text", "text": text})
            logger.info("Typing request completed.", result)
            return json_response(200, {"ok": True, **result})
        except Exception as exc:  # noqa: BLE001
            logger.error("Typing request failed.", {"error": str(exc)})
            return json_response(500, {"error": str(exc)})

    if method == "POST" and path == "/api/key":
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            logger.warn("Rejected invalid JSON body.")
            return json_response(400, {"error": "Invalid JSON body."})

        key = payload.get("key", "")
        if key not in {"backspace", "delete", "down", "enter", "up"}:
            return json_response(400, {"error": f"Unsupported key: {key}"})
        if press_key is None:
            return json_response(500, {"error": "Key input is not configured."})

        logger.info("Received key request.", {"key": key})
        try:
            result = press_key(key)
            logger.info("Key request completed.", result)
            return json_response(200, {"ok": True, **result})
        except Exception as exc:  # noqa: BLE001
            logger.error("Key request failed.", {"key": key, "error": str(exc)})
            return json_response(500, {"error": str(exc)})

    return json_response(404, {"error": "Not found."})










