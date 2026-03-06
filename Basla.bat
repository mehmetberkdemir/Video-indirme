@echo off
chcp 65001 >nul
cd /d "X:\Drive'ım\Projeler\Video-indirme"
set "PATH=%cd%\araçlar;%PATH%"
start "" "araçlar\python\pythonw.exe" "izleyici.pyw"
