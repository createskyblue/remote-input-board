from __future__ import annotations

from dataclasses import dataclass
import json


HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>远程输入粘贴板</title>
  <style>
    :root {
      --bg: #eef3f0;
      --ink: #16211d;
      --muted: #65716d;
      --line: #d9e2de;
      --accent: #0f7b5f;
      --accent-2: #1d4f91;
      --danger: #b73535;
      --shadow: 0 18px 42px rgba(20, 38, 31, 0.14);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
      background:
        linear-gradient(135deg, rgba(15, 123, 95, 0.18), transparent 34%),
        linear-gradient(315deg, rgba(29, 79, 145, 0.16), transparent 32%),
        var(--bg);
      padding: 16px;
    }
    .shell {
      width: min(100%, 720px);
      margin: 0 auto;
      display: grid;
      grid-template-rows: auto auto auto;
      gap: 14px;
    }
    header, .composer, .statusbar {
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }
    header { padding: 16px; }
    h1 { margin: 0; font-size: 24px; line-height: 1.2; }
    .subtitle { margin: 8px 0 0; color: var(--muted); font-size: 14px; line-height: 1.6; }
    .composer { padding: 14px; display: grid; align-content: start; gap: 8px; }
    label { font-size: 14px; font-weight: 700; }
    textarea {
      width: 100%;
      min-height: 14vh;
      max-height: 24vh;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      color: var(--ink);
      background: #fbfdfc;
      font: inherit;
      font-size: 19px;
      line-height: 1.65;
      resize: vertical;
      outline: none;
    }
    textarea:focus, .delayControl input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 4px rgba(15, 123, 95, 0.12);
    }
    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 12px;
      align-items: center;
    }
    .switch, .delayControl {
      min-height: 48px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      white-space: nowrap;
    }
    .switch input { width: 22px; height: 22px; accent-color: var(--accent); }
    .delayControl input {
      width: 72px;
      height: 40px;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0 10px;
      color: var(--ink);
      background: #fbfdfc;
      font: inherit;
      font-weight: 700;
      outline: none;
    }
    .actions { display: flex; gap: 10px; }
    button {
      min-height: 48px;
      border: 0;
      border-radius: 12px;
      padding: 0 18px;
      color: #fff;
      background: var(--accent);
      font: inherit;
      font-weight: 800;
      cursor: pointer;
    }
    button.secondary { color: var(--accent); background: rgba(15, 123, 95, 0.1); }
    button:disabled { opacity: 0.62; cursor: wait; }
    .progressTrack { height: 8px; overflow: hidden; border-radius: 999px; background: #dce6e2; }
    .progressFill {
      width: 0%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      transition: width 80ms linear;
    }
    .historyPanel { padding: 14px; background: rgba(255, 255, 255, 0.92); border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow); }
    .historyHeader { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
    .historyHeader h2 { margin: 0; font-size: 16px; }
    .historyList { display: grid; gap: 8px; max-height: 32vh; overflow: auto; }
    .historyItem { border: 1px solid var(--line); border-radius: 12px; padding: 10px; background: #fbfdfc; white-space: pre-wrap; word-break: break-word; font-size: 14px; line-height: 1.45; }
    .historyMeta { color: var(--muted); font-size: 12px; margin-bottom: 4px; }
    .statusbar { padding: 12px 14px; color: var(--muted); font-size: 14px; min-height: 48px; }
    .statusbar.error { color: var(--danger); }
    @media (max-width: 520px) {
      body { padding: 10px; }
      .toolbar { grid-template-columns: 1fr; }
      .actions { display: grid; grid-template-columns: 1fr 1fr; }
      textarea { min-height: 12vh; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <h1>远程输入粘贴板</h1>
      <p class="subtitle">手机语音输入后发送到电脑当前光标位置。自动发送开启时，停止输入到设定秒数后会发送并清空。</p>
    </header>

    <section class="composer">
      <label for="text">输入内容</label>
      <textarea id="text" placeholder="在这里用豆包输入法语音输入"></textarea>
      <div class="progressTrack" aria-hidden="true"><div id="progressFill" class="progressFill"></div></div>
      <div class="toolbar">
        <label class="switch"><input id="autoSend" type="checkbox" checked><span>自动发送</span></label>
        <label class="delayControl" for="delaySeconds">
          <span>延迟</span>
          <input id="delaySeconds" type="number" inputmode="decimal" min="0.1" max="30" step="0.1" value="2">
          <span>秒</span>
        </label>
        <div class="actions">
          <button id="send" type="button">发送</button>
          <button id="clear" class="secondary" type="button">清空</button>
        </div>
      </div>
    </section>

    <section class="historyPanel">
      <div class="historyHeader">
        <h2>最近 30 条发送历史</h2>
        <button id="clearHistory" class="secondary" type="button">清空历史</button>
      </div>
      <div id="historyList" class="historyList"></div>
    </section>

    <div id="status" class="statusbar">等待输入。</div>
  </main>

  <script>
    const DELAY_STORAGE_KEY = "remoteInput.autoSendDelaySeconds";
    const HISTORY_STORAGE_KEY = "remoteInput.history";
    const HISTORY_LIMIT = 30;
    const text = document.getElementById("text");
    const autoSend = document.getElementById("autoSend");
    const delaySeconds = document.getElementById("delaySeconds");
    const sendButton = document.getElementById("send");
    const clearButton = document.getElementById("clear");
    const statusNode = document.getElementById("status");
    const progressFill = document.getElementById("progressFill");
    const historyList = document.getElementById("historyList");
    const clearHistory = document.getElementById("clearHistory");

    let pendingTimer = null;
    let progressTimer = null;
    let countdownStartedAt = 0;
    let sending = false;
    let syncingKey = false;


    function loadHistory() {
      try {
        const raw = window.localStorage.getItem(HISTORY_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
      } catch {
        return [];
      }
    }

    function saveHistory(items) {
      window.localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(items.slice(0, HISTORY_LIMIT)));
    }

    function renderHistory() {
      const items = loadHistory();
      historyList.innerHTML = "";
      if (items.length === 0) {
        const empty = document.createElement("div");
        empty.className = "historyItem";
        empty.textContent = "暂无发送历史。";
        historyList.appendChild(empty);
        return;
      }
      for (const item of items) {
        const node = document.createElement("div");
        node.className = "historyItem";
        const meta = document.createElement("div");
        meta.className = "historyMeta";
        meta.textContent = new Date(item.createdAt).toLocaleString();
        const body = document.createElement("div");
        body.textContent = item.kind === "key" ? "[按键] " + item.key : item.text;
        node.appendChild(meta);
        node.appendChild(body);
        historyList.appendChild(node);
      }
    }

    function addHistoryItem(item) {
      const items = loadHistory();
      items.unshift({ ...item, createdAt: new Date().toISOString() });
      saveHistory(items);
      renderHistory();
    }
    function setStatus(message, isError = false) {
      statusNode.textContent = message;
      statusNode.classList.toggle("error", isError);
    }

    function stopCountdown() {
      clearTimeout(pendingTimer);
      clearInterval(progressTimer);
      pendingTimer = null;
      progressTimer = null;
      progressFill.style.width = "0%";
    }

    function normalizeDelaySeconds(value) {
      const seconds = Number.parseFloat(value);
      if (!Number.isFinite(seconds) || seconds <= 0) return 2;
      return Math.min(30, Math.max(0.1, seconds));
    }

    function loadSavedDelay() {
      const savedValue = window.localStorage.getItem(DELAY_STORAGE_KEY);
      if (savedValue !== null) delaySeconds.value = normalizeDelaySeconds(savedValue).toString();
    }

    function saveDelayDraft() {
      window.localStorage.setItem(DELAY_STORAGE_KEY, delaySeconds.value);
    }

    function commitDelay() {
      const seconds = normalizeDelaySeconds(delaySeconds.value);
      delaySeconds.value = seconds.toString();
      window.localStorage.setItem(DELAY_STORAGE_KEY, seconds.toString());
    }

    function getAutoSendDelay() {
      return normalizeDelaySeconds(delaySeconds.value) * 1000;
    }

    function startCountdown() {
      stopCountdown();
      if (!autoSend.checked || sending || !text.value.trim()) return;

      const autoSendDelay = getAutoSendDelay();
      countdownStartedAt = Date.now();
      setStatus("停止输入后 " + (autoSendDelay / 1000).toString() + " 秒自动发送。");
      progressTimer = setInterval(() => {
        const elapsed = Date.now() - countdownStartedAt;
        progressFill.style.width = Math.min(100, (elapsed / autoSendDelay) * 100) + "%";
      }, 50);
      pendingTimer = setTimeout(() => sendText({ source: "auto" }), autoSendDelay);
    }

    async function postJson(url, payload) {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "请求失败");
      return result;
    }

    async function sendText(options = {}) {
      const payloadText = text.value;
      if (!payloadText.trim() || sending) return;

      stopCountdown();
      sending = true;
      sendButton.disabled = true;
      setStatus(options.source === "auto" ? "自动发送中..." : "发送中...");

      try {
        const result = await postJson("/api/type", { text: payloadText });
        addHistoryItem({ kind: "text", text: payloadText });
        text.value = "";
        setStatus("已发送，耗时 " + (result.durationMs || 0) + " ms。");
      } catch (error) {
        setStatus(error.message || "发送失败", true);
      } finally {
        sending = false;
        sendButton.disabled = false;
        progressFill.style.width = "0%";
      }
    }

    async function syncKey(key) {
      if (syncingKey) return;
      stopCountdown();
      syncingKey = true;
      setStatus(key === "backspace" ? "同步退格中..." : "同步回车中...");
      try {
        await postJson("/api/key", { key });

        setStatus("已同步 " + key + "。");
      } catch (error) {
        setStatus(error.message || "按键同步失败", true);
      } finally {
        syncingKey = false;
      }
    }

    function syncBackspace() {
      syncKey("backspace");
    }

    function syncEnter(event) {
      event.preventDefault();
      syncKey("enter");
    }

    function sendOrEnter() {
      if (text.value.trim()) {
        sendText({ source: "manual" });
      } else {
        syncKey("enter");
      }
    }

    function sendOnEnter(event) {
      if (!text.value.trim() || sending) return;
      event.preventDefault();
      sendText({ source: "enter" });
    }

    text.addEventListener("beforeinput", (event) => {
      if (event.inputType === "deleteContentBackward" && text.value === "") syncBackspace();
      if (event.inputType === "insertLineBreak") {
        text.value.trim() ? sendOnEnter(event) : syncEnter(event);
      }
    });
    text.addEventListener("keydown", (event) => {
      if (event.key === "Backspace" && text.value === "") syncBackspace();
      if (event.key === "Enter") {
        text.value.trim() ? sendOnEnter(event) : syncEnter(event);
      }
    });
    text.addEventListener("input", startCountdown);
    delaySeconds.addEventListener("input", () => {
      saveDelayDraft();
      startCountdown();
    });
    delaySeconds.addEventListener("blur", () => {
      commitDelay();
      startCountdown();
    });
    autoSend.addEventListener("change", () => {
      if (autoSend.checked) startCountdown();
      else {
        stopCountdown();
        setStatus("自动发送已关闭。");
      }
    });
    sendButton.addEventListener("click", sendOrEnter);
    clearHistory.addEventListener("click", () => {
      saveHistory([]);
      renderHistory();
      setStatus("历史已清空。");
    });
    clearButton.addEventListener("click", () => {
      stopCountdown();
      text.value = "";
      setStatus("已清空。");
      text.focus();
    });

    loadSavedDelay();
    renderHistory();
  </script>
</body>
</html>
"""


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
        if key not in {"backspace", "delete", "enter"}:
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








