import json
import unittest
from importlib import resources

import py_remote_input
from py_remote_input.web import handle_realtime_message, handle_request


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
        self.assertIn("textSurface", html)
        self.assertIn(".textSurface { min-height: 220px;", html)
        self.assertIn(".trackpad { min-height: 220px;", html)
        self.assertIn(".textSurface, .trackpad { min-height: 260px; }", html)
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
        self.assertIn("mouseKeyUp", html)
        self.assertIn("mouseKeyDown", html)
        self.assertIn("滑动控制鼠标", html)
        self.assertIn("单指单击：左键", html)
        self.assertIn("双指单击：右键", html)
        self.assertIn("双击按住：拖拽", html)
        self.assertIn("tapDebug", html)
        self.assertIn("双击间隔：-- ms", html)
        self.assertIn("updateTapDebug", html)
        self.assertIn("button.mouseButton { color: var(--accent-2);", html)
        self.assertIn("syncMouseMove", html)
        self.assertIn("syncMouseButton", html)
        self.assertIn("TRACKPAD_ACCELERATION_SPEED_THRESHOLD", html)
        self.assertIn("TRACKPAD_ACCELERATION_MAX", html)
        self.assertIn("const TRACKPAD_ACCELERATION_SPEED_THRESHOLD = 0.45;", html)
        self.assertIn("const TRACKPAD_ACCELERATION_MAX = 1.8;", html)
        self.assertIn("const TRACKPAD_ACCELERATION_GAIN = 1.4;", html)
        self.assertIn("applyTrackpadAcceleration", html)
        self.assertIn("const adjusted = applyTrackpadAcceleration(dx, dy, elapsedMs);", html)
        self.assertIn("queueMouseMove(adjusted.dx, adjusted.dy)", html)
        self.assertIn("lastAt", html)
        self.assertIn("dragLocked", html)
        self.assertIn("DOUBLE_TAP_MAX_MS", html)
        self.assertIn("const DOUBLE_TAP_MAX_MS = 180;", html)
        self.assertIn("lastClickDownAt", html)
        self.assertIn("tapStartedDrag", html)
        self.assertIn("startDragFromDoubleTap", html)
        self.assertIn("setDragLocked(true)", html)
        self.assertIn("const tapIntervalMs = lastClickDownAt > 0 ? startedAt - lastClickDownAt : null;", html)
        self.assertIn("tapIntervalMs < DOUBLE_TAP_MAX_MS", html)
        self.assertIn("lastClickDownAt = startedAt;", html)
        self.assertIn("updateTapDebug(tapIntervalMs", html)
        self.assertIn("if (dragLocked) {", html)
        self.assertIn("setDragLocked(false);", html)
        self.assertNotIn("pendingSingleTapTimer", html)
        self.assertNotIn("scheduleSingleTapClick", html)
        self.assertNotIn("cancelPendingSingleTapClick", html)
        self.assertNotIn("doubleTapSuppressedUntil", html)
        self.assertNotIn("lastTapEndedAt", html)
        self.assertNotIn("tapHandledByDragStart", html)
        self.assertNotIn("dragArmed", html)
        self.assertNotIn("startDragFromThirdTap", html)
        self.assertNotIn("lockDragFromDoubleTap", html)
        self.assertIn("new WebSocket", html)
        self.assertIn('"/ws"', html)
        self.assertIn("connectRealtime", html)
        self.assertIn("sendRealtime", html)
        self.assertIn("activeTrackpadPointers", html)
        self.assertIn("finishTrackpadTap", html)
        self.assertIn('syncMouseClick("left")', html)
        self.assertIn('syncMouseClick("right")', html)
        self.assertNotIn("window.clearTimeout(pendingSingleTapTimer)", html)
        self.assertIn('syncMouseButton("left", locked ? "down" : "up")', html)
        self.assertIn('mouseKeyUpButton.addEventListener("click", () => syncKey("up"))', html)
        self.assertIn('mouseKeyDownButton.addEventListener("click", () => syncKey("down"))', html)
        self.assertIn('postJson("/api/mouse/move"', html)
        self.assertIn('postJson("/api/mouse/click"', html)
        self.assertIn('postJson("/api/mouse/button"', html)
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

    def test_submits_mouse_button_action_to_mouse_button_handler(self):
        calls = []

        response = handle_request(
            "POST",
            "/api/mouse/button",
            json.dumps({"button": "left", "action": "down"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            mouse_button=lambda button, action: calls.append((button, action)) or {"method": "sendinput-mouse-button"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, [("left", "down")])

    def test_realtime_mouse_move_calls_mouse_mover(self):
        calls = []

        result = handle_realtime_message(
            {"type": "mouseMove", "dx": 2.4, "dy": -3.6},
            FakeLogger(),
            move_mouse=lambda dx, dy: calls.append((dx, dy)) or {"method": "sendinput-mouse-move"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, [(2, -4)])

    def test_realtime_mouse_click_calls_mouse_clicker(self):
        calls = []

        result = handle_realtime_message(
            {"type": "mouseClick", "button": "left"},
            FakeLogger(),
            click_mouse=lambda button: calls.append(button) or {"method": "sendinput-mouse-click"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, ["left"])

    def test_realtime_mouse_button_calls_mouse_button_handler(self):
        calls = []

        result = handle_realtime_message(
            {"type": "mouseButton", "button": "left", "action": "up"},
            FakeLogger(),
            mouse_button=lambda button, action: calls.append((button, action)) or {"method": "sendinput-mouse-button"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, [("left", "up")])

    def test_realtime_key_calls_key_presser(self):
        calls = []

        result = handle_realtime_message(
            {"type": "key", "key": "down"},
            FakeLogger(),
            press_key=lambda key: calls.append(key) or {"method": "sendinput-key"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, ["down"])

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



