@echo off
chcp 65001 >nul
cd /d "X:\Drive'ım\Projeler\Video-indirme"
echo Python paketleri kuruluyor...
"araçlar\python\python.exe" -m pip install pyperclip pystray pillow winotify
echo.
echo Kurulum tamamlandi!
pause
