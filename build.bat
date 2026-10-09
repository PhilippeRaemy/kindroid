@echo off
REM Build script for Kindroid CLI Windows executable
REM Usage: build.bat [--no-console]

echo Building Kindroid CLI executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Determine build flags based on arguments
set PYINSTALLER_FLAGS=--onefile --name kindroid

if "%1"=="--no-console" (
    set PYINSTALLER_FLAGS=%PYINSTALLER_FLAGS% --windowed
    echo Building with hidden console window...
) else (
    echo Building with visible console window...
)

echo.
echo Running PyInstaller...
echo.

REM Run PyInstaller
pyinstaller %PYINSTALLER_FLAGS% kindroid_cli.py

echo.
if errorlevel 0 (
    echo.
    echo ========================================
    echo Build successful!
    echo ========================================
    echo.
    echo Executable location:
    echo   dist\kindroid.exe
    echo.
    echo Usage:
    echo   dist\kindroid.exe --help
    echo   dist\kindroid.exe send --chat-id abc123 "Hello"
    echo   dist\kindroid.exe get --chat-id abc123 --limit 50
    echo   dist\kindroid.exe chat --chat-id abc123
    echo.
    echo Environment variables needed:
    echo   set KINDROID_API_KEY=kn_your_api_key
    echo   set CHAT_ID=your_chat_id (optional)
    echo.
    echo You can clean up build artifacts:
    echo   rmdir /s build
    echo   del kindroid.spec
    echo.
) else (
    echo.
    echo Build failed! Check the errors above.
    echo.
)

pause

