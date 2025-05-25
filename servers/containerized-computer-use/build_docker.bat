@echo off
echo Building Containerized Computer Use Docker Image...
echo ================================================

cd /d "%~dp0"

REM Check if Docker is running
docker ps > nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo.
echo Building Docker image...
docker-compose build --no-cache

if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo.
echo To start the container manually:
echo   docker-compose up -d
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To connect via VNC:
echo   VNC URL: vnc://localhost:5900
echo   Password: vnc123

pause
