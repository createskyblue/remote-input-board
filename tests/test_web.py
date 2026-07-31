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


class FakeTextStats:
    def __init__(self, total=0):
        self.total = total

    def get_total_chars(self):
        return self.total

    def add_text(self, _text):
        return self.total

    def save_total_chars(self, total):
        self.total = total
        return self.total


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
        self.assertIn(".trackpad { aspect-ratio: 1;", html)
        self.assertIn(".textSurface { min-height: 260px; }", html)
        self.assertIn(".actions { grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr; }", html)
        self.assertIn(".modePanel { display: grid; gap: 0; }", html)
        self.assertIn("TOTAL_CHARS_STORAGE_KEY", html)
        self.assertIn("remoteInput.totalChars", html)
        self.assertIn("totalChars", html)
        self.assertIn("累计字数", html)
        self.assertIn("updateTotalChars", html)
        self.assertIn('fetchJson("/api/stats")', html)
        self.assertIn("Math.max(loadLocalTotalChars() + sentChars, serverTotal)", html)
        self.assertIn("saveStatsToServer", html)
        self.assertIn('type: "setStats"', html)
        self.assertIn("loadLocalTotalChars", html)
        self.assertNotIn("addTypedChars(payloadText)", html)
        self.assertIn("syncBackspace", html)
        self.assertIn("syncEnter", html)
        self.assertIn("sendOrEnter", html)
        self.assertIn("sendOnEnter", html)
        self.assertIn('aria-label="发送或回车"', html)
        self.assertIn('class="enterIcon"', html)
        self.assertNotIn('id="keyUp"', html)
        self.assertNotIn('id="keyDown"', html)
        self.assertIn('id="keyEscape"', html)
        self.assertIn('syncKey("up")', html)
        self.assertIn('syncKey("down")', html)
        self.assertIn('syncKey("escape")', html)
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
        self.assertIn("双指横放：上下滚动", html)
        self.assertIn("双指竖放：左右滚动", html)
        self.assertIn("双击按住：拖拽", html)
        self.assertIn("tapDebug", html)
        self.assertIn("双击间隔：-- ms", html)
        self.assertIn("updateTapDebug", html)
        self.assertIn("button.mouseButton { color: var(--accent-2);", html)
        self.assertIn("syncMouseMove", html)
        self.assertIn("syncMouseScroll", html)
        self.assertIn("syncMouseButton", html)
        self.assertIn("TRACKPAD_SCROLL_SCALE", html)
        self.assertIn("const TRACKPAD_SCROLL_SCALE = 6;", html)
        self.assertIn("TRACKPAD_SPEED", html)
        self.assertIn("const TRACKPAD_SPEED = 1.5;", html)
        self.assertIn("scaleTrackpadDelta", html)
        self.assertIn("scaleTrackpadDelta(corrected.dx, corrected.dy)", html)
        self.assertIn("queueMouseMove(a.dx, a.dy)", html)
        self.assertIn("getTwoFingerScrollAxis", html)
        self.assertIn("const ax = getTwoFingerScrollAxis();", html)
        self.assertIn('queueMouseScroll(ax === "horizontal" ? -corrected.dx * TRACKPAD_SCROLL_SCALE : 0, ax === "vertical" ? corrected.dy * TRACKPAD_SCROLL_SCALE : 0)', html)
        self.assertNotIn("getTrackpadCentroid", html)
        self.assertIn('sendRealtime({ type: "mouseScroll", dx, dy }', html)
        self.assertIn('postJson("/api/mouse/scroll", { dx, dy })', html)
        self.assertIn("lastAt", html)
        self.assertIn("dragLocked", html)
        self.assertIn("DOUBLE_TAP_MAX_MS", html)
        self.assertIn("const DOUBLE_TAP_MAX_MS = 380;", html)
        self.assertIn("lastClickDownAt", html)
        self.assertIn("tapStartedDrag", html)
        self.assertIn("startDragFromDoubleTap", html)
        self.assertIn("setDragLocked(true)", html)
        self.assertIn("const tapIntervalMs = lastClickDownAt > 0 ? startedAt - lastClickDownAt : null;", html)
        self.assertIn("tapIntervalMs < DOUBLE_TAP_MAX_MS", html)
        self.assertIn("pendingSingleTapTimer", html)
        self.assertIn("scheduleSingleTapClick", html)
        self.assertIn("cancelPendingSingleTapClick", html)
        self.assertIn("pendingSingleTapTimer = window.setTimeout", html)
        self.assertIn("window.clearTimeout(pendingSingleTapTimer)", html)
        self.assertIn("scheduleSingleTapClick(started)", html)
        self.assertIn("updateTapDebug(tapIntervalMs", html)
        self.assertIn("if (dragLocked) {", html)
        self.assertIn("setDragLocked(false);", html)
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
        self.assertNotIn('syncMouseClick("left");\n      lastClickDownAt = startedAt;', html)
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
        self.assertIn('sendButton.addEventListener("pointerdown", keepComposerFocus)', html)
        self.assertIn("function keepComposerFocus(event)", html)
        self.assertIn("event.preventDefault();", html)
        self.assertIn('setStatus("停止输入后 " + (d / 1000).toString() + " 秒自动发送。");', html)
        self.assertIn("sendButton.disabled = false; focusComposer();", html)
        self.assertIn("applyHistoryItem", html)
        self.assertIn("confirmHistoryOverwrite", html)
        self.assertIn("要覆盖当前输入内容吗", html)
        self.assertNotIn('addHistoryItem({ kind: "key", key })', html)
        self.assertNotIn("已同步", html)
        self.assertIn("settingsButton", html)
        self.assertIn('name="inputMethod"', html)
        self.assertIn('value="paste"', html)
        self.assertIn("SETTINGS_STORAGE_KEY", html)
        self.assertIn("sendRealtimeRequest", html)
        self.assertIn("saveSettings", html)
        self.assertIn('settings.inputMethod === "paste" ? "paste" : "type"', html)
        self.assertIn('postJson("/api/" + messageType, { text: payloadText })', html)
        self.assertIn("剪贴板粘贴", html)
        self.assertIn("键盘输入", html)
        self.assertIn("serverList", html)
        self.assertIn("getActiveServerHost", html)
        self.assertIn("loadSavedServers", html)
        self.assertIn("SERVERS_STORAGE_KEY", html)
        self.assertIn("selectServer", html)
        self.assertIn("getSnippets", html)
        self.assertIn("getStats", html)
        self.assertIn("SNIPPETS_STORAGE_KEY", html)
        self.assertIn("loadLocalSnippets", html)
        self.assertIn("saveLocalSnippets", html)

    def test_trackpad_two_finger_scroll_uses_same_slower_scale_for_both_axes(self):
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        self.assertIn("const TRACKPAD_SCROLL_SCALE = 6;", template)
        self.assertIn("const ax = getTwoFingerScrollAxis();", template)
        self.assertIn('queueMouseScroll(ax === "horizontal" ? -corrected.dx * TRACKPAD_SCROLL_SCALE : 0, ax === "vertical" ? corrected.dy * TRACKPAD_SCROLL_SCALE : 0)', template)
        self.assertNotIn("TRACKPAD_HORIZONTAL_SCROLL_SCALE", template)
        self.assertNotIn("TRACKPAD_VERTICAL_SCROLL_SCALE", template)

    def test_trackpad_mouse_move_keeps_subpixel_remainder_between_frames(self):
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        self.assertIn("pendingMouseDx -= dx;", template)
        self.assertIn("pendingMouseDy -= dy;", template)
        self.assertNotIn("pendingMouseDx = 0;\n      pendingMouseDy = 0;\n      if (dx === 0 && dy === 0) return;", template)

    def test_empty_backspace_does_not_sync_from_both_beforeinput_and_keydown(self):
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        self.assertIn('const canUseBeforeInput = "onbeforeinput" in text;', template)
        self.assertIn('event.inputType === "deleteContentBackward"', template)
        self.assertIn('event.key === "Backspace" && !canUseBeforeInput', template)
        self.assertNotIn('event.key === "Backspace" && text.value === "") syncBackspace();', template)

    def test_empty_composer_uses_invisible_sentinel_for_repeated_mobile_backspace(self):
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        self.assertIn('const BACKSPACE_SENTINEL = "​";', template)
        self.assertIn("function getComposerText()", template)
        self.assertIn("function ensureBackspaceSentinel()", template)
        self.assertIn("function restoreBackspaceSentinelAfterDelete(event)", template)
        self.assertIn("composerTextBeforeInput === \"\"", template)
        self.assertIn("!text.value.includes(BACKSPACE_SENTINEL)", template)
        self.assertIn("syncBackspace();\n      ensureBackspaceSentinel();", template)
        self.assertIn("const payloadText = getComposerText();", template)
        self.assertIn("text.value = BACKSPACE_SENTINEL;", template)

    def test_text_mode_actions_prioritize_escape_snippets_and_send(self):
        template = resources.files(py_remote_input).joinpath("templates", "index.html").read_text(encoding="utf-8")

        text_panel = template.split('<div id="touchpadPanel"', 1)[0]
        self.assertIn('class="actions textActions"', text_panel)
        self.assertIn('id="keyEscape"', text_panel)
        self.assertIn('class="sendButton primaryAction"', text_panel)
        self.assertIn('grid-template-areas: "escape send" "snippets send";', template)
        self.assertIn(".primaryAction { grid-area: send;", template)
        self.assertIn(".escapeAction { grid-area: escape;", template)
        self.assertIn(".snippetsAction { grid-area: snippets;", template)
        self.assertIn('keyEscapeButton.addEventListener("click", () => syncKey("escape"))', template)
        self.assertNotIn('id="keyUp"', text_panel)
        self.assertNotIn('id="keyDown"', text_panel)
        self.assertIn('id="mouseKeyUp"', template)
        self.assertIn('id="mouseKeyDown"', template)

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

    def test_submits_escape_key_to_key_presser(self):
        calls = []

        def press_key(key):
            calls.append(key)
            return {"method": "sendinput-key", "durationMs": 5, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/key",
            json.dumps({"key": "escape"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=press_key,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["escape"])

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

    def test_submits_mouse_scroll_to_mouse_scroller(self):
        calls = []

        def scroll_mouse(dx, dy):
            calls.append((dx, dy))
            return {"method": "sendinput-mouse-scroll", "durationMs": 3}

        response = handle_request(
            "POST",
            "/api/mouse/scroll",
            json.dumps({"dx": 119.6, "dy": -240.4}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            scroll_mouse=scroll_mouse,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, [(120, -240)])

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

    def test_realtime_mouse_scroll_calls_mouse_scroller(self):
        calls = []

        result = handle_realtime_message(
            {"type": "mouseScroll", "dx": 24.4, "dy": -49.6},
            FakeLogger(),
            scroll_mouse=lambda dx, dy: calls.append((dx, dy)) or {"method": "sendinput-mouse-scroll"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, [(24, -50)])

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
            {"type": "key", "key": "escape"},
            FakeLogger(),
            press_key=lambda key: calls.append(key) or {"method": "sendinput-key"},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(calls, ["escape"])

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
            json.dumps({"key": "pageup"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            press_key=lambda _key: {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported key", response.body.decode("utf-8"))

    def test_submits_text_to_paste(self):
        calls = []

        def paste_text(text):
            calls.append(text)
            return {"method": "clipboard-paste", "durationMs": 8, "windowTitle": "Notepad"}

        response = handle_request(
            "POST",
            "/api/paste",
            json.dumps({"text": "粘贴内容"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            paste_text=paste_text,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(calls, ["粘贴内容"])
        self.assertIn("clipboard-paste", response.body.decode("utf-8"))

    def test_rejects_empty_paste_text(self):
        response = handle_request(
            "POST",
            "/api/paste",
            json.dumps({"text": "   "}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
            paste_text=lambda _text: {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Text is required", response.body.decode("utf-8"))

    def test_paste_unconfigured_returns_500(self):
        response = handle_request(
            "POST",
            "/api/paste",
            json.dumps({"text": "hello"}).encode("utf-8"),
            lambda _text: {},
            FakeLogger(),
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Paste input is not configured", response.body.decode("utf-8"))

    def test_realtime_type_message_calls_typer_and_records_history(self):
        calls = []
        records = []

        result = handle_realtime_message(
            {"type": "type", "text": "你好"},
            FakeLogger(),
            type_text=lambda text: calls.append(text) or {"method": "sendinput-unicode", "durationMs": 12},
            record_history=lambda item: records.append(item),
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["type"], "type")
        self.assertEqual(result["sentChars"], 2)
        self.assertEqual(calls, ["你好"])
        self.assertEqual(records[0]["text"], "你好")

    def test_realtime_paste_message_calls_paster(self):
        calls = []

        result = handle_realtime_message(
            {"type": "paste", "text": "代码"},
            FakeLogger(),
            paste_text=lambda text: calls.append(text) or {"method": "clipboard-paste", "durationMs": 8},
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["type"], "paste")
        self.assertEqual(result["sentChars"], 2)
        self.assertEqual(calls, ["代码"])

    def test_realtime_get_settings_returns_stored_settings(self):
        import tempfile
        from pathlib import Path

        from py_remote_input.settings_store import SettingsStore

        with tempfile.TemporaryDirectory() as tmp:
            store = SettingsStore(Path(tmp) / "settings.json")
            result = handle_realtime_message({"type": "getSettings"}, FakeLogger(), settings_store=store)

            self.assertEqual(result["ok"], True)
            self.assertEqual(result["type"], "settings")
            self.assertEqual(result["settings"], {"inputMethod": "type"})

    def test_realtime_set_settings_saves_and_returns(self):
        import tempfile
        from pathlib import Path

        from py_remote_input.settings_store import SettingsStore

        with tempfile.TemporaryDirectory() as tmp:
            store = SettingsStore(Path(tmp) / "settings.json")
            result = handle_realtime_message(
                {"type": "setSettings", "settings": {"inputMethod": "paste"}},
                FakeLogger(),
                settings_store=store,
            )

            self.assertEqual(result["ok"], True)
            self.assertEqual(result["settings"], {"inputMethod": "paste"})
            self.assertEqual(store.get_all(), {"inputMethod": "paste"})

    def test_realtime_set_settings_rejects_invalid_input_method(self):
        import tempfile
        from pathlib import Path

        from py_remote_input.settings_store import SettingsStore

        with tempfile.TemporaryDirectory() as tmp:
            store = SettingsStore(Path(tmp) / "settings.json")
            result = handle_realtime_message(
                {"type": "setSettings", "settings": {"inputMethod": "weird"}},
                FakeLogger(),
                settings_store=store,
            )

            self.assertEqual(result["ok"], False)
            self.assertIn("Invalid inputMethod", result["error"])
            self.assertEqual(store.get_all(), {"inputMethod": "type"})

    def test_realtime_get_stats_returns_total_chars(self):
        result = handle_realtime_message(
            {"type": "getStats"},
            FakeLogger(),
            text_stats=FakeTextStats(12345),
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["type"], "stats")
        self.assertEqual(result["totalChars"], 12345)

    def test_realtime_set_stats_saves_total(self):
        stats = FakeTextStats(100)

        result = handle_realtime_message(
            {"type": "setStats", "totalChars": 123456},
            FakeLogger(),
            text_stats=stats,
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["type"], "stats")
        self.assertEqual(result["totalChars"], 123456)
        self.assertEqual(stats.get_total_chars(), 123456)

    def test_realtime_set_stats_rejects_non_numeric(self):
        result = handle_realtime_message(
            {"type": "setStats", "totalChars": "abc"},
            FakeLogger(),
            text_stats=FakeTextStats(),
        )

        self.assertEqual(result["ok"], False)
        self.assertIn("numeric totalChars", result["error"])

    def test_realtime_get_snippets_returns_snippets(self):
        class FakeSnippets:
            def get_all(self):
                return [{"id": "1", "text": "hi"}]

            def save_all(self, incoming):
                return incoming

        result = handle_realtime_message({"type": "getSnippets"}, FakeLogger(), snippets_store=FakeSnippets())

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["type"], "snippets")
        self.assertEqual(result["snippets"], [{"id": "1", "text": "hi"}])

    def test_realtime_set_snippets_saves(self):
        saved = []

        class FakeSnippets:
            def get_all(self):
                return []

            def save_all(self, incoming):
                saved.append(incoming)
                return incoming

        result = handle_realtime_message(
            {"type": "setSnippets", "snippets": [{"id": "x", "text": "abc"}]},
            FakeLogger(),
            snippets_store=FakeSnippets(),
        )

        self.assertEqual(result["ok"], True)
        self.assertEqual(saved, [[{"id": "x", "text": "abc"}]])

    def test_realtime_set_snippets_rejects_non_array(self):
        class FakeSnippets:
            def get_all(self):
                return []

            def save_all(self, incoming):
                return incoming

        result = handle_realtime_message(
            {"type": "setSnippets", "snippets": "nope"},
            FakeLogger(),
            snippets_store=FakeSnippets(),
        )

        self.assertEqual(result["ok"], False)
        self.assertIn("Expected a snippets array", result["error"])


if __name__ == "__main__":
    unittest.main()



