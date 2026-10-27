import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile

import soundfile as sf

from apps.chapter_speech import parse_chapters, run_chapters


class ChapterTests(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(parse_chapters("# CHƯƠNG 1: Mở đầu\nXin chào\n\n**CHƯƠNG 2**\nKết thúc"),
                         [("CHƯƠNG 1: Mở đầu", "Xin chào"), ("CHƯƠNG 2", "Kết thúc")])
        for script in ("Văn bản", "CHƯƠNG 1\n", "Lời ngoài\nCHƯƠNG 1\nA",
                       "CHƯƠNG 1\nA\nCHƯƠNG 1\nB"):
            with self.assertRaises(ValueError):
                parse_chapters(script)

    def test_retry_edit_and_merge(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
                "os.environ", {"VIENEU_CHAPTER_OUTPUT_DIR": tmp}):
            source = str(Path(tmp) / "sample.wav")
            sf.write(source, [0.1] * 160, 16000)
            calls = []
            fail = [True]
            def synthesize(text):
                calls.append(text)
                if text == "B" and fail[0]:
                    yield None, "Lỗi thử nghiệm"
                else:
                    yield source, "Xong"
            script = "CHƯƠNG 1\nA\nCHƯƠNG 2\nB"
            first = list(run_chapters(script, {}, None, synthesize, lambda: False))[-1]
            self.assertEqual(len(first[2]), 1)
            fail[0] = False
            second = list(run_chapters(script, {}, first[0], synthesize, lambda: False, True))[-1]
            self.assertEqual(calls, ["A", "B", "B"])
            self.assertEqual(sf.info(second[4]).frames, 320)
            with zipfile.ZipFile(second[3]) as archive:
                self.assertEqual(set(archive.namelist()), {"01.wav", "02.wav", "full.wav", "chapters.json"})
            list(run_chapters(script.replace("\nB", "\nC"), {}, second[0], synthesize, lambda: False))
            self.assertEqual(calls[-1], "C")
            self.assertEqual(len(calls), 4)
            list(run_chapters(script, {"voice": "other"}, second[0], synthesize, lambda: False))
            self.assertEqual(calls[-2:], ["A", "B"])

    def test_stop_does_not_cache_partial_chapter(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
                "os.environ", {"VIENEU_CHAPTER_OUTPUT_DIR": tmp}):
            stopped = [False]
            def synthesize(text):
                stopped[0] = True
                yield None, "Đang chạy"
            result = list(run_chapters("CHƯƠNG 1\nA", {}, None, synthesize, lambda: stopped[0]))[-1]
            self.assertEqual(result[0]["cache"], {})
            self.assertEqual(result[2], [])
            self.assertIn("Đã dừng", result[1])


if __name__ == "__main__":
    unittest.main()
