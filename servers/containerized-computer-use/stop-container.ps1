# PowerShell script to stop the containerized Computer Use server

Write-Host "Stopping Containerized Computer Use Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if container is running
$containerStatus = docker ps --filter "name=windows-computer-use" --format "{{.Status}}" 2>$null

if (-not $containerStatus) {
    Write-Host "Container is not running" -ForegroundColor Yellow
    exit 0
}

# Stop the container
Write-Host "`nStopping container..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Container stopped successfully" -ForegroundColor Green
    
    # Optional: Clean up volumes
    $response = Read-Host "`nDo you want to remove volumes (persistent data)? (y/n)"
    if ($response -eq 'y') {
        docker-compose down -v
        Write-Host "✓ Volumes removed" -ForegroundColor Green
    }
} else {
    Write-Host "✗ Failed to stop container" -ForegroundColor Red
    Write-Host "You may need to manually stop it with: docker stop windows-computer-use" -ForegroundColor Yellow
    exit 1
}
