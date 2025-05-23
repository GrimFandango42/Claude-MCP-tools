# Test runner for containerized Computer Use MCP Server
# This script runs comprehensive tests against the running container

Write-Host "Containerized Computer Use Test Runner" -ForegroundColor Cyan
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

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "`nError: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Install test dependencies if needed
Write-Host "`nChecking test dependencies..." -ForegroundColor Yellow
$pipList = pip list 2>$null | Out-String

if (-not ($pipList -like "*pillow*")) {
    Write-Host "Installing test dependencies..." -ForegroundColor Yellow
    pip install pillow --quiet
}

# Run the test suite
Write-Host "`nRunning test suite..." -ForegroundColor Yellow
Write-Host ""

python test_container.py

$exitCode = $LASTEXITCODE

# Display results
if ($exitCode -eq 0) {
    Write-Host "`nAll tests passed! ✓" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed! ✗" -ForegroundColor Red
}

# Check for test results file
if (Test-Path "test_results.json") {
    Write-Host "`nTest results saved to: test_results.json" -ForegroundColor Cyan
    
    # Offer to view results
    $viewResults = Read-Host "`nWould you like to view detailed results? (y/n)"
    if ($viewResults -eq 'y') {
        Get-Content test_results.json | ConvertFrom-Json | Format-List
    }
}

# Container logs option
Write-Host "`nContainer Logs:" -ForegroundColor Yellow
Write-Host "To view container logs: docker logs $containerName" -ForegroundColor Gray
Write-Host "To view live logs: docker logs -f $containerName" -ForegroundColor Gray

# VNC connection reminder
Write-Host "`nVNC Access:" -ForegroundColor Yellow
Write-Host "VNC Viewer URL: localhost:5900" -ForegroundColor Gray
Write-Host "Password: vnc123" -ForegroundColor Gray

exit $exitCode
