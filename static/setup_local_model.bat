@echo off
title DocuLens Local AI Model Setup
color 0A
echo ======================================================================
echo    DocuLens Enterprise AI: 1-Click Local Model Auto-Setup
echo ======================================================================
echo.
echo [*] Checking for Ollama installation on your system...

where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if exist "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
    ) else if exist "C:\Program Files\Ollama\ollama.exe" (
        set "OLLAMA_EXE=C:\Program Files\Ollama\ollama.exe"
    ) else (
        echo [!] Ollama is not installed yet.
        echo [*] Opening official free Ollama download page...
        start https://ollama.com/download/OllamaSetup.exe
        echo.
        echo Please finish the installer, then double-click this file again!
        echo ======================================================================
        pause
        exit /b 0
    )
) else (
    set "OLLAMA_EXE=ollama"
)

echo [*] Ollama binary confirmed!
echo [*] Configuring browser permissions (OLLAMA_ORIGINS=*)...
set OLLAMA_ORIGINS=*

echo [*] Ensuring model 'qwen2.5:1.5b' is downloaded to your laptop...
"%OLLAMA_EXE%" pull qwen2.5:1.5b

echo.
echo ======================================================================
echo [SUCCESS] Qwen 2.5 (1.5B) is ready on your laptop!
echo Starting local Ollama service with browser permissions...
echo.
echo === KEEP THIS WINDOW OPEN WHILE USING DOCULENS WEB STUDIO ===
echo ======================================================================
echo.
"%OLLAMA_EXE%" serve
pause
