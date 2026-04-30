from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys


APP_NAME = "RemoteInputBoard"
DATA_SEPARATOR = ";" if os.name == "nt" else ":"


def build_pyinstaller_args(project_root: Path) -> list[str]:
    package_dir = project_root / "py_remote_input"
    templates_dir = package_dir / "templates"
    entrypoint = package_dir / "__main__.py"
    work_dir = project_root / "build" / "pyinstaller"
    spec_dir = project_root / "build" / "pyinstaller"
    dist_dir = project_root / "dist"

    return [
        "--noconfirm",
        "--clean",
        "--onefile",
        "--console",
        "--name",
        APP_NAME,
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
        "--distpath",
        str(dist_dir),
        "--add-data",
        f"{templates_dir}{DATA_SEPARATOR}py_remote_input/templates",
        str(entrypoint),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Windows exe with bundled web resources.")
    parser.add_argument(
        "--show-command",
        action="store_true",
        help="Print the PyInstaller command before running it.",
    )
    return parser.parse_args()


def build_runner_command() -> list[str]:
    if importlib.util.find_spec("PyInstaller") is not None:
        return [sys.executable, "-m", "PyInstaller"]

    uv_path = shutil.which("uv")
    if uv_path is not None:
        return [uv_path, "run", "--with", "pyinstaller", "pyinstaller"]

    raise RuntimeError(
        "PyInstaller is not installed, and uv was not found. "
        "Install PyInstaller once with: python -m pip install pyinstaller"
    )


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    pyinstaller_args = build_pyinstaller_args(project_root)
    try:
        command = [*build_runner_command(), *pyinstaller_args]
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.show_command:
        print(" ".join(command))

    try:
        subprocess.run(command, cwd=project_root, check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    exe_path = project_root / "dist" / f"{APP_NAME}.exe"
    print(f"Built {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
