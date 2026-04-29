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
        self.assertIn("AUTO_SEND_STORAGE_KEY", html)
        self.assertIn("remoteInput.autoSendEnabled", html)
        self.assertIn("loadSavedAutoSend", html)
        self.assertIn("saveAutoSend", html)
        self.assertIn("autoSendSentence", html)
        self.assertIn("autoSendPrefix", html)
        self.assertIn("autoSendSuffix", html)
        self.assertIn("要在", html)
        self.assertIn("秒后自动发送吗？", html)
        self.assertIn("秒后自动发送！", html)
        self.assertIn("renderAutoSendCopy", html)
        self.assertIn("remoteInput.autoSendDelaySeconds", html)
        self.assertIn("loadSavedDelay", html)
        self.assertIn("saveDelayDraft", html)
        self.assertIn("commitDelay", html)
        self.assertIn("grid-template-columns: 1fr auto;", html)
        self.assertIn(".toolbar { grid-template-columns: 1fr; }", html)
        self.assertIn(".actions { grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr; }", html)
        self.assertIn(".modePanel { display: grid; gap: 8px; }", html)
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
        self.assertIn('aria-label="发送或回车"', html)
        self.assertIn('class="enterIcon"', html)
        self.assertIn('id="keyUp"', html)
        self.assertIn('id="keyDown"', html)
        self.assertIn('syncKey("up")', html)
        self.assertIn('syncKey("down")', html)
        self.assertIn("modeToggle", html)
        self.assertIn("touchpadPanel", html)
        self.assertIn("trackpad", html)
        self.assertIn("mouseLeft", html)
        self.assertIn("mouseRight", html)
        self.assertIn("滑动控制鼠标", html)
        self.assertIn("单指单击：左键", html)
        self.assertIn("双指单击：右键", html)
        self.assertIn("syncMouseMove", html)
        self.assertIn("activeTrackpadPointers", html)
        self.assertIn("finishTrackpadTap", html)
        self.assertIn('syncMouseClick("left")', html)
        self.assertIn('syncMouseClick("right")', html)
        self.assertIn('postJson("/api/mouse/move"', html)
        self.assertIn('postJson("/api/mouse/click"', html)
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

    def test_submits_arrow_key_to_key_presser(self):
        calls = []

        def press_key(key):
            calls.append(key)
            return {"method": "sendinput-key", "durationMs": 5, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/key",
            json.dumps({"key": "up"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=press_key,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["up"])

    def test_submits_mouse_move_to_mouse_mover(self):
        calls = []

        def move_mouse(dx, dy):
            calls.append((dx, dy))
            return {"method": "sendinput-mouse-move", "durationMs": 3}

        response = handle_request(
            "POST",
            "/api/mouse/move",
            json.dumps({"dx": 12.4, "dy": -7.6}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            move_mouse=move_mouse,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, [(12, -8)])

    def test_submits_mouse_click_to_mouse_clicker(self):
        calls = []

        def click_mouse(button):
            calls.append(button)
            return {"method": "sendinput-mouse-click", "durationMs": 3}

        response = handle_request(
            "POST",
            "/api/mouse/click",
            json.dumps({"button": "right"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            click_mouse=click_mouse,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["right"])

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



