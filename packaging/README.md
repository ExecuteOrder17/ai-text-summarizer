# Windows packaging

Most users should download the ready-made installer from the main README. The files here are for someone who wants to rebuild that installer.

## Two different build options

| Option | Result | What to run |
| --- | --- | --- |
| PyInstaller application build | An app folder containing an executable and its support files. | `Build_Windows_EXE.bat` in the repository root. |
| NSIS installer build | One setup `.exe` that installs the app and creates shortcuts. | The preparation and compilation commands below. |

The installer includes a private copy of Python and the Qt components needed by this application. It does not depend on a system Python installation.

## Rebuild the setup installer

You need Python 3.10 or newer with pip, an internet connection for downloads, and NSIS 3.11 with its 64-bit Unicode stubs. Install NSIS from its official distribution or your operating system's package manager, and make `makensis` available on PATH.

From the repository root, run:

```sh
python packaging/prepare_windows_payload.py
makensis packaging/windows/launcher.nsi
makensis packaging/windows/installer.nsi
```

The output is:

```text
downloads/AI_Text_Summarizer_Setup.exe
```

The installer source uses relative paths. NSIS changes to the script directory while compiling, so keep the `packaging/windows` layout as supplied. The `payload` directory and download cache are ignored by Git because they contain generated runtime files.

The NSIS route can be compiled with a compatible NSIS compiler on Linux or Windows. The separate PyInstaller route should be built on the operating system that will run its executable.

## What the preparation script does

1. Downloads the official Windows x64 embeddable Python 3.13.13 archive.
2. Uses pip to download the Windows PySide6-Essentials and shiboken6 6.10.1 wheels.
3. Extracts the runtime and packages into the ignored payload directory.
4. Includes the app code, assets, current report, slides, and license notices.
5. Removes unused Qt modules and tools, keeping the widgets and Windows platform plugin used by this app.
6. Writes the private runtime's search paths so that it can find the app and its packages.

`launcher.nsi` creates the small installed launcher. `installer.nsi` includes that launcher and the payload in one setup file. The installer creates desktop and Start menu shortcuts and registers an uninstaller for the current Windows user.

## Before distributing a new build

Run the project's tests, check the included project material, and try the installed app on a Windows computer. Rebuilding an installer does not itself prove that the app launches on every supported machine. Retain dependency license notices with the packaged runtime.

The current build was compiled and its package contents verified on Linux. A full installation and launch on a real Windows computer was not verified in that build environment.
