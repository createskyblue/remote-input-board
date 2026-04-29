from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import json
import math


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


def _read_json_body(body: bytes, logger) -> dict | None:
    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        logger.warn("Rejected invalid JSON body.")
        return None
    return payload


def _is_finite_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def handle_request(
    method: str,
    path: str,
    body: bytes,
    type_text,
    logger,
    press_key=None,
    record_history=None,
    move_mouse=None,
    click_mouse=None,
) -> Response:
    if method == "GET" and path == "/":
        logger.info("Served mobile page.")
        return Response(200, "text/html; charset=utf-8", HTML_PAGE.encode("utf-8"))

    if method == "POST" and path == "/api/type":
        payload = _read_json_body(body, logger)
        if payload is None:
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
        payload = _read_json_body(body, logger)
        if payload is None:
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

    if method == "POST" and path == "/api/mouse/move":
        payload = _read_json_body(body, logger)
        if payload is None:
            return json_response(400, {"error": "Invalid JSON body."})

        dx = payload.get("dx")
        dy = payload.get("dy")
        if not _is_finite_number(dx) or not _is_finite_number(dy):
            return json_response(400, {"error": "Mouse movement dx and dy are required."})
        if move_mouse is None:
            return json_response(500, {"error": "Mouse input is not configured."})

        rounded_dx = int(round(dx))
        rounded_dy = int(round(dy))
        if rounded_dx == 0 and rounded_dy == 0:
            return json_response(200, {"ok": True, "method": "sendinput-mouse-move", "dx": 0, "dy": 0})

        logger.info("Received mouse move request.", {"dx": rounded_dx, "dy": rounded_dy})
        try:
            result = move_mouse(rounded_dx, rounded_dy)
            logger.info("Mouse move request completed.", result)
            return json_response(200, {"ok": True, **result})
        except Exception as exc:  # noqa: BLE001
            logger.error("Mouse move request failed.", {"dx": rounded_dx, "dy": rounded_dy, "error": str(exc)})
            return json_response(500, {"error": str(exc)})

    if method == "POST" and path == "/api/mouse/click":
        payload = _read_json_body(body, logger)
        if payload is None:
            return json_response(400, {"error": "Invalid JSON body."})

        button = payload.get("button", "")
        if button not in {"left", "right"}:
            return json_response(400, {"error": f"Unsupported mouse button: {button}"})
        if click_mouse is None:
            return json_response(500, {"error": "Mouse input is not configured."})

        logger.info("Received mouse click request.", {"button": button})
        try:
            result = click_mouse(button)
            logger.info("Mouse click request completed.", result)
            return json_response(200, {"ok": True, **result})
        except Exception as exc:  # noqa: BLE001
            logger.error("Mouse click request failed.", {"button": button, "error": str(exc)})
            return json_response(500, {"error": str(exc)})

    return json_response(404, {"error": "Not found."})










