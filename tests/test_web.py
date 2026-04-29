import json
import unittest
from importlib import resources

import py_remote_input
from py_remote_input.web import handle_request


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, meta=None):
        self.messages.append(("info", message, meta))

    def warn(self, message, meta=None):
        self.messages.append(("warn", message, meta))

    def error(self, message, meta=None):
        self.messages.append(("error", message, meta))


class WebTests(unittest.TestCase):
    def test_serves_mobile_page_with_controls(self):
        response = handle_request("GET", "/", b"", lambda _text: {}, FakeLogger())
        html = response.body.decode("utf-8")
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(html, template)
        self.assertIn("textarea", html)
        self.assertNotIn("<header>", html)
        self.assertNotIn("手机语音输入后发送到电脑当前光标位置", html)
        self.assertIn("autoSend", html)
        self.assertIn("delaySeconds", html)
        self.assertIn("remoteInput.autoSendDelaySeconds", html)
        self.assertIn("TOTAL_CHARS_STORAGE_KEY", html)
        self.assertIn("remoteInput.totalChars", html)
        self.assertIn("totalChars", html)
        self.assertIn("累计字数", html)
        self.assertIn("updateTotalChars", html)
        self.assertIn("addTypedChars(payloadText)", html)
        self.assertIn("syncBackspace", html)
        self.assertIn("syncEnter", html)
        self.assertIn("sendOrEnter", html)
        self.assertIn("sendOnEnter", html)
        self.assertIn("/api/key", html)
        self.assertIn("HISTORY_STORAGE_KEY", html)
        self.assertIn("historyList", html)
        self.assertIn("clearHistory", html)
        self.assertIn("addHistoryItem", html)
        self.assertIn('addHistoryItem({ kind: "text", text: payloadText })', html)
        self.assertIn("focusComposer", html)
        self.assertIn('textarea id="text" autofocus', html)
        self.assertIn("applyHistoryItem", html)
        self.assertIn("confirmHistoryOverwrite", html)
        self.assertIn("要覆盖当前输入内容吗", html)
        self.assertNotIn('addHistoryItem({ kind: "key", key })', html)
        self.assertNotIn("已同步", html)

    def test_submits_text_to_typer(self):
        calls = []

        def type_text(text):
            calls.append(text)
            return {"method": "sendinput-unicode", "durationMs": 12, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/type",
            json.dumps({"text": "你好"}).encode("utf-8"),
            type_text,
            FakeLogger(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["你好"])

    def test_records_text_to_history_logger(self):
        records = []

        def type_text(text):
            return {"method": "sendinput-unicode", "durationMs": 12, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/type",
            json.dumps({"text": "重要内容"}).encode("utf-8"),
            type_text,
            FakeLogger(),
            record_history=lambda item: records.append(item),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(records[0]["kind"], "text")
        self.assertEqual(records[0]["text"], "重要内容")

    def test_does_not_record_key_to_history_logger(self):
        records = []

        def press_key(key):
            return {"method": "sendinput-key", "durationMs": 5, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/key",
            json.dumps({"key": "enter"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=press_key,
            record_history=lambda item: records.append(item),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(records, [])

    def test_submits_key_to_key_presser(self):
        calls = []

        def press_key(key):
            calls.append(key)
            return {"method": "sendinput-key", "durationMs": 5, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/key",
            json.dumps({"key": "backspace"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=press_key,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["backspace"])

    def test_rejects_empty_text(self):
        response = handle_request(
            "POST",
            "/api/type",
            json.dumps({"text": "   "}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Text is required", response.body.decode("utf-8"))

    def test_rejects_unsupported_key(self):
        response = handle_request(
            "POST",
            "/api/key",
            json.dumps({"key": "escape"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=lambda _key: {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported key", response.body.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()



