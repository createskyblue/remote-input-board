from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
import time

from winrt.windows.applicationmodel.datatransfer import Clipboard, ClipboardHistoryItemsResultStatus


ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]


INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000
VK_BACK = 0x08
VK_ESCAPE = 0x1B
VK_RETURN = 0x0D
VK_UP = 0x26
VK_DOWN = 0x28
VK_DELETE = 0x2E
VK_CONTROL = 0x11
VK_V = 0x56

TYPE_BATCH_CHARS = 5
TYPE_BATCH_DELAY = 0.008
PASTE_SETTLE_DELAY = 0.05
PASTE_HISTORY_TIMEOUT = 1.0
PASTE_HISTORY_POLL_INTERVAL = 0.05
PASTE_RESTORE_DELAY = 0.5

CF_UNICODETEXT = 13
CF_BITMAP = 2
CF_METAFILEPICT = 3
CF_ENHMETAFILE = 14
CF_OWNERDISPLAY = 0x0080
GMEM_MOVEABLE = 0x0002
IMAGE_BITMAP = 0


class METAFILEPICT(ctypes.Structure):
    _fields_ = [
        ("mm", wintypes.LONG),
        ("xExt", wintypes.LONG),
        ("yExt", wintypes.LONG),
        ("hMF", wintypes.HANDLE),
    ]

SUPPORTED_KEYS = {
    "backspace": VK_BACK,
    "delete": VK_DELETE,
    "down": VK_DOWN,
    "enter": VK_RETURN,
    "escape": VK_ESCAPE,
    "up": VK_UP,
}

SUPPORTED_MOUSE_BUTTONS = {
    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
}

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT
user32.GetForegroundWindow.argtypes = ()
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
user32.GetWindowTextW.restype = ctypes.c_int
user32.OpenClipboard.argtypes = (wintypes.HWND,)
user32.OpenClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = ()
user32.EmptyClipboard.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = (wintypes.UINT,)
user32.GetClipboardData.restype = wintypes.HANDLE
user32.EnumClipboardFormats.argtypes = (wintypes.UINT,)
user32.EnumClipboardFormats.restype = wintypes.UINT
user32.CopyImage.argtypes = (wintypes.HANDLE, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT)
user32.CopyImage.restype = wintypes.HANDLE
user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
user32.SetClipboardData.restype = wintypes.HANDLE
user32.CloseClipboard.argtypes = ()
user32.CloseClipboard.restype = wintypes.BOOL

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalLock.restype = wintypes.LPVOID
kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalFree.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalFree.restype = wintypes.HGLOBAL
kernel32.GlobalSize.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalSize.restype = ctypes.c_size_t

gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
gdi32.DeleteObject.argtypes = (wintypes.HANDLE,)
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.CopyEnhMetaFileW.argtypes = (wintypes.HANDLE, wintypes.LPCWSTR)
gdi32.CopyEnhMetaFileW.restype = wintypes.HANDLE
gdi32.DeleteEnhMetaFile.argtypes = (wintypes.HANDLE,)
gdi32.DeleteEnhMetaFile.restype = wintypes.BOOL
gdi32.CopyMetaFileW.argtypes = (wintypes.HANDLE, wintypes.LPCWSTR)
gdi32.CopyMetaFileW.restype = wintypes.HANDLE
gdi32.DeleteMetaFile.argtypes = (wintypes.HANDLE,)
gdi32.DeleteMetaFile.restype = wintypes.BOOL


def _iter_utf16_units(text: str) -> list[int]:
    payload = text.encode("utf-16-le")
    return [int.from_bytes(payload[index:index + 2], "little") for index in range(0, len(payload), 2)]


def _make_unicode_input(scan_code: int, key_up: bool) -> INPUT:
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=0,
            wScan=scan_code,
            dwFlags=KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0),
            time=0,
            dwExtraInfo=0,
        ),
    )


def _make_key_input(virtual_key: int, key_up: bool) -> INPUT:
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=virtual_key,
            wScan=0,
            dwFlags=KEYEVENTF_KEYUP if key_up else 0,
            time=0,
            dwExtraInfo=0,
        ),
    )


def _make_mouse_input(dx: int = 0, dy: int = 0, mouse_data: int = 0, flags: int = 0) -> INPUT:
    return INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=dx,
            dy=dy,
            mouseData=mouse_data,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )


def build_key_inputs(key: str) -> list[INPUT]:
    virtual_key = SUPPORTED_KEYS.get(key)
    if virtual_key is None:
        raise ValueError(f"Unsupported key: {key}")
    return [_make_key_input(virtual_key, False), _make_key_input(virtual_key, True)]


def build_mouse_move_inputs(dx: int, dy: int) -> list[INPUT]:
    if dx == 0 and dy == 0:
        return []
    return [_make_mouse_input(dx=dx, dy=dy, flags=MOUSEEVENTF_MOVE)]


def build_mouse_scroll_inputs(dx: int, dy: int) -> list[INPUT]:
    inputs: list[INPUT] = []
    if dx != 0:
        inputs.append(_make_mouse_input(mouse_data=dx, flags=MOUSEEVENTF_HWHEEL))
    if dy != 0:
        inputs.append(_make_mouse_input(mouse_data=dy, flags=MOUSEEVENTF_WHEEL))
    return inputs


def build_mouse_click_inputs(button: str) -> list[INPUT]:
    flags = SUPPORTED_MOUSE_BUTTONS.get(button)
    if flags is None:
        raise ValueError(f"Unsupported mouse button: {button}")
    down_flag, up_flag = flags
    return [_make_mouse_input(flags=down_flag), _make_mouse_input(flags=up_flag)]


def build_mouse_button_inputs(button: str, action: str) -> list[INPUT]:
    flags = SUPPORTED_MOUSE_BUTTONS.get(button)
    if flags is None:
        raise ValueError(f"Unsupported mouse button: {button}")
    if action not in {"down", "up"}:
        raise ValueError(f"Unsupported mouse button action: {action}")
    down_flag, up_flag = flags
    return [_make_mouse_input(flags=down_flag if action == "down" else up_flag)]


def build_text_inputs(text: str) -> list[INPUT]:
    inputs: list[INPUT] = []
    for unit in _iter_utf16_units(text):
        if unit in (0x000A, 0x000D):
            inputs.extend(build_key_inputs("enter"))
            continue
        inputs.append(_make_unicode_input(unit, False))
        inputs.append(_make_unicode_input(unit, True))
    return inputs


def _send_inputs(inputs: list[INPUT]) -> None:
    if not inputs:
        return
    array_type = INPUT * len(inputs)
    payload = array_type(*inputs)
    sent = user32.SendInput(len(payload), payload, ctypes.sizeof(INPUT))
    if sent != len(payload):
        error_code = ctypes.get_last_error()
        raise OSError(error_code, f"SendInput failed. Sent {sent} of {len(payload)} events.")


def get_foreground_window_title() -> str:
    handle = user32.GetForegroundWindow()
    if not handle:
        return ""
    buffer = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(handle, buffer, len(buffer))
    return buffer.value


def type_text(text: str) -> dict:
    started_at = time.perf_counter()
    window_title = get_foreground_window_title()
    inputs = build_text_inputs(text)
    batch_size = TYPE_BATCH_CHARS * 2
    for offset in range(0, len(inputs), batch_size):
        _send_inputs(inputs[offset:offset + batch_size])
        if offset + batch_size < len(inputs):
            time.sleep(TYPE_BATCH_DELAY)
    return {
        "method": "sendinput-unicode",
        "windowTitle": window_title,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def press_key(key: str) -> dict:
    started_at = time.perf_counter()
    window_title = get_foreground_window_title()
    _send_inputs(build_key_inputs(key))
    return {
        "method": "sendinput-key",
        "key": key,
        "windowTitle": window_title,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def move_mouse(dx: int, dy: int) -> dict:
    started_at = time.perf_counter()
    _send_inputs(build_mouse_move_inputs(dx, dy))
    return {
        "method": "sendinput-mouse-move",
        "dx": dx,
        "dy": dy,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def scroll_mouse(dx: int, dy: int) -> dict:
    started_at = time.perf_counter()
    _send_inputs(build_mouse_scroll_inputs(dx, dy))
    return {
        "method": "sendinput-mouse-scroll",
        "dx": dx,
        "dy": dy,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def click_mouse(button: str) -> dict:
    started_at = time.perf_counter()
    _send_inputs(build_mouse_click_inputs(button))
    return {
        "method": "sendinput-mouse-click",
        "button": button,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def mouse_button(button: str, action: str) -> dict:
    started_at = time.perf_counter()
    _send_inputs(build_mouse_button_inputs(button, action))
    return {
        "method": "sendinput-mouse-button",
        "button": button,
        "action": action,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }


def _open_clipboard_with_retry(attempts: int = 4, delay: float = 0.05) -> None:
    for _ in range(attempts):
        if user32.OpenClipboard(None):
            return
        time.sleep(delay)
    raise OSError(ctypes.get_last_error(), "OpenClipboard failed (clipboard is busy).")


def set_clipboard_text(text: str) -> None:
    payload = (text + "\0").encode("utf-16-le")
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(payload))
    if not handle:
        raise OSError(ctypes.get_last_error(), "GlobalAlloc failed for clipboard text.")
    locked = kernel32.GlobalLock(handle)
    if not locked:
        kernel32.GlobalFree(handle)
        raise OSError(ctypes.get_last_error(), "GlobalLock failed for clipboard text.")
    try:
        ctypes.memmove(locked, payload, len(payload))
    finally:
        kernel32.GlobalUnlock(handle)

    _open_clipboard_with_retry()
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise OSError(ctypes.get_last_error(), "SetClipboardData failed.")
        handle = None  # Ownership transferred to the system on success.
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)



def _duplicate_memory_handle(handle: int) -> int:
    """Copy a clipboard global-memory block so it survives EmptyClipboard."""
    size = kernel32.GlobalSize(handle)
    if not size:
        return 0
    source = kernel32.GlobalLock(handle)
    if not source:
        return 0
    try:
        copy = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        if not copy:
            return 0
        target = kernel32.GlobalLock(copy)
        if not target:
            kernel32.GlobalFree(copy)
            return 0
        try:
            ctypes.memmove(target, source, size)
        finally:
            kernel32.GlobalUnlock(copy)
        return copy
    finally:
        kernel32.GlobalUnlock(handle)


def _duplicate_metafile_pict(handle: int) -> int:
    """Deep-copy a CF_METAFILEPICT memory block and its underlying metafile."""
    source = kernel32.GlobalLock(handle)
    if not source:
        return 0
    try:
        original = ctypes.cast(source, ctypes.POINTER(METAFILEPICT)).contents
        if not original.hMF:
            return 0
        new_hmetafile = gdi32.CopyMetaFileW(original.hMF, None)
        if not new_hmetafile:
            return 0
        copy = kernel32.GlobalAlloc(GMEM_MOVEABLE, ctypes.sizeof(METAFILEPICT))
        if not copy:
            gdi32.DeleteMetaFile(new_hmetafile)
            return 0
        target = kernel32.GlobalLock(copy)
        if not target:
            kernel32.GlobalFree(copy)
            gdi32.DeleteMetaFile(new_hmetafile)
            return 0
        try:
            ctypes.cast(target, ctypes.POINTER(METAFILEPICT)).contents = METAFILEPICT(
                original.mm, original.xExt, original.yExt, new_hmetafile
            )
        finally:
            kernel32.GlobalUnlock(copy)
        return copy
    finally:
        kernel32.GlobalUnlock(handle)


def _snapshot_clipboard() -> list[tuple[int, int]]:
    """Copy every restorable clipboard format into independent handles."""
    snapshot: list[tuple[int, int]] = []
    _open_clipboard_with_retry()
    try:
        fmt = user32.EnumClipboardFormats(0)
        while fmt:
            handle = user32.GetClipboardData(fmt)
            if handle:
                if fmt == CF_BITMAP:
                    copy = user32.CopyImage(handle, IMAGE_BITMAP, 0, 0, 0)
                elif fmt == CF_ENHMETAFILE:
                    copy = gdi32.CopyEnhMetaFileW(handle, None)
                elif fmt == CF_METAFILEPICT:
                    copy = _duplicate_metafile_pict(handle)
                elif fmt == CF_OWNERDISPLAY:
                    copy = 0
                else:
                    copy = _duplicate_memory_handle(handle)
                if copy:
                    snapshot.append((fmt, copy))
            fmt = user32.EnumClipboardFormats(fmt)
    finally:
        user32.CloseClipboard()
    return snapshot


def _free_gdi_handle(fmt: int, handle: int) -> None:
    if fmt == CF_BITMAP:
        gdi32.DeleteObject(handle)
    elif fmt == CF_ENHMETAFILE:
        gdi32.DeleteEnhMetaFile(handle)
    elif fmt == CF_METAFILEPICT:
        locked = kernel32.GlobalLock(handle)
        metafile = 0
        if locked:
            try:
                metafile = ctypes.cast(locked, ctypes.POINTER(METAFILEPICT)).contents.hMF
            finally:
                kernel32.GlobalUnlock(handle)
        if metafile:
            gdi32.DeleteMetaFile(metafile)
        kernel32.GlobalFree(handle)
    else:
        kernel32.GlobalFree(handle)


def _free_snapshot(snapshot: list[tuple[int, int]]) -> None:
    for fmt, handle in snapshot:
        _free_gdi_handle(fmt, handle)


def _restore_clipboard(snapshot: list[tuple[int, int]]) -> bool:
    """Restore a snapshot as a new clipboard-history head, then keep its successor."""
    if not snapshot:
        return False
    _open_clipboard_with_retry()
    try:
        user32.EmptyClipboard()
        all_ok = True
        for fmt, handle in snapshot:
            if user32.SetClipboardData(fmt, handle):
                continue
            all_ok = False
            _free_gdi_handle(fmt, handle)
        return all_ok
    finally:
        user32.CloseClipboard()


async def _history_has_current_text(text: str) -> bool:
    deadline = time.monotonic() + PASTE_HISTORY_TIMEOUT
    while time.monotonic() < deadline:
        try:
            result = await Clipboard.get_history_items_async()
            if result.status == ClipboardHistoryItemsResultStatus.SUCCESS and result.items:
                current = result.items[0].content
                if current.contains("Text") and await asyncio.wait_for(current.get_text_async(), 0.2) == text:
                    return True
        except Exception:
            return False
        await asyncio.sleep(PASTE_HISTORY_POLL_INTERVAL)
    return False


def _wait_for_clipboard_history_text(text: str) -> bool:
    """Wait until Windows clipboard history has indexed the newly pasted text."""
    return asyncio.run(_history_has_current_text(text))


async def _history_has_text_as_second_item(text: str) -> bool:
    deadline = time.monotonic() + PASTE_HISTORY_TIMEOUT
    while time.monotonic() < deadline:
        try:
            result = await Clipboard.get_history_items_async()
            if result.status == ClipboardHistoryItemsResultStatus.SUCCESS:
                items = list(result.items)
                if len(items) >= 2:
                    second = items[1].content
                    if second.contains("Text") and await asyncio.wait_for(second.get_text_async(), 0.2) == text:
                        return True
        except Exception:
            pass
        await asyncio.sleep(PASTE_HISTORY_POLL_INTERVAL)
    return False


def _wait_for_clipboard_history_second_item(text: str) -> bool:
    """Wait until the pasted text is the second Windows clipboard-history item."""
    return asyncio.run(_history_has_text_as_second_item(text))


def build_ctrl_v_inputs() -> list[INPUT]:
    return [
        _make_key_input(VK_CONTROL, False),
        _make_key_input(VK_V, False),
        _make_key_input(VK_V, True),
        _make_key_input(VK_CONTROL, True),
    ]


def paste_text(text: str) -> dict:
    started_at = time.perf_counter()
    window_title = get_foreground_window_title()
    snapshot = _snapshot_clipboard()
    try:
        set_clipboard_text(text)
        time.sleep(PASTE_SETTLE_DELAY)
        _send_inputs(build_ctrl_v_inputs())
    except Exception:
        _free_snapshot(snapshot)
        raise

    history_captured = _wait_for_clipboard_history_text(text)
    time.sleep(PASTE_RESTORE_DELAY)
    try:
        restored = _restore_clipboard(snapshot)
    except OSError:
        _free_snapshot(snapshot)
        restored = False
    history_ordered = _wait_for_clipboard_history_second_item(text) if restored else False
    return {
        "method": "clipboard-paste",
        "windowTitle": window_title,
        "charCount": len(text),
        "clipboardRestored": restored,
        "clipboardHistoryCaptured": history_captured,
        "clipboardHistoryOrdered": history_ordered,
        "durationMs": int((time.perf_counter() - started_at) * 1000),
    }
