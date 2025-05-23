# Interactive demo runner for containerized Computer Use MCP Server

Write-Host "Containerized Computer Use Demo Runner" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if container is running
$containerName = "windows-computer-use"
$containerStatus = docker ps --filter "name=$containerName" --format "{{.Status}}" 2>$null

if (-not $containerStatus) {
    Write-Host "`nError: Container '$containerName' is not running!" -ForegroundColor Red
    Write-Host "Please start the container first with: .\start-container.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nContainer Status: $containerStatus" -ForegroundColor Green

# VNC reminder
Write-Host "`n" -ForegroundColor Yellow
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║                    IMPORTANT NOTICE                       ║" -ForegroundColor Yellow
Write-Host "║                                                           ║" -ForegroundColor Yellow
Write-Host "║  To see visual demonstrations, connect with VNC Viewer:   ║" -ForegroundColor Yellow
Write-Host "║                                                           ║" -ForegroundColor Yellow
Write-Host "║  VNC URL: localhost:5900                                  ║" -ForegroundColor Yellow
Write-Host "║  Password: vnc123                                         ║" -ForegroundColor Yellow
Write-Host "║                                                           ║" -ForegroundColor Yellow
Write-Host "║  Download VNC Viewer from:                                ║" -ForegroundColor Yellow
Write-Host "║  https://www.realvnc.com/en/connect/download/viewer/     ║" -ForegroundColor Yellow
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to continue
$continue = Read-Host "Have you connected with VNC Viewer? (y/n)"
if ($continue -ne 'y') {
    Write-Host "`nPlease connect with VNC Viewer first to see the visual demos." -ForegroundColor Yellow
    exit 0
}

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "`nError: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Run the demo
Write-Host "`nStarting interactive demo..." -ForegroundColor Green
Write-Host "This will demonstrate various capabilities of the containerized server." -ForegroundColor Gray
Write-Host ""

python demo_container.py

# Check for screenshots
Write-Host "`n" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Green

$screenshots = Get-ChildItem -Path . -Filter "screenshot_*.png" -ErrorAction SilentlyContinue
if ($screenshots) {
    Write-Host "`nScreenshots captured:" -ForegroundColor Yellow
    foreach ($screenshot in $screenshots) {
        Write-Host "  - $($screenshot.Name)" -ForegroundColor Gray
    }
}

# Workspace files
Write-Host "`nTo access workspace files from the container:" -ForegroundColor Yellow
Write-Host "  docker exec -it $containerName ls -la /workspace/" -ForegroundColor Gray
Write-Host "  docker cp ${containerName}:/workspace/. ./container_output/" -ForegroundColor Gray

# Logs
Write-Host "`nTo view container logs:" -ForegroundColor Yellow
Write-Host "  docker logs $containerName" -ForegroundColor Gray

Write-Host "`nDemo completed successfully!" -ForegroundColor Green
