# Build script for Kindroid CLI Windows executable
# Usage: .\build.ps1 [-NoConsole]

param(
    [switch]$NoConsole
)

Write-Host "Building Kindroid CLI executable..." -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" 2>$null
}
catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Determine build flags
$flags = @("--onefile", "--name", "kindroid", "kindroid_cli.py")

if ($NoConsole) {
    $flags += "--windowed"
    Write-Host "Building with hidden console window..." -ForegroundColor Green
}
else {
    Write-Host "Building with visible console window..." -ForegroundColor Green
}

Write-Host ""
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
Write-Host ""

# Run PyInstaller
& pyinstaller @flags

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  dist\kindroid.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  dist\kindroid.exe --help" -ForegroundColor White
    Write-Host "  dist\kindroid.exe send --chat-id abc123 'Hello'" -ForegroundColor White
    Write-Host "  dist\kindroid.exe get --chat-id abc123 --limit 50" -ForegroundColor White
    Write-Host "  dist\kindroid.exe chat --chat-id abc123" -ForegroundColor White
    Write-Host ""
    Write-Host "Environment variables needed:" -ForegroundColor Cyan
    Write-Host "  `$env:KINDROID_API_KEY = 'kn_your_api_key'" -ForegroundColor White
    Write-Host "  `$env:CHAT_ID = 'your_chat_id' (optional)" -ForegroundColor White
    Write-Host ""
    Write-Host "Cleanup (optional):" -ForegroundColor Cyan
    Write-Host "  Remove-Item -Recurse build" -ForegroundColor White
    Write-Host "  Remove-Item kindroid.spec" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "Build failed! Check the errors above." -ForegroundColor Red
    Write-Host ""
    exit 1
}

