Unicode true
Target amd64-unicode
!include "MUI2.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

Name "AI Text Summarizer"
Caption "AI Text Summarizer Setup"
OutFile "../../downloads/AI_Text_Summarizer_Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\AITextSummarizer"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompressorDictSize 32
ManifestDPIAware true
BrandingText "Less text. More clarity."
VIProductVersion "1.0.0.0"
VIAddVersionKey /LANG=1033 "ProductName" "AI Text Summarizer"
VIAddVersionKey /LANG=1033 "FileDescription" "AI Text Summarizer offline setup (64-bit Windows)"
VIAddVersionKey /LANG=1033 "FileVersion" "1.0.0"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Saumya and project team"

!define MUI_ICON "payload/assets/app.ico"
!define MUI_UNICON "payload/assets/app.ico"
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "AI Text Summarizer"
!define MUI_WELCOMEPAGE_TEXT "Less text. More clarity.$\r$\n$\r$\nThis setup installs the desktop app and creates a shortcut on your desktop.$\r$\n$\r$\nPython and all required interface components are included. No additional downloads or administrator account are needed.$\r$\n$\r$\nClose an earlier copy of the app before continuing."
!define MUI_FINISHPAGE_TITLE "Your app is ready."
!define MUI_FINISHPAGE_TEXT "AI Text Summarizer has been installed.$\r$\n$\r$\nOpen it anytime from the AI Text Summarizer shortcut on your desktop.$\r$\n$\r$\nTry Guided demo to present the project. Press F11 for presentation view."
!define MUI_FINISHPAGE_RUN "$INSTDIR\AI_Text_Summarizer.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Open AI Text Summarizer"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_OK|MB_ICONSTOP "This app needs 64-bit Windows 10 or Windows 11."
    Abort
  ${EndIf}
  ${IfNot} ${AtLeastWin10}
    MessageBox MB_OK|MB_ICONSTOP "This app needs Windows 10 or Windows 11."
    Abort
  ${EndIf}
  SetShellVarContext current
  SetRegView 64
  ; Keep the managed app folder fixed, including when /D is supplied.
  StrCpy $INSTDIR "$LOCALAPPDATA\Programs\AITextSummarizer"
FunctionEnd

Section "AI Text Summarizer" Main
  SetShellVarContext current
  SetRegView 64
  SetOutPath "$INSTDIR"
  SetOverwrite on
  ClearErrors
  File /r "payload/*.*"
  IfErrors failed
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  IfErrors failed

  ; CreateShortcut uses the current SetOutPath as its working directory.
  CreateShortcut "$DESKTOP\AI Text Summarizer.lnk" "$INSTDIR\AI_Text_Summarizer.exe" "" "$INSTDIR\assets\app.ico" 0 SW_SHOWNORMAL "" "AI Text Summarizer - Less text. More clarity."
  CreateDirectory "$SMPROGRAMS\AI Text Summarizer"
  CreateShortcut "$SMPROGRAMS\AI Text Summarizer\AI Text Summarizer.lnk" "$INSTDIR\AI_Text_Summarizer.exe" "" "$INSTDIR\assets\app.ico"
  CreateShortcut "$SMPROGRAMS\AI Text Summarizer\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "DisplayName" "AI Text Summarizer"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "DisplayVersion" "1.0.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "Publisher" "Saumya and project team"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "DisplayIcon" "$INSTDIR\assets\app.ico"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "QuietUninstallString" '$\"$INSTDIR\Uninstall.exe$\" /S'
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "NoRepair" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer" "EstimatedSize" 100000
  Goto done
  failed:
    MessageBox MB_OK|MB_ICONSTOP "Setup could not copy all app files. Close AI Text Summarizer if it is running, then run setup again."
    Abort
  done:
SectionEnd

Section "Uninstall"
  SetShellVarContext current
  SetRegView 64
  SetOutPath "$TEMP"
  Delete "$DESKTOP\AI Text Summarizer.lnk"
  Delete "$SMPROGRAMS\AI Text Summarizer\AI Text Summarizer.lnk"
  Delete "$SMPROGRAMS\AI Text Summarizer\Uninstall.lnk"
  RMDir "$SMPROGRAMS\AI Text Summarizer"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\SaumyaAITextSummarizer"
  RMDir /r "$INSTDIR\runtime"
  RMDir /r "$INSTDIR\assets"
  RMDir /r "$INSTDIR\project_materials"
  RMDir /r "$INSTDIR\licenses"
  RMDir /r "$INSTDIR\__pycache__"
  Delete "$INSTDIR\app.py"
  Delete "$INSTDIR\summarizer.py"
  Delete "$INSTDIR\launch.pyw"
  Delete "$INSTDIR\AI_Text_Summarizer.exe"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\THIRD_PARTY_NOTICES.txt"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
SectionEnd
