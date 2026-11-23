"""Run on the target operating system to build a standalone app."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
command = [
    sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
    "--windowed", "--onedir", "--name", "AI_Text_Summarizer",
    "--icon", str(ROOT / "assets" / "app.ico"),
    "--add-data", f"{ROOT / 'assets'}:assets",
    "--add-data", f"{ROOT / 'project_materials'}:project_materials",
    str(ROOT / "app.py"),
]
subprocess.run(command, cwd=ROOT, check=True)
print("Built app:", ROOT / "dist" / "AI_Text_Summarizer")
