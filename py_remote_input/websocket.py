from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib


WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


@dataclass
class WebSocketFrame:
    opcode: int
    payload: bytes


def build_websocket_accept(key: str) -> str:
    digest = hashlib.sha1((key + WEBSOCKET_GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def _read_exact(reader, length: int) -> bytes | None:
    data = reader.read(length)
    if len(data) != length:
        return None
    return data


def read_websocket_frame(reader) -> WebSocketFrame | None:
    header = _read_exact(reader, 2)
    if header is None:
        return None

    opcode = header[0] & 0x0F
    masked = bool(header[1] & 0x80)
    length = header[1] & 0x7F
    if length == 126:
        extended = _read_exact(reader, 2)
        if extended is None:
            return None
        length = int.from_bytes(extended, "big")
    elif length == 127:
        extended = _read_exact(reader, 8)
        if extended is None:
            return None
        length = int.from_bytes(extended, "big")

    mask = b""
    if masked:
        mask = _read_exact(reader, 4)
        if mask is None:
            return None

    payload = _read_exact(reader, length)
    if payload is None:
        return None

    if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return WebSocketFrame(opcode=opcode, payload=payload)


def encode_websocket_frame(opcode: int, payload: bytes = b"") -> bytes:
    first_byte = 0x80 | (opcode & 0x0F)
    length = len(payload)
    if length < 126:
        header = bytes([first_byte, length])
    elif length <= 0xFFFF:
        header = bytes([first_byte, 126]) + length.to_bytes(2, "big")
    else:
        header = bytes([first_byte, 127]) + length.to_bytes(8, "big")
    return header + payload
