import io
import json
import unittest

from py_remote_input.server import serve_websocket_messages
from py_remote_input.websocket import (
    build_websocket_accept,
    encode_websocket_frame,
    read_websocket_frame,
)


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, meta=None):
        self.messages.append(("info", message, meta))

    def warn(self, message, meta=None):
        self.messages.append(("warn", message, meta))

    def error(self, message, meta=None):
        self.messages.append(("error", message, meta))


def build_masked_client_frame(opcode: int, payload: bytes = b"") -> bytes:
    mask = b"\x01\x02\x03\x04"
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return bytes([0x80 | opcode, 0x80 | len(payload)]) + mask + masked


class WebSocketProtocolTests(unittest.TestCase):
    def test_builds_rfc_accept_key(self):
        accept = build_websocket_accept("dGhlIHNhbXBsZSBub25jZQ==")

        self.assertEqual(accept, "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=")

    def test_reads_masked_text_frame(self):
        payload = b'{"type":"key","key":"up"}'
        mask = b"\x01\x02\x03\x04"
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        stream = io.BytesIO(bytes([0x81, 0x80 | len(payload)]) + mask + masked)

        frame = read_websocket_frame(stream)

        self.assertIsNotNone(frame)
        self.assertEqual(frame.opcode, 0x1)
        self.assertEqual(frame.payload, payload)

    def test_encodes_unmasked_server_text_frame(self):
        payload = b'{"ok":true}'

        frame = encode_websocket_frame(0x1, payload)

        self.assertEqual(frame, bytes([0x81, len(payload)]) + payload)

    def test_websocket_message_loop_dispatches_key_message(self):
        calls = []
        payload = json.dumps({"type": "key", "key": "up"}).encode("utf-8")
        reader = io.BytesIO(build_masked_client_frame(0x1, payload) + build_masked_client_frame(0x8))
        writer = io.BytesIO()

        serve_websocket_messages(
            reader,
            writer,
            FakeLogger(),
            press_key=lambda key: calls.append(key) or {"method": "sendinput-key"},
        )

        self.assertEqual(calls, ["up"])


if __name__ == "__main__":
    unittest.main()
