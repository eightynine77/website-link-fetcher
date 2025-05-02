@echo off
:home
cls
echo choose which mode you want to use
echo.
echo.
echo [1] fetch links from one wep page
echo [2] fetch links from multiple web pages
echo.
choice /c 12 /n /m ">"
if %errorlevel% == 1 start cmd /c py website-link-fetcher.py
if %errorlevel% == 2 start cmd /c py multiple-website-link-fetcher.py
goto home