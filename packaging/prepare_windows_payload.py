"""Prepare the local runtime consumed by the NSIS installer source.

Run from the repository with Python and pip available. Only the ignored
packaging/windows/payload directory is replaced. Downloads remain in a cache.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGING = ROOT / 'packaging'
CACHE = PACKAGING / 'download-cache'
PAYLOAD = PACKAGING / 'windows' / 'payload'
PYTHON_VERSION = '3.13.13'
QT_VERSION = '6.10.1'


def extract(archive, destination):
    """Extract only entries that stay beneath the chosen destination."""
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as source:
        for entry in source.infolist():
            target = (destination / entry.filename).resolve()
            if not target.is_relative_to(destination):
                raise ValueError(f'Unsafe archive entry: {entry.filename}')
        source.extractall(destination)


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    archive_name = f'python-{PYTHON_VERSION}-embed-amd64.zip'
    python_archive = CACHE / archive_name
    if not python_archive.exists():
        print('Downloading the official Windows Python runtime...')
        url = f'https://www.python.org/ftp/python/{PYTHON_VERSION}/{archive_name}'
        partial = python_archive.with_suffix('.partial')
        urllib.request.urlretrieve(url, partial)
        partial.replace(python_archive)

    subprocess.run([
        sys.executable, '-m', 'pip', 'download', '--only-binary=:all:',
        '--platform', 'win_amd64', '--python-version', '313',
        '--implementation', 'cp', '--abi', 'cp313', '--dest', str(CACHE),
        f'PySide6-Essentials=={QT_VERSION}', f'shiboken6=={QT_VERSION}',
    ], check=True)

    if PAYLOAD.exists():
        shutil.rmtree(PAYLOAD)
    runtime = PAYLOAD / 'runtime'
    runtime.mkdir(parents=True)
    extract(python_archive, runtime)
    packages = runtime / 'Lib' / 'site-packages'
    packages.mkdir(parents=True)
    wheels = list(CACHE.glob(f'pyside6_essentials-{QT_VERSION}-*-win_amd64.whl'))
    wheels += list(CACHE.glob(f'shiboken6-{QT_VERSION}-*-win_amd64.whl'))
    if len(wheels) != 2:
        raise RuntimeError('Expected exactly one Windows wheel for each Qt package.')
    for wheel in wheels:
        extract(wheel, packages)
    (runtime / 'python313._pth').write_text(
        'python313.zip\n.\nLib/site-packages\n..\nimport site\n', encoding='utf-8'
    )

    pyside = packages / 'PySide6'
    keep_dll = {'qt6core.dll', 'qt6gui.dll', 'qt6widgets.dll', 'pyside6.abi3.dll'}
    keep_pyd = {'qtcore.pyd', 'qtgui.pyd', 'qtwidgets.pyd'}
    for file in pyside.iterdir():
        if not file.is_file():
            continue
        name = file.name.lower()
        unused_dll = file.suffix.lower() == '.dll' and name.startswith(('qt6', 'pyside6')) and name not in keep_dll
        unused_pyd = file.suffix.lower() == '.pyd' and name not in keep_pyd
        if unused_dll or unused_pyd or file.suffix.lower() == '.exe':
            file.unlink()
    for name in ('qml', 'translations', 'resources', 'metatypes'):
        directory = pyside / name
        if directory.exists():
            shutil.rmtree(directory)
    plugins = pyside / 'plugins'
    for entry in plugins.iterdir():
        if entry.name != 'platforms':
            shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    for plugin in (plugins / 'platforms').iterdir():
        if plugin.name.lower() != 'qwindows.dll':
            plugin.unlink()

    for name in ('app.py', 'summarizer.py', 'THIRD_PARTY_NOTICES.txt'):
        shutil.copy2(ROOT / name, PAYLOAD / name)
    for name in ('assets', 'project_materials'):
        shutil.copytree(ROOT / name, PAYLOAD / name)
    shutil.copy2(PACKAGING / 'windows' / 'launch.pyw', PAYLOAD / 'launch.pyw')
    shutil.copytree(PACKAGING / 'licenses', PAYLOAD / 'licenses')
    (PAYLOAD / 'README.txt').write_text(
        'AI Text Summarizer\nLess text. More clarity.\n\n'
        'Open the app from its desktop shortcut. Use Guided demo for a presentation.\n'
        'F11 opens presentation view; Escape leaves it.\n'
        'Python and required interface components are included. The app works offline.\n'
        'The current summarizer selects the first two sentences using a fixed rule.\n'
        'See the repository README for full usage and source instructions.\n',
        encoding='utf-8',
    )
    print('Payload prepared:', PAYLOAD)
    print('Next: compile launcher.nsi, then installer.nsi with makensis.')


if __name__ == '__main__':
    main()
