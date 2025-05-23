# PowerShell script to start the containerized Computer Use server

Write-Host "Starting Containerized Computer Use Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if container is already running
$containerStatus = docker ps --filter "name=windows-computer-use" --format "{{.Status}}" 2>$null

if ($containerStatus) {
    Write-Host "Container is already running: $containerStatus" -ForegroundColor Yellow
    $response = Read-Host "Do you want to restart it? (y/n)"
    if ($response -eq 'y') {
        Write-Host "Stopping existing container..." -ForegroundColor Yellow
        docker-compose down
    } else {
        Write-Host "Container is still running. Exiting." -ForegroundColor Green
        exit 0
    }
}

# Start the container
Write-Host "`nStarting container..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Container started successfully" -ForegroundColor Green
    
    # Wait for services to be ready
    Write-Host "`nWaiting for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check container logs
    Write-Host "`nContainer logs:" -ForegroundColor Yellow
    docker logs windows-computer-use --tail 20
    
    # Display connection information
    Write-Host "`n=========================================" -ForegroundColor Cyan
    Write-Host "Container is running!" -ForegroundColor Green
    Write-Host "`nVNC Access:" -ForegroundColor Yellow
    Write-Host "  Host: localhost:5900" -ForegroundColor White
    Write-Host "  Password: vnc123" -ForegroundColor White
    Write-Host "`nMCP WebSocket:" -ForegroundColor Yellow
    Write-Host "  Host: localhost:8080" -ForegroundColor White
    Write-Host "`nTo view logs:" -ForegroundColor Yellow
    Write-Host "  docker logs -f windows-computer-use" -ForegroundColor White
    Write-Host "`nTo stop:" -ForegroundColor Yellow
    Write-Host "  .\stop-container.ps1" -ForegroundColor White
    Write-Host "=========================================" -ForegroundColor Cyan
} else {
    Write-Host "✗ Failed to start container" -ForegroundColor Red
    Write-Host "Check docker-compose logs for details" -ForegroundColor Yellow
    exit 1
}
