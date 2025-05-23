# PowerShell script to set up the containerized Computer Use environment

Write-Host "Containerized Computer Use Setup Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Create shared directories
Write-Host "`nCreating shared directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path ".\shared" | Out-Null
New-Item -ItemType Directory -Force -Path ".\workspaces" | Out-Null
Write-Host "✓ Created shared and workspaces directories" -ForegroundColor Green

# Build the Docker image
Write-Host "`nBuilding Docker image..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Create VNC viewer batch file
$vncScript = @'
@echo off
echo Starting VNC viewer for containerized Computer Use...
echo.
echo VNC Connection Details:
echo   Host: localhost:5900
echo   Password: vnc123
echo.
echo You can use any VNC viewer such as:
echo   - TightVNC Viewer
echo   - RealVNC Viewer
echo   - UltraVNC
echo.
echo Or use the web-based noVNC interface (if configured)
echo.
pause
'@

$vncScript | Out-File -FilePath ".\connect-vnc.bat" -Encoding ASCII
Write-Host "✓ Created VNC connection script" -ForegroundColor Green

# Create MCP configuration for Claude Desktop
$mcpConfig = @{
    "containerized-computer-use" = @{
        "command" = "docker"
        "args" = @("exec", "-i", "windows-computer-use", "python3", "/app/container_mcp_wrapper.py")
        "keepAlive" = $true
        "stderrToConsole" = $true
    }
}

$configJson = $mcpConfig | ConvertTo-Json -Depth 3
Write-Host "`nMCP Configuration for Claude Desktop:" -ForegroundColor Yellow
Write-Host $configJson -ForegroundColor Cyan

# Save configuration to file
$configJson | Out-File -FilePath ".\claude_config_snippet.json" -Encoding UTF8
Write-Host "`n✓ Saved MCP configuration to claude_config_snippet.json" -ForegroundColor Green

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run .\start-container.ps1 to start the container" -ForegroundColor White
Write-Host "2. Add the configuration from claude_config_snippet.json to your Claude Desktop config" -ForegroundColor White
Write-Host "3. Connect to VNC using .\connect-vnc.bat" -ForegroundColor White
