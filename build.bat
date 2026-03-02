@echo off
echo === Working Hours Tracker - Build Script ===
echo.

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller
echo.

echo Building .exe...
pyinstaller --onefile --windowed --name "WorkingHoursTracker" main.py
echo.

if exist "dist\WorkingHoursTracker.exe" (
    echo ✓ Build successful!
    echo   Output: dist\WorkingHoursTracker.exe
) else (
    echo ✗ Build failed. Check errors above.
)
echo.
pause
