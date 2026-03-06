@echo off
REM Claude Code Launcher for MultiCMS Project

echo ========================================
echo Claude Code - MultiCMS Project
echo ========================================
echo.

REM Proje dizinine git
cd /d "%~dp0"

REM Mevcut dizini göster
echo Proje dizini: %CD%
echo.

REM Claude Code'u başlat
echo Claude Code baslatiliyor...
claude

REM Hata kontrolü
if %errorlevel% neq 0 (
    echo.
    echo HATA: Claude komutu bulunamadi!
    echo.
    echo Lutfen Claude Code'un PATH'e eklendiginden emin olun.
    echo Veya VS Code'u acip "Ctrl + Shift + P" ile Claude'u baslatin.
    pause
    exit /b 1
)