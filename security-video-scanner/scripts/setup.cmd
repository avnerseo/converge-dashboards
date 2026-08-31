@echo off
rem Windows refuses to run .ps1 files by default (the "running scripts is
rem disabled on this system" error). Rather than ask an operator to loosen a
rem machine-wide security setting before they can try the product, this
rem wrapper runs our own script - and only ours - with that check bypassed.
rem Double-click it, or call it from any shell.
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
set "CODE=%ERRORLEVEL%"
rem Keep the window open when it was double-clicked, so the output is readable.
echo %cmdcmdline% | find /i " /c " >nul && pause
exit /b %CODE%
