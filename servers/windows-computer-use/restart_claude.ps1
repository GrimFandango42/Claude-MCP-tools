# Windows Computer Use MCP Server - Restart and Test Script
# This script will stop Claude Desktop, test the server, and restart Claude

Write-Host "Windows Computer Use MCP Server - Restart Script" -ForegroundColor Green
Write-Host "=" -repeat 50 -ForegroundColor Green

# Stop Claude Desktop if running
Write-Host "`nStopping Claude Desktop..." -ForegroundColor Yellow
try {
    Get-Process "Claude Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "Claude Desktop stopped" -ForegroundColor Green
}
catch {
    Write-Host "Claude Desktop not running or already stopped" -ForegroundColor Yellow
}

# Navigate to server directory
$serverPath = "C:\AI_Projects\Claude-MCP-tools\servers\windows-computer-use"
Set-Location $serverPath

# Test the server
Write-Host "`nTesting Windows Computer Use MCP Server..." -ForegroundColor Yellow
try {
    & "$serverPath\.venv\Scripts\python.exe" "$serverPath\test_server.py"
    Write-Host "Server test completed" -ForegroundColor Green
}
catch {
    Write-Host "Server test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait a moment
Start-Sleep -Seconds 2

# Restart Claude Desktop
Write-Host "`nRestarting Claude Desktop..." -ForegroundColor Yellow
try {
    Start-Process "C:\Users\Nithin\AppData\Local\Programs\Claude\Claude Desktop.exe"
    Write-Host "Claude Desktop started" -ForegroundColor Green
}
catch {
    Write-Host "Failed to start Claude Desktop: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nRestart script completed!" -ForegroundColor Green
Write-Host "Check the Claude Desktop interface to see if the Windows Computer Use server is working properly." -ForegroundColor Yellow

# Keep window open
Read-Host "`nPress Enter to exit"
