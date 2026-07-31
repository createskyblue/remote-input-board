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
            day_dir = Path(temp_dir) / "history" / "2026-08-01"
            day_dir.mkdir(parents=True)
            (day_dir / "10.log").write_text(
                "\n".join(
                    [
                        json.dumps({"kind": "text", "text": "你好"}),
                        json.dumps({"kind": "key", "key": "enter"}),
                        "not json",
                    ]
                ),
                encoding="utf-8",
            )
            (day_dir / "11.log").write_text(
                json.dumps({"kind": "text", "text": "A🙂"}), encoding="utf-8"
            )

            self.assertEqual(count_text_history_chars(day_dir.parent), 4)

    def test_type_request_returns_sent_chars_and_backup_total(self):
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
            # 发送响应带回本次字数 sentChars；服务器不再自行累加，累计数以手机上报为准（stats.json 只是备份）
            self.assertEqual(payload["sentChars"], 3)
            self.assertEqual(payload["totalChars"], 10)
            self.assertEqual(json.loads((Path(temp_dir) / "stats.json").read_text(encoding="utf-8"))["totalChars"], 10)

    def test_save_total_chars_overwrites_backup_total(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TextStatsStore(Path(temp_dir) / "stats.json", initial_total_chars=10)

            self.assertEqual(store.save_total_chars(5000), 5000)
            self.assertEqual(store.get_total_chars(), 5000)
            store.flush()
            self.assertEqual(json.loads((Path(temp_dir) / "stats.json").read_text(encoding="utf-8"))["totalChars"], 5000)

    def test_save_total_chars_stays_in_memory_until_flush_due(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TextStatsStore(Path(temp_dir) / "stats.json", initial_total_chars=10, flush_interval=600)

            self.assertEqual(store.save_total_chars(5000), 5000)
            # 5 分钟缓存：未到落盘时间，文件仍是旧值
            self.assertEqual(json.loads((Path(temp_dir) / "stats.json").read_text(encoding="utf-8"))["totalChars"], 10)
            store.flush()
            self.assertEqual(json.loads((Path(temp_dir) / "stats.json").read_text(encoding="utf-8"))["totalChars"], 5000)

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
            day_dir = log_dir / "history" / "2026-08-01"
            day_dir.mkdir(parents=True)
            (day_dir / "09.log").write_text(
                json.dumps({"kind": "text", "text": "旧数据"}) + "\n", encoding="utf-8"
            )

            recorder, store = build_history_recorder(log_dir, log_dir / "stats.json")
            recorder({"kind": "text", "text": "新"})

            self.assertEqual(store.get_total_chars(), 3)

    def test_history_recorder_writes_to_daily_hourly_files(self):
        import re

        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            recorder, _store = build_history_recorder(log_dir, log_dir / "stats.json")

            recorder({"kind": "text", "text": "记录"})

            files = sorted((log_dir / "history").rglob("*.log"))
            self.assertEqual(len(files), 1)
            payload = json.loads(files[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["text"], "记录")
            self.assertRegex(files[0].parent.name, r"^\d{4}-\d{2}-\d{2}$")
            self.assertRegex(files[0].name, r"^\d{2}\.log$")


if __name__ == "__main__":
    unittest.main()
