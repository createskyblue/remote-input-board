import ctypes
import unittest

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


if __name__ == "__main__":
    unittest.main()
