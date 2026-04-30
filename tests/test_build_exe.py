from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_exe  # noqa: E402


class BuildExeTests(unittest.TestCase):
    def test_pyinstaller_args_bundle_templates(self):
        args = build_exe.build_pyinstaller_args(ROOT)

        self.assertIn("--onefile", args)
        self.assertIn("--name", args)
        self.assertIn("RemoteInputBoard", args)
        self.assertIn(
            f"{ROOT / 'py_remote_input' / 'templates'}{build_exe.DATA_SEPARATOR}py_remote_input/templates",
            args,
        )
        self.assertEqual(args[-1], str(ROOT / "py_remote_input" / "__main__.py"))


if __name__ == "__main__":
    unittest.main()
