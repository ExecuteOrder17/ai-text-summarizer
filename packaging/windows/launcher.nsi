Unicode true
Target amd64-unicode
Name "AI Text Summarizer"
OutFile "payload/AI_Text_Summarizer.exe"
RequestExecutionLevel user
SilentInstall silent
AutoCloseWindow true
Icon "payload/assets/app.ico"
ManifestDPIAware true
VIProductVersion "1.0.0.0"
VIAddVersionKey /LANG=1033 "ProductName" "AI Text Summarizer"
VIAddVersionKey /LANG=1033 "FileDescription" "AI Text Summarizer desktop launcher"
VIAddVersionKey /LANG=1033 "FileVersion" "1.0.0"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Saumya and project team"

Section
  IfFileExists "$EXEDIR\runtime\pythonw.exe" found missing
  found:
    SetOutPath "$EXEDIR"
    ClearErrors
    Exec '"$EXEDIR\runtime\pythonw.exe" "$EXEDIR\launch.pyw"'
    IfErrors missing
    Quit
  missing:
    MessageBox MB_OK|MB_ICONSTOP "AI Text Summarizer could not find its runtime. Please run AI_Text_Summarizer_Setup.exe again."
    SetErrorLevel 1
SectionEnd
