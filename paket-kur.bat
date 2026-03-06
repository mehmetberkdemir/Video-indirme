@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Python paketleri kuruluyor...
"araçlar\python\python.exe" -m pip install pyperclip pystray pillow winotify
echo.
echo Kurulum tamamlandi!
pause
