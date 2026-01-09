@echo off
echo Killing any existing bot instances...
taskkill /f /im python.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo.
echo Starting DarkReaver Bot...
echo.
cd /d "C:\Users\Dell\Desktop\bot"
python bot.py
pause