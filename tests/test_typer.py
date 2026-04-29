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


if __name__ == "__main__":
    unittest.main()
