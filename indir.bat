@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PATH=%cd%\araçlar;%PATH%"

if "%~1"=="" (
    set /p "URL=YouTube linkini yapistir: "
) else (
    set "URL=%~1"
)

echo Indiriliyor: %URL%
"araçlar\yt-dlp.exe" -f "bv*[height<=1080]+ba/b" ^
    --merge-output-format mp4 ^
    --ffmpeg-location "araçlar" ^
    -o "videolar\%%(title)s.%%(ext)s" ^
    "%URL%"

if %errorlevel%==0 (
    echo.
    echo Basariyla indirildi!
) else (
    echo.
    echo Hata olustu!
)
pause
