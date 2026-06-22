import json
import tempfile
import unittest
from pathlib import Path

from py_remote_input.server import build_history_recorder
from py_remote_input.stats import TextStatsStore, count_text_history_chars
from py_remote_input.web import handle_request


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, meta=None):
        self.messages.append(("info", message, meta))

    def warn(self, message, meta=None):
        self.messages.append(("warn", message, meta))

    def error(self, message, meta=None):
        self.messages.append(("error", message, meta))


class TextStatsTests(unittest.TestCase):
    def test_counts_only_text_history_characters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "input-history.log"
            history_file.write_text(
                "\n".join(
                    [
                        json.dumps({"kind": "text", "text": "你好"}),
                        json.dumps({"kind": "key", "key": "enter"}),
                        "not json",
                        json.dumps({"kind": "text", "text": "A🙂"}),
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(count_text_history_chars(history_file), 4)

    def test_type_request_adds_and_returns_persisted_total_chars(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TextStatsStore(Path(temp_dir) / "stats.json", initial_total_chars=10)

            response = handle_request(
                "POST",
                "/api/type",
                json.dumps({"text": "你好🙂"}).encode("utf-8"),
                lambda _text: {"method": "sendinput-unicode", "durationMs": 7, "windowTitle": "Notepad"},
                FakeLogger(),
                text_stats=store,
            )

            payload = json.loads(response.body.decode("utf-8"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(payload["totalChars"], 13)
            self.assertEqual(json.loads((Path(temp_dir) / "stats.json").read_text(encoding="utf-8"))["totalChars"], 13)

    def test_stats_endpoint_returns_persisted_total_chars(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TextStatsStore(Path(temp_dir) / "stats.json", initial_total_chars=42)

            response = handle_request(
                "GET",
                "/api/stats",
                b"",
                lambda _text: {},
                FakeLogger(),
                text_stats=store,
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.body.decode("utf-8"))["totalChars"], 42)

    def test_history_recorder_seeds_stats_from_existing_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            history_file = log_dir / "input-history.log"
            stats_file = log_dir / "stats.json"
            history_file.write_text(json.dumps({"kind": "text", "text": "旧数据"}) + "\n", encoding="utf-8")

            recorder, store = build_history_recorder(history_file, stats_file)
            recorder({"kind": "text", "text": "新"})

            self.assertEqual(store.get_total_chars(), 3)


if __name__ == "__main__":
    unittest.main()
