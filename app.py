"""AI Text Summarizer — a native, offline desktop presentation app."""
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QRectF
from PySide6.QtGui import (
    QColor, QPainter, QPixmap, QIcon, QFont, QLinearGradient, QKeySequence,
    QShortcut, QDesktopServices, QPainterPath,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QPlainTextEdit, QStackedWidget, QFileDialog,
    QGraphicsOpacityEffect, QScrollArea, QSizePolicy,
)

from summarizer import summarize, split_sentences, word_count, SAMPLE, SENTENCE_PATTERN

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS = BASE / "assets"

STYLE = """
QWidget { color: #173b3e; font-family: 'Segoe UI', 'Inter', 'DejaVu Sans'; font-size: 13px; }
QLabel { background: transparent; }
QFrame#header { background: rgba(9, 34, 37, 228); border: 1px solid rgba(231,245,239,45); border-radius: 22px; }
QLabel#brand { color: #f4f7ef; font-size: 17px; font-weight: 700; }
QLabel#brandSub { color: #b6c9c5; font-size: 10px; letter-spacing: 2px; }
QLabel#offline { color: #d8ead8; font-size: 11px; padding: 8px; }
QPushButton { background: #edf2e9; border: 1px solid #d4dfd7; border-radius: 12px; padding: 10px 16px; font-weight: 600; }
QPushButton:hover { background: #dfebdf; border-color: #9cb9a9; }
QPushButton:pressed { background: #ccdfcf; }
QPushButton:focus { border: 2px solid #6f9b87; }
QPushButton:disabled { color: #96a7a2; background: #e9ede7; border-color: #e3e8e1; }
QPushButton#primary { background: #204d43; color: #f8fcf3; border-color: #204d43; padding: 12px 24px; }
QPushButton#primary:hover { background: #326657; border-color: #326657; }
QPushButton#primary:pressed { background: #173e35; }
QPushButton#nav { background: transparent; color: #c2d3cc; border: none; border-radius: 14px; padding: 10px 18px; }
QPushButton#nav:checked { background: #e9f0e2; color: #20483f; }
QPushButton#nav:hover { background: rgba(239,248,235,35); }
QPushButton#nav:checked:hover { background: #f4f7ec; }
QPushButton#quiet { background: transparent; border: none; color: #466b5d; padding: 8px 10px; }
QPushButton#quiet:hover { background: #e6eee1; }
QLabel#eyebrow { color: #f0f7e7; font-size: 10px; font-weight: 700; letter-spacing: 3px; }
QLabel#hero { color: #f6faf2; font-size: 42px; font-weight: 600; letter-spacing: -1px; }
QLabel#subtitle { color: #e4efe7; font-size: 13px; }
QFrame#panel { background: rgba(247,249,240,246); border: 1px solid rgba(255,255,255,220); border-radius: 23px; }
QFrame#pane { background: #f1f5eb; border: 1px solid #dbe4d6; border-radius: 17px; }
QFrame#resultPane { background: #eaf1e5; border: 1px solid #d1ddca; border-radius: 17px; }
QLabel#section { font-size: 19px; font-weight: 650; }
QLabel#muted { color: #6b8078; font-size: 11px; }
QLabel#tiny { color: #6b8078; font-size: 10px; }
QLabel#number { color: #859e8e; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#tag { background: #dce8d5; color: #466546; border-radius: 9px; padding: 5px 9px; font-size: 10px; font-weight: 700; }
QPlainTextEdit { background: transparent; border: none; padding: 0; color: #24473f; font-size: 15px; selection-background-color: #c2d7b8; selection-color: #183d31; }
QPlainTextEdit:focus { border: none; }
QScrollBar:vertical { background: transparent; width: 7px; margin: 2px; }
QScrollBar::handle:vertical { background: #afc3b2; border-radius: 2px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QLabel#stat { font-size: 22px; font-weight: 650; }
QFrame#divider { background: #d5dfd1; max-width: 1px; }
QLabel#footer { color: #e4eee3; font-size: 11px; }
QLabel#notice { background: #e3ecda; color: #35593f; border-radius: 10px; padding: 9px 12px; font-size: 12px; }
QLabel#notice[error="true"] { background: #f4e2d7; color: #873d31; }
QPushButton#step { text-align: left; background: transparent; border: 1px solid #d4dfcf; padding: 15px; font-size: 13px; }
QPushButton#step:checked { background: #204d43; color: white; border-color: #204d43; }
QLabel#body { color: #496356; font-size: 14px; }
QLabel#code { background: #183e37; color: #e5efcf; border-radius: 14px; padding: 20px; font-family: 'Consolas', 'DejaVu Sans Mono'; font-size: 13px; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
"""


def label(text, name=None, wrap=False):
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    w.setWordWrap(wrap)
    return w


def button(text, callback=None, name=None):
    b = QPushButton(text)
    b.setCursor(Qt.PointingHandCursor)
    if name:
        b.setObjectName(name)
    if callback:
        b.clicked.connect(callback)
    return b


def row(*widgets):
    layout = QHBoxLayout()
    layout.setSpacing(10)
    for widget in widgets:
        if widget is None:
            layout.addStretch()
        else:
            layout.addWidget(widget)
    return layout


class Artwork(QWidget):
    def __init__(self, path, radius=14):
        super().__init__()
        self.pix = QPixmap(str(path))
        self.radius = radius

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.radius, self.radius)
        painter.setClipPath(path)
        if not self.pix.isNull():
            pix = self.pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            painter.drawPixmap((self.width()-pix.width())//2, (self.height()-pix.height())//2, pix)


class Scenery(QWidget):
    def __init__(self):
        super().__init__()
        self.pix = QPixmap(str(ASSETS / "train-view.png"))
        self.cached_size = None
        self.scaled = QPixmap()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#153d3c"))
        if not self.pix.isNull():
            if self.cached_size != self.size():
                self.scaled = self.pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.cached_size = self.size()
            p.drawPixmap((self.width()-self.scaled.width())//2, (self.height()-self.scaled.height())//2, self.scaled)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(9, 34, 34, 85))
        g.setColorAt(.4, QColor(9, 34, 34, 50))
        g.setColorAt(1, QColor(9, 34, 34, 150))
        p.fillRect(self.rect(), g)


STEPS = [
    ("Read the paragraph", "The input box accepts typed text, pasted notes or a UTF-8 text file. No text is sent to a server.", 'text = input_text.strip()'),
    ("Check for empty input", "If the paragraph is empty or contains only spaces, the app asks for text and leaves the summary empty.", 'if not text:\n    show_message("Please enter some text.")'),
    ("Split into sentences", "The regular expression splits at whitespace after a full stop, exclamation mark or question mark. Punctuation stays with each sentence.", 'sentences = re.split(\n    r"(?<=[.!?])\\s+", text\n)'),
    ("Keep the first two", "This project uses the lead-sentence approach. With two sentences or fewer, the original text is returned. Otherwise the first two are joined with a space.", 'summary = (text if len(sentences) <= 2\n           else " ".join(sentences[:2]))'),
    ("Display the result", "The result appears beside the original. Compare sentence and word counts, copy the summary or save it as a text file.", 'result_box.setPlainText(summary)'),
]


class SummarizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Text Summarizer · Saumya 078")
        self.setWindowIcon(QIcon(str(ASSETS / "ai-brand.png")))
        self.resize(1280, 860)
        self.setMinimumSize(960, 720)
        self.setStyleSheet(STYLE)
        self._summary = ""
        self._animations = []
        self.demo_index = -1
        self.bg = Scenery()
        self.setCentralWidget(self.bg)
        outer = QVBoxLayout(self.bg)
        outer.setContentsMargins(32, 22, 32, 18)
        outer.setSpacing(15)
        self.make_header(outer)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: transparent; }")
        self.workspace = self.make_workspace()
        self.process = self.make_process()
        self.project = self.make_project()
        for page in (self.workspace, self.process, self.project):
            self.stack.addWidget(page)
        outer.addWidget(self.stack, 1)
        outer.addLayout(row(label("SAUMYA  /  ROLL NO. 078", "footer"), None,
                            label("A Python project, with a clearer view.", "footer"), None,
                            label("F11  Presentation view", "footer")))
        self.nav[0].setChecked(True)
        self.shortcuts = []
        for keys, callback in [
            ("Ctrl+Return", self.run_summary), ("Ctrl+O", self.open_text),
            ("Ctrl+Shift+S", self.save_summary), ("Ctrl+L", self.clear),
            ("F11", self.toggle_fullscreen), ("Escape", self.leave_fullscreen),
        ]:
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)
        self.input.textChanged.connect(self.input_changed)
        self.input_changed()

    def make_header(self, outer):
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 10, 18, 10)
        icon = Artwork(ASSETS / "ai-brand.png", 12)
        icon.setFixedSize(48, 48)
        layout.addWidget(icon)
        brand = QVBoxLayout()
        brand.setSpacing(3)
        brand.addWidget(label("AI Text Summarizer", "brand"))
        brand.addWidget(label("LESS TEXT. MORE CLARITY.", "brandSub"))
        layout.addLayout(brand)
        layout.addStretch()
        self.nav = []
        for i, text in enumerate(["Workspace", "How it works", "Our project"]):
            b = button(text, lambda checked=False, index=i: self.navigate(index), "nav")
            b.setCheckable(True)
            self.nav.append(b)
            layout.addWidget(b)
        layout.addStretch()
        layout.addWidget(label("●  Offline & private", "offline"))
        outer.addWidget(header)

    def make_workspace(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(44, 5, 44, 0)
        v.setSpacing(10)
        eyebrow = label("A CLEARER WAY THROUGH YOUR WORDS", "eyebrow")
        self.workspace_eyebrow = eyebrow
        eyebrow.setAlignment(Qt.AlignCenter)
        v.addWidget(eyebrow)
        title = label("Less text. More clarity.", "hero")
        self.workspace_title = title
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)
        subtitle = label("Turn a paragraph into its opening two sentences. A simple idea, beautifully presented.", "subtitle")
        self.workspace_subtitle = subtitle
        subtitle.setAlignment(Qt.AlignCenter)
        v.addWidget(subtitle)
        v.addSpacing(6)
        panel = QFrame()
        self.workspace_panel = panel
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(22, 20, 22, 17)
        p.setSpacing(14)
        self.demo_btn = button("▶  Guided demo", self.demo_next, "quiet")
        p.addLayout(row(label("Make room for the essentials.", "section"), None,
                        label("EXTRACTIVE · FIRST 2 SENTENCES", "tag"), self.demo_btn))
        self.notice = label("", "notice", True)
        self.notice.hide()
        p.addWidget(self.notice)
        columns = QHBoxLayout()
        columns.setSpacing(16)
        for is_output in (False, True):
            pane = QFrame()
            pane.setObjectName("resultPane" if is_output else "pane")
            pane.setMinimumHeight(245)
            pv = QVBoxLayout(pane)
            pv.setContentsMargins(19, 16, 19, 14)
            pv.setSpacing(10)
            pv.addLayout(row(label("02" if is_output else "01", "number"),
                             label("Your summary" if is_output else "Your paragraph", "section"), None))
            pv.addWidget(label("The opening lines, with a little more breathing room." if is_output else "Paste your text. We’ll take it from here.", "muted", True))
            edit = QPlainTextEdit()
            edit.setMinimumHeight(115)
            edit.setFrameShape(QFrame.NoFrame)
            edit.setTabChangesFocus(True)
            edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            edit.document().setDocumentMargin(2)
            option = edit.document().defaultTextOption()
            option.setWrapMode(option.WrapMode.WrapAtWordBoundaryOrAnywhere)
            edit.document().setDefaultTextOption(option)
            if is_output:
                self.output = edit
                edit.setReadOnly(True)
                edit.setPlaceholderText("Your summary will appear here.\n\nTwo sentences. One clearer view.")
                edit.setAccessibleName("Generated summary")
                self.output_meta = label("Ready when you are", "muted")
                meta = self.output_meta
            else:
                self.input = edit
                edit.setPlaceholderText("Start with an article, study notes, or a paragraph…\n\nOr try our example below.")
                edit.setAccessibleName("Paragraph to summarize")
                self.input_meta = label("0 words · 0 sentences", "muted")
                meta = self.input_meta
            pv.addWidget(edit, 1)
            pv.addWidget(meta)
            columns.addWidget(pane, 1)
        p.addLayout(columns, 1)
        self.run_btn = button("Summarize  →", self.run_summary, "primary")
        self.run_btn.setToolTip("Keep the first two sentences · Ctrl+Enter")
        self.sample_btn = button("Try an example", self.load_sample, "quiet")
        self.open_btn = button("Open .txt", self.open_text, "quiet")
        self.clear_btn = button("Clear", self.clear, "quiet")
        self.copy_btn = button("Copy", self.copy_summary)
        self.save_btn = button("Save .txt", self.save_summary)
        p.addLayout(row(self.run_btn, self.sample_btn, self.open_btn, self.clear_btn, None, self.copy_btn, self.save_btn))
        stats = QHBoxLayout()
        stats.setContentsMargins(4, 0, 4, 0)
        stats.setSpacing(24)
        self.stat_values = []
        for initial, caption in [("—", "sentences kept"), ("—", "summary words"), ("—", "fewer words")]:
            box = QVBoxLayout()
            box.setSpacing(1)
            value = label(initial, "stat")
            self.stat_values.append(value)
            box.addWidget(value)
            box.addWidget(label(caption, "tiny"))
            stats.addLayout(box)
        stats.addStretch()
        note = label("A rule-based classroom project.\nSelects opening sentences; no trained AI model.", "muted", True)
        note.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        stats.addWidget(note)
        self.stat_container = QWidget()
        self.stat_container.setLayout(stats)
        p.addWidget(self.stat_container)
        panel.setMinimumHeight(560)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(panel)
        v.addWidget(scroll, 1)
        return page

    def make_process(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(44, 15, 44, 0)
        v.addWidget(label("FROM PARAGRAPH TO SUMMARY", "eyebrow"))
        v.addWidget(label("One simple process. Five clear steps.", "hero", True))
        v.addWidget(label("Walk through the same logic used in your original Python project.", "subtitle"))
        v.addSpacing(12)
        panel = QFrame()
        panel.setObjectName("panel")
        h = QHBoxLayout(panel)
        h.setContentsMargins(26, 26, 26, 26)
        h.setSpacing(30)
        left = QVBoxLayout()
        self.steps = []
        for i, (title, _, _) in enumerate(STEPS):
            b = button(f"0{i+1}    {title}", lambda checked=False, index=i: self.set_step(index), "step")
            b.setCheckable(True)
            b.setMinimumHeight(50)
            self.steps.append(b)
            left.addWidget(b)
        left.addStretch()
        left.addWidget(button("Try it in the workspace  →", lambda: self.navigate(0), "primary"))
        h.addLayout(left, 2)
        right = QVBoxLayout()
        right.setSpacing(18)
        self.step_number = label("", "number")
        self.step_title = label("", "section", True)
        self.step_body = label("", "body", True)
        self.step_code = label("", "code", True)
        self.step_code.setTextFormat(Qt.PlainText)
        self.step_code.setTextInteractionFlags(Qt.TextSelectableByMouse)
        for w in (self.step_number, self.step_title, self.step_body, self.step_code):
            right.addWidget(w)
        right.addStretch()
        right.addWidget(label("Know the limits", "section"))
        right.addWidget(label("The app does not rank importance or rewrite ideas. Abbreviations such as “Dr.” can be split as sentences. The result may miss key information later in the paragraph.", "body", True))
        h.addLayout(right, 3)
        panel.setMinimumHeight(520)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(panel)
        v.addWidget(scroll, 1)
        self.set_step(0)
        return page

    def make_project(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(44, 15, 44, 0)
        v.addWidget(label("BUILT TO MAKE LEARNING VISIBLE", "eyebrow"))
        v.addWidget(label("Small project. Thoughtful details.", "hero", True))
        v.addWidget(label("AI Text Summarizer  /  Computer Science and Engineering", "subtitle"))
        v.addSpacing(12)
        panel = QFrame()
        panel.setObjectName("panel")
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(24, 24, 24, 22)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        h = QHBoxLayout(content)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(30)
        image_col = QVBoxLayout()
        art = Artwork(ASSETS / "ai-brand.png", 18)
        art.setFixedSize(270, 270)
        image_col.addWidget(art)
        image_col.addWidget(label("Less text. More clarity.", "section"))
        image_col.addWidget(label("A fresh identity for our classroom project.", "muted", True))
        image_col.addStretch()
        h.addLayout(image_col, 2)
        details = QVBoxLayout()
        details.setSpacing(12)
        details.addWidget(label("The idea", "section"))
        details.addWidget(label("Make long paragraphs easier to preview through a simple offline desktop app. Python and a regular expression select the first two sentences, demonstrating string processing, validation and event-driven programming.", "body", True))
        details.addWidget(label("Our team", "section"))
        details.addWidget(label("Saumya  ·  25/SET/BCML/078\nAnant Kumar Dubey  ·  25/SET/BCML/094\nNishant Sah  ·  25/SET/BCML/098\nSuruchi Sah  ·  25/SET/BCML/099\nMoksh  ·  26/SET/BCML(L)/004", "body", True))
        details.addWidget(label("Manav Rachna International Institute of\nResearch and Studies", "muted", True))
        details.addWidget(label("What’s next", "section"))
        details.addWidget(label("Sentence ranking, more accurate sentence detection, adjustable summary length and model-based summarization.", "body", True))
        details.addStretch()
        h.addLayout(details, 3)
        scroll.setWidget(content)
        pv.addWidget(scroll, 1)
        pv.addLayout(row(button("Open project slides", lambda: self.open_material("AI_Text_Summarizer_PBL.pptx")),
                         button("Open project report", lambda: self.open_material("AI_Text_Summarizer_Report.docx")), None,
                         label("Python + PySide6 interface · Python re algorithm", "tiny")))
        v.addWidget(panel, 1)
        return page

    def fade(self, widget):
        # Keep animation ownership on the window; rapid navigation safely cancels it.
        for animation in self._animations:
            animation.stop()
            animation.deleteLater()
        self._animations.clear()
        if getattr(self, "_fade_widget", None) is not None:
            self._fade_widget.setGraphicsEffect(None)
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        self._fade_widget = widget
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(240)
        animation.setStartValue(.35)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animations.append(animation)
        animation.start()

    def navigate(self, index):
        if self.stack.currentIndex() == index:
            return
        self.stack.setCurrentIndex(index)
        for i, b in enumerate(self.nav):
            b.setChecked(i == index)
        self.fade(self.stack.currentWidget())

    def set_step(self, index):
        for i, b in enumerate(self.steps):
            b.setChecked(i == index)
        title, body, code = STEPS[index]
        self.step_number.setText(f"STEP 0{index+1} / 05")
        self.step_title.setText(title)
        self.step_body.setText(body)
        self.step_code.setText(code)

    def tell(self, message, error=False):
        self.notice.setProperty("error", error)
        self.notice.style().unpolish(self.notice)
        self.notice.style().polish(self.notice)
        self.notice.setText(message)
        self.notice.show()

    def input_changed(self):
        text = self.input.toPlainText()
        count = len(split_sentences(text))
        self.input_meta.setText(f"{word_count(text):,} words · {count:,} sentence{'s' if count != 1 else ''}")
        self._summary = ""
        self.output.clear()
        self.output_meta.setText("Ready when you are")
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        for stat in self.stat_values:
            stat.setText("—")
        self.notice.hide()
        self.demo_index = -1
        self.demo_btn.setText("▶  Guided demo")

    def run_summary(self):
        self.navigate(0)
        text = self.input.toPlainText().strip()
        if not text:
            self.tell("Please enter some text, or choose “Try an example”.", True)
            self.input.setFocus()
            return
        self._summary = summarize(text)
        self.output.setPlainText(self._summary)
        sentences = len(split_sentences(text))
        words = word_count(self._summary)
        kept = min(sentences, 2)
        self.output_meta.setText(f"{words:,} words · {kept} sentence{'s' if kept != 1 else ''}")
        reduction = round(100 * (1 - words / max(1, word_count(text))))
        for stat, value in zip(self.stat_values, [f"{kept} / {sentences}", f"{words:,}", f"{reduction}%"]):
            stat.setText(value)
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.tell("This text already has two sentences or fewer, so it stays unchanged." if sentences <= 2 else "Done. The opening two sentences are ready to use.")

    def load_sample(self):
        self.navigate(0)
        self.input.setPlainText(SAMPLE)
        self.tell("Example loaded: 6 sentences. Click Summarize to keep the first 2.")
        self.input.setFocus()

    def clear(self):
        self.navigate(0)
        self.input.clear()
        self.input_changed()
        self.input.setFocus()

    def copy_summary(self):
        if self._summary:
            QApplication.clipboard().setText(self._summary)
            self.tell("Copied. Your summary is ready to paste.")

    def open_text(self):
        self.navigate(0)
        path, _ = QFileDialog.getOpenFileName(self, "Open a paragraph", "", "Text files (*.txt)")
        if not path:
            return
        try:
            if Path(path).stat().st_size > 2_000_000:
                self.tell("Please choose a text file smaller than 2 MB for this classroom demo.", True)
                return
            text = Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            self.tell("This file could not be opened. Please choose a readable UTF-8 .txt file.", True)
            return
        self.input.setPlainText(text)
        self.tell("Text file opened. Click Summarize when you’re ready.")

    def save_summary(self):
        if not self._summary:
            return
        self.navigate(0)
        path, _ = QFileDialog.getSaveFileName(self, "Save your summary", "AI_Text_Summary.txt", "Text files (*.txt)")
        if not path:
            return
        if not Path(path).suffix:
            path += ".txt"
        try:
            Path(path).write_text(self._summary + "\n", encoding="utf-8")
        except OSError:
            self.tell("The summary could not be saved. Please choose another folder.", True)
            return
        self.tell("Saved. Your summary is now a text file.")

    def demo_next(self):
        if self.demo_index < 0:
            self.load_sample()
            self.demo_index = 0
            self.demo_btn.setText("Next: summarize  →")
            self.tell("DEMO 1 / 3 · Six sentences are loaded. Explain that the first two will be selected, then click “Next”.")
        elif self.demo_index == 0:
            self.run_summary()
            self.demo_index = 1
            self.demo_btn.setText("Next: explain it  →")
            self.tell("DEMO 2 / 3 · Compare the original with the two-sentence result. Copy or save it, then show how the rule works.")
        else:
            self.demo_index = -1
            self.demo_btn.setText("▶  Guided demo")
            self.navigate(1)
            self.set_step(2)
            self.tell("DEMO 3 / 3 · Demo complete. Open “How it works” to explain the regex and first-two-sentence rule.")

    def open_material(self, name):
        path = BASE / "project_materials" / name
        if not path.is_file() or not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            self.navigate(0)
            self.tell("Open the project_materials folder to view the report or slides in a compatible office application.", True)

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def leave_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "stat_container"):
            return
        compact = self.height() < 800
        self.workspace_eyebrow.setVisible(not compact)
        self.workspace_subtitle.setVisible(not compact)
        self.stat_container.setVisible(not compact)
        self.workspace_title.setStyleSheet("font-size: 32px;" if compact else "font-size: 42px;")
        self.workspace_panel.setMinimumHeight(500 if compact else 560)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AI Text Summarizer")
    app.setOrganizationName("Saumya · 078")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    window = SummarizerApp()
    screen = app.primaryScreen().availableGeometry()
    window.resize(min(1280, screen.width()), min(860, screen.height()))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
