import ctypes
import unittest
from unittest import mock

from py_remote_input import typer


class TyperTests(unittest.TestCase):
    def test_newline_maps_to_enter_key(self):
        inputs = typer.build_text_inputs("a\nb")
        self.assertEqual(inputs[2].ki.wVk, typer.VK_RETURN)
        self.assertEqual(inputs[3].ki.wVk, typer.VK_RETURN)

    def test_regular_text_uses_unicode_input(self):
        inputs = typer.build_text_inputs("你")
        self.assertEqual(inputs[0].ki.wVk, 0)
        self.assertEqual(inputs[0].ki.dwFlags & typer.KEYEVENTF_UNICODE, typer.KEYEVENTF_UNICODE)

    def test_backspace_key_supported(self):
        inputs = typer.build_key_inputs("backspace")
        self.assertEqual(inputs[0].ki.wVk, typer.VK_BACK)
        self.assertEqual(inputs[1].ki.wVk, typer.VK_BACK)

    def test_escape_key_supported(self):
        inputs = typer.build_key_inputs("escape")
        self.assertEqual(inputs[0].ki.wVk, typer.VK_ESCAPE)
        self.assertEqual(inputs[1].ki.wVk, typer.VK_ESCAPE)

    def test_arrow_keys_supported(self):
        up_inputs = typer.build_key_inputs("up")
        down_inputs = typer.build_key_inputs("down")

        self.assertEqual(up_inputs[0].ki.wVk, typer.VK_UP)
        self.assertEqual(up_inputs[1].ki.wVk, typer.VK_UP)
        self.assertEqual(down_inputs[0].ki.wVk, typer.VK_DOWN)
        self.assertEqual(down_inputs[1].ki.wVk, typer.VK_DOWN)

    def test_mouse_move_uses_relative_mouse_input(self):
        inputs = typer.build_mouse_move_inputs(12, -7)

        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].type, typer.INPUT_MOUSE)
        self.assertEqual(inputs[0].mi.dx, 12)
        self.assertEqual(inputs[0].mi.dy, -7)
        self.assertEqual(inputs[0].mi.dwFlags, typer.MOUSEEVENTF_MOVE)

    def test_mouse_scroll_uses_wheel_inputs(self):
        inputs = typer.build_mouse_scroll_inputs(120, -240)

        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0].type, typer.INPUT_MOUSE)
        self.assertEqual(inputs[0].mi.dwFlags, typer.MOUSEEVENTF_HWHEEL)
        self.assertEqual(ctypes.c_int32(inputs[0].mi.mouseData).value, 120)
        self.assertEqual(inputs[1].mi.dwFlags, typer.MOUSEEVENTF_WHEEL)
        self.assertEqual(ctypes.c_int32(inputs[1].mi.mouseData).value, -240)

    def test_mouse_buttons_supported(self):
        left_inputs = typer.build_mouse_click_inputs("left")
        right_inputs = typer.build_mouse_click_inputs("right")

        self.assertEqual(left_inputs[0].mi.dwFlags, typer.MOUSEEVENTF_LEFTDOWN)
        self.assertEqual(left_inputs[1].mi.dwFlags, typer.MOUSEEVENTF_LEFTUP)
        self.assertEqual(right_inputs[0].mi.dwFlags, typer.MOUSEEVENTF_RIGHTDOWN)
        self.assertEqual(right_inputs[1].mi.dwFlags, typer.MOUSEEVENTF_RIGHTUP)

    def test_mouse_button_hold_actions_supported(self):
        left_down = typer.build_mouse_button_inputs("left", "down")
        left_up = typer.build_mouse_button_inputs("left", "up")

        self.assertEqual(len(left_down), 1)
        self.assertEqual(len(left_up), 1)
        self.assertEqual(left_down[0].mi.dwFlags, typer.MOUSEEVENTF_LEFTDOWN)
        self.assertEqual(left_up[0].mi.dwFlags, typer.MOUSEEVENTF_LEFTUP)

    def test_ctrl_v_inputs_press_control_v_in_order(self):
        inputs = typer.build_ctrl_v_inputs()

        self.assertEqual(len(inputs), 4)
        self.assertEqual([i.ki.wVk for i in inputs], [typer.VK_CONTROL, typer.VK_V, typer.VK_V, typer.VK_CONTROL])
        self.assertEqual(inputs[0].ki.dwFlags, 0)
        self.assertEqual(inputs[1].ki.dwFlags, 0)
        self.assertEqual(inputs[2].ki.dwFlags & typer.KEYEVENTF_KEYUP, typer.KEYEVENTF_KEYUP)
        self.assertEqual(inputs[3].ki.dwFlags & typer.KEYEVENTF_KEYUP, typer.KEYEVENTF_KEYUP)

    def test_snapshot_clipboard_duplicates_memory_formats(self):
        with (
            mock.patch.object(typer, "user32") as user32,
            mock.patch.object(typer, "_duplicate_memory_handle", return_value=999) as duplicate,
            mock.patch.object(typer, "_open_clipboard_with_retry", return_value=None),
        ):
            user32.EnumClipboardFormats.side_effect = [typer.CF_UNICODETEXT, 0]
            user32.GetClipboardData.return_value = 123

            snapshot = typer._snapshot_clipboard()

        self.assertEqual(snapshot, [(typer.CF_UNICODETEXT, 999)])
        duplicate.assert_called_once_with(123)

    def test_duplicate_memory_handle_copies_bytes(self):
        with (
            mock.patch.object(typer, "kernel32") as kernel32,
            mock.patch.object(typer, "ctypes") as ctypes_mock,
        ):
            kernel32.GlobalSize.return_value = 4
            kernel32.GlobalLock.side_effect = [0x1000, 0x2000]
            kernel32.GlobalAlloc.return_value = 0x3000

            result = typer._duplicate_memory_handle(0x1111)

        self.assertEqual(result, 0x3000)
        kernel32.GlobalAlloc.assert_called_once_with(typer.GMEM_MOVEABLE, 4)
        ctypes_mock.memmove.assert_called_once_with(0x2000, 0x1000, 4)
        self.assertEqual(kernel32.GlobalUnlock.call_args_list, [mock.call(0x3000), mock.call(0x1111)])

    def test_restore_clipboard_frees_failed_formats(self):
        with (
            mock.patch.object(typer, "user32") as user32,
            mock.patch.object(typer, "_free_gdi_handle") as free_gdi,
            mock.patch.object(typer, "_open_clipboard_with_retry", return_value=None),
        ):
            user32.SetClipboardData.side_effect = [1, 0]

            restored = typer._restore_clipboard([(typer.CF_UNICODETEXT, 11), (0xC148, 22)])

        self.assertFalse(restored)
        free_gdi.assert_called_once_with(0xC148, 22)

    def test_restore_clipboard_with_empty_snapshot_returns_false(self):
        self.assertFalse(typer._restore_clipboard([]))

    def test_paste_fast_path_timing_budget_is_short(self):
        self.assertLessEqual(typer.PASTE_SETTLE_DELAY, 0.03)
        self.assertLessEqual(typer.PASTE_HISTORY_TIMEOUT, 0.4)
        self.assertLessEqual(typer.PASTE_HISTORY_POLL_INTERVAL, 0.02)
        self.assertLessEqual(typer.PASTE_RESTORE_DELAY, 0.12)

    def test_paste_restores_previous_clipboard_after_history_capture(self):
        snapshot = [(typer.CF_UNICODETEXT, 7)]
        with (
            mock.patch.object(typer, "_snapshot_clipboard", return_value=snapshot, create=True) as take_snapshot,
            mock.patch.object(typer, "set_clipboard_text", return_value=None) as set_clipboard,
            mock.patch.object(typer, "_send_inputs", return_value=None) as send_inputs,
            mock.patch.object(typer, "_wait_for_clipboard_history_text", return_value=True, create=True) as wait_history,
            mock.patch.object(typer, "_restore_clipboard", return_value=True, create=True) as restore,
            mock.patch.object(typer, "get_foreground_window_title", return_value="Remote Desktop"),
            mock.patch.object(typer.time, "sleep", return_value=None) as sleep,
        ):
            result = typer.paste_text("新内容")

        take_snapshot.assert_called_once_with()
        set_clipboard.assert_called_once_with("新内容")
        send_inputs.assert_called_once()
        wait_history.assert_called_once_with("新内容")
        restore.assert_called_once_with(snapshot)
        self.assertEqual(result["clipboardRestored"], True)
        self.assertTrue(result["clipboardHistoryCaptured"])
        self.assertTrue(result["clipboardHistoryOrdered"])
        self.assertEqual(result["charCount"], 3)
        self.assertIn(mock.call(typer.PASTE_SETTLE_DELAY), sleep.call_args_list)
        self.assertIn(mock.call(typer.PASTE_RESTORE_DELAY), sleep.call_args_list)

    def test_paste_restores_after_timeout_when_history_is_unavailable(self):
        snapshot = [(typer.CF_UNICODETEXT, 7)]
        with (
            mock.patch.object(typer, "_snapshot_clipboard", return_value=snapshot, create=True),
            mock.patch.object(typer, "set_clipboard_text", return_value=None),
            mock.patch.object(typer, "_send_inputs", return_value=None),
            mock.patch.object(typer, "_wait_for_clipboard_history_text", return_value=False, create=True) as wait_history,
            mock.patch.object(typer, "_restore_clipboard", return_value=True, create=True) as restore,
            mock.patch.object(typer, "get_foreground_window_title", return_value="Remote Desktop"),
            mock.patch.object(typer.time, "sleep", return_value=None),
        ):
            result = typer.paste_text("新内容")

        wait_history.assert_called_once_with("新内容")
        restore.assert_called_once_with(snapshot)
        self.assertEqual(result["clipboardRestored"], True)
        self.assertFalse(result["clipboardHistoryCaptured"])
        self.assertFalse(result["clipboardHistoryOrdered"])


if __name__ == "__main__":
    unittest.main()
