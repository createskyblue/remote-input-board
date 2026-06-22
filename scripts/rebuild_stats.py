from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from py_remote_input.stats import count_text_history_chars


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild total character stats from input history.")
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("dist") / "logs" / "input-history.log",
        help="Input history JSONL file.",
    )
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("dist") / "logs" / "stats.json",
        help="Stats JSON file to write.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    total = count_text_history_chars(args.history)
    args.stats.parent.mkdir(parents=True, exist_ok=True)
    args.stats.write_text(json.dumps({"totalChars": total}, ensure_ascii=False) + "\n", encoding="utf-8")
    print(total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
