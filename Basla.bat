@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PATH=%cd%\araçlar;%PATH%"
start "" "araçlar\python\pythonw.exe" "app\main.py"
