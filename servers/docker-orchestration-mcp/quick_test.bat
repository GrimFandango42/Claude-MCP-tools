@echo off
echo Docker Orchestration MCP Server - Quick Test
echo ========================================
echo.

echo Step 1: Testing Docker connection...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker not available
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon not running
    pause
    exit /b 1
)
echo ✓ Docker is running

echo.
echo Step 2: Testing virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)
echo ✓ Virtual environment exists

echo.
echo Step 3: Testing Python dependencies...
.venv\Scripts\python.exe -c "import docker; print('✓ docker package available')"
if %errorlevel% neq 0 (
    echo ERROR: docker package not available
    pause
    exit /b 1
)

.venv\Scripts\python.exe -c "import mcp; print('✓ mcp package available')"
if %errorlevel% neq 0 (
    echo ERROR: mcp package not available
    pause
    exit /b 1
)

echo.
echo Step 4: Testing server import...
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src'); from server import DockerOrchestrationServer; print('✓ Server module imports successfully')"
if %errorlevel% neq 0 (
    echo ERROR: Server module import failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ All tests passed! Docker server is ready to launch.
echo.
echo To start the server:
echo   launch_fixed.bat
echo.
echo To test with Claude Desktop:
echo   1. Restart Claude Desktop
echo   2. Try using Docker tools
echo ========================================

pause
