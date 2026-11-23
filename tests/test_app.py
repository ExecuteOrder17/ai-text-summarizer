"""Checks of actual input/output behavior and the classroom demonstration flow."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from summarizer import summarize, split_sentences, SAMPLE
from app import SummarizerApp
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt


class AlgorithmTests(unittest.TestCase):
    def test_blank_input(self):
        for text in ("", "  ", "\n\t"):
            self.assertEqual(summarize(text), "")

    def test_short_input_is_preserved(self):
        for text in ("One thought", "First sentence.\nSecond sentence!", "No punctuation at all"):
            self.assertEqual(summarize("  " + text + " \n"), text)

    def test_first_two_keep_their_original_punctuation(self):
        self.assertEqual(summarize("One! Two? Three."), "One! Two?")
        self.assertEqual(summarize("One. Two. Three."), "One. Two.")
        self.assertEqual(summarize("One.\n\nTwo!\tThree?"), "One. Two!")

    def test_sample_is_six_sentences_reduced_to_two(self):
        self.assertEqual(len(split_sentences(SAMPLE)), 6)
        self.assertEqual(split_sentences(summarize(SAMPLE)), split_sentences(SAMPLE)[:2])

    def test_unicode_is_retained(self):
        self.assertEqual(summarize("Café notes. Study résumé. More details."), "Café notes. Study résumé.")


class DesktopWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setStyle("Fusion")

    def setUp(self):
        self.w = SummarizerApp()
        self.w.show()
        self.qt.processEvents()

    def tearDown(self):
        self.w.close()
        self.qt.processEvents()

    def test_empty_validation_and_short_text(self):
        QTest.mouseClick(self.w.run_btn, Qt.LeftButton)
        self.assertIn("Please enter", self.w.notice.text())
        self.assertEqual(self.w.output.toPlainText(), "")
        self.assertFalse(self.w.copy_btn.isEnabled())
        self.w.input.setPlainText("Just one sentence.")
        QTest.mouseClick(self.w.run_btn, Qt.LeftButton)
        self.assertEqual(self.w.output.toPlainText(), "Just one sentence.")
        self.assertIn("unchanged", self.w.notice.text())
        self.assertEqual(self.w.stat_values[2].text(), "0%")

    def test_sample_copy_save_and_invalidation(self):
        QTest.mouseClick(self.w.sample_btn, Qt.LeftButton)
        QTest.mouseClick(self.w.run_btn, Qt.LeftButton)
        self.assertEqual(self.w.output.toPlainText(), summarize(SAMPLE))
        self.assertEqual(self.w.stat_values[0].text(), "2 / 6")
        QTest.mouseClick(self.w.copy_btn, Qt.LeftButton)
        self.assertEqual(self.qt.clipboard().text(), summarize(SAMPLE))
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / "saved.txt"
            with patch("app.QFileDialog.getSaveFileName", return_value=(str(dest), "")):
                self.w.save_summary()
            self.assertEqual(dest.read_text(encoding="utf-8"), summarize(SAMPLE) + "\n")
        self.w.input.insertPlainText("Changed ")
        self.assertEqual(self.w.output.toPlainText(), "")
        self.assertFalse(self.w.copy_btn.isEnabled())
        self.assertFalse(self.w.save_btn.isEnabled())
        QTest.mouseClick(self.w.clear_btn, Qt.LeftButton)
        self.assertEqual(self.w.input.toPlainText(), "")
        self.assertEqual(self.w.input_meta.text(), "0 words · 0 sentences")

    def test_import_unicode_bom_and_bad_encoding(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "notes.txt"
            p.write_text("Café. More notes. Extra.", encoding="utf-8-sig")
            with patch("app.QFileDialog.getOpenFileName", return_value=(str(p), "")):
                self.w.open_text()
            self.assertEqual(self.w.input.toPlainText(), "Café. More notes. Extra.")
            p.write_bytes(b"\xff\xff\xff")
            with patch("app.QFileDialog.getOpenFileName", return_value=(str(p), "")):
                self.w.open_text()
            self.assertTrue(self.w.notice.property("error"))
            self.assertIn("UTF-8", self.w.notice.text())

    def test_cancelled_dialogs_and_failed_save(self):
        self.w.load_sample()
        self.w.run_summary()
        with patch("app.QFileDialog.getOpenFileName", return_value=("", "")):
            self.w.open_text()
        self.assertEqual(self.w.output.toPlainText(), summarize(SAMPLE))
        with patch("app.QFileDialog.getSaveFileName", return_value=("", "")):
            self.w.save_summary()
        with tempfile.TemporaryDirectory() as folder:
            bad = str(Path(folder) / "missing" / "out.txt")
            with patch("app.QFileDialog.getSaveFileName", return_value=(bad, "")):
                self.w.save_summary()
            self.assertTrue(self.w.notice.property("error"))
            self.assertIn("could not be saved", self.w.notice.text())

    def test_guided_demo_and_navigation(self):
        QTest.mouseClick(self.w.demo_btn, Qt.LeftButton)
        self.assertEqual(self.w.input.toPlainText(), SAMPLE)
        QTest.mouseClick(self.w.demo_btn, Qt.LeftButton)
        self.assertEqual(self.w.output.toPlainText(), summarize(SAMPLE))
        QTest.mouseClick(self.w.demo_btn, Qt.LeftButton)
        self.assertEqual(self.w.stack.currentIndex(), 1)
        self.assertIn("Split", self.w.step_title.text())
        for i in range(5):
            QTest.mouseClick(self.w.steps[i], Qt.LeftButton)
            self.assertTrue(self.w.steps[i].isChecked())
            self.assertIn(f"0{i+1}", self.w.step_number.text())
        for i in (2, 0, 1, 2, 0):
            QTest.mouseClick(self.w.nav[i], Qt.LeftButton)
            QTest.qWait(260)
            self.assertEqual(self.w.stack.currentIndex(), i)
            self.assertTrue(self.w.nav[i].isChecked())

    def test_layout_at_minimum_and_large_sizes(self):
        for width, height in ((960, 720), (1280, 860), (1920, 1080)):
            self.w.resize(width, height)
            for index in range(3):
                self.w.navigate(index)
                QTest.qWait(260)
                self.assertEqual(self.w.width(), width)
                self.assertEqual(self.w.height(), height)
                self.assertGreaterEqual(self.w.input.height(), 115)


if __name__ == "__main__":
    unittest.main()
