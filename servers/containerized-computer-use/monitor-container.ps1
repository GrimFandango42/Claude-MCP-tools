# Real-time monitoring dashboard for containerized Computer Use server

Write-Host "Container Monitor - Windows Computer Use" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker version | Out-Null
} catch {
    Write-Host "`nError: Docker is not running or not installed!" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is running." -ForegroundColor Yellow
    exit 1
}

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "`nError: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Display monitoring options
Write-Host "`nMonitoring Options:" -ForegroundColor Yellow
Write-Host "1. Real-time Dashboard (Python)" -ForegroundColor Gray
Write-Host "2. Docker Stats (Native)" -ForegroundColor Gray
Write-Host "3. Container Logs (Follow mode)" -ForegroundColor Gray
Write-Host "4. Process List" -ForegroundColor Gray

$choice = Read-Host "`nSelect monitoring mode (1-4)"

$containerName = "windows-computer-use"

switch ($choice) {
    "1" {
        Write-Host "`nStarting real-time dashboard..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
        python monitor_container.py
    }
    "2" {
        Write-Host "`nStarting Docker stats..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
        docker stats $containerName
    }
    "3" {
        Write-Host "`nFollowing container logs..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to exit" -ForegroundColor Gray
        docker logs -f $containerName
    }
    "4" {
        Write-Host "`nContainer process list:" -ForegroundColor Green
        docker top $containerName
        
        Write-Host "`nPress any key to refresh, or 'q' to quit" -ForegroundColor Gray
        while ($true) {
            $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            if ($key.Character -eq 'q') { break }
            Clear-Host
            Write-Host "Container process list:" -ForegroundColor Green
            docker top $containerName
            Write-Host "`nPress any key to refresh, or 'q' to quit" -ForegroundColor Gray
        }
    }
    default {
        Write-Host "`nInvalid choice. Exiting." -ForegroundColor Red
    }
}
