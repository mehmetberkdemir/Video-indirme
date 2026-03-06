@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   YouTube Video Indirme - Kurulum
echo ============================================
echo.

if not exist "araçlar" mkdir araçlar
if not exist "videolar" mkdir videolar

echo [1/4] yt-dlp indiriliyor...
if not exist "araçlar\yt-dlp.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe' -OutFile 'araçlar\yt-dlp.exe'"
    echo       OK
) else (
    echo       Zaten mevcut, atlaniyor.
)

echo [2/4] deno indiriliyor...
if not exist "araçlar\deno.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip' -OutFile 'araçlar\deno.zip'"
    powershell -Command "Expand-Archive -Path 'araçlar\deno.zip' -DestinationPath 'araçlar' -Force"
    del "araçlar\deno.zip" 2>nul
    echo       OK
) else (
    echo       Zaten mevcut, atlaniyor.
)

echo [3/4] ffmpeg indiriliyor...
if not exist "araçlar\ffmpeg.exe" (
    echo       ffmpeg-release-essentials.zip indiriliyor (buyuk dosya, bekleyin)...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'araçlar\ffmpeg.zip'"
    echo       Zip aciliyor...
    powershell -Command "$zip = 'araçlar\ffmpeg.zip'; $tmp = 'araçlar\ffmpeg-tmp'; Expand-Archive -Path $zip -DestinationPath $tmp -Force; Get-ChildItem -Path $tmp -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1 | Copy-Item -Destination 'araçlar\ffmpeg.exe'; Remove-Item -Path $tmp -Recurse -Force; Remove-Item -Path $zip -Force"
    echo       OK
) else (
    echo       Zaten mevcut, atlaniyor.
)

echo [4/4] Python (portable) indiriliyor...
if not exist "araçlar\python\python.exe" (
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.9/python-3.12.9-embed-amd64.zip' -OutFile 'araçlar\python.zip'"
    powershell -Command "Expand-Archive -Path 'araçlar\python.zip' -DestinationPath 'araçlar\python' -Force"
    del "araçlar\python.zip" 2>nul
    REM pip icin import site satirini ac
    powershell -Command "(Get-Content 'araçlar\python\python312._pth') -replace '#import site','import site' | Set-Content 'araçlar\python\python312._pth'"
    echo       pip kuruluyor...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'araçlar\python\get-pip.py'"
    "araçlar\python\python.exe" "araçlar\python\get-pip.py" >nul 2>&1
    echo       Python paketleri kuruluyor...
    "araçlar\python\python.exe" -m pip install pyperclip pystray pillow winotify >nul 2>&1
    echo       OK
) else (
    echo       Zaten mevcut, atlaniyor.
)

echo.
echo ============================================
echo   Kurulum tamamlandi!
echo ============================================
echo.
echo   Basla.bat  = Clipboard izleyici (tray)
echo   indir.bat  = Manuel indirme
echo.
pause
