from __future__ import annotations

import ctypes
from ctypes import wintypes
import time


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
VK_RETURN = 0x0D
VK_UP = 0x26
VK_DOWN = 0x28
VK_DELETE = 0x2E

SUPPORTED_KEYS = {
    "backspace": VK_BACK,
    "delete": VK_DELETE,
    "down": VK_DOWN,
    "enter": VK_RETURN,
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
    _send_inputs(build_text_inputs(text))
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
