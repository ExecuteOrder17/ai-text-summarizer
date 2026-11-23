"""Check the installed runtime and native Windows interface in CI.

Run with the installed runtime's python.exe and the install directory as
the first argument. This file is separate from the normal source checks.
"""
from pathlib import Path
import sys


def main():
    install_dir = Path(sys.argv[1]).resolve()
    # The private runtime's ._pth includes its parent, where app.py lives.
    import app as installed_app
    from summarizer import SAMPLE, summarize
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    assert Path(installed_app.__file__).resolve().parent == install_dir
    assert sys.platform == 'win32'
    assert (install_dir / 'AI_Text_Summarizer.exe').is_file()
    assert (install_dir / 'assets' / 'app.ico').is_file()
    assert (install_dir / 'project_materials' / 'AI_Text_Summarizer_Report.docx').is_file()

    qt = QApplication([])
    qt.setStyle('Fusion')
    window = installed_app.SummarizerApp()
    window.show()
    window.load_sample()
    window.run_summary()
    qt.processEvents()
    assert window.isVisible()
    assert not window.windowIcon().isNull()
    assert window.output.toPlainText() == summarize(SAMPLE)
    assert window.stat_values[0].text() == '2 / 6'
    QTimer.singleShot(400, qt.quit)
    result = qt.exec()
    print('Installed Windows runtime, native interface and sample summary passed.')
    return result


if __name__ == '__main__':
    sys.exit(main())
