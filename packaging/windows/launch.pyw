"""Windowless entry point with a readable startup error if loading fails."""
from pathlib import Path
import ctypes
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

try:
    from app import main
    main()
except Exception:
    message = traceback.format_exc()
    log_path = Path(os.environ.get("LOCALAPPDATA", str(ROOT))) / "AITextSummarizer" / "logs" / "startup.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(message, encoding="utf-8")
        detail = f"The app could not start. Details were saved to:\n\n{log_path}\n\nTry reinstalling AI Text Summarizer."
    except OSError:
        detail = "The app could not start. Please try reinstalling AI Text Summarizer.\n\n" + message[-1200:]
    ctypes.windll.user32.MessageBoxW(None, detail, "AI Text Summarizer", 0x10)
    sys.exit(1)
