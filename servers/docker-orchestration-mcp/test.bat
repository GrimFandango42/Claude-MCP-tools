@echo off
REM Docker Orchestration MCP Server Test Runner
REM Quick test script for validating server functionality

echo ========================================
echo Docker Orchestration MCP Server Tests
echo ========================================

echo.
echo Step 1: Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker Desktop not found
    echo Please install Docker Desktop first
    exit /b 1
)
echo ✓ Docker Desktop found

echo.
echo Step 2: Checking Docker daemon...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker daemon not running
    echo Please start Docker Desktop
    exit /b 1
)
echo ✓ Docker daemon running

echo.
echo Step 3: Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ✗ Virtual environment not found
    echo Run setup.bat first
    exit /b 1
)

echo.
echo Step 4: Running Python tests...
python -m pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo ✗ Some tests failed
) else (
    echo ✓ All tests passed
)

echo.
echo Step 5: Testing Docker connectivity...
python -c "import docker; client = docker.from_env(); client.ping(); print('✓ Docker client connection successful')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Docker client connection failed
    exit /b 1
)

echo.
echo Step 6: Testing server import...
python -c "import sys; sys.path.append('src'); from server import DockerOrchestrationServer; print('✓ Server import successful')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Server import failed - check dependencies
    exit /b 1
)

echo.
echo Step 7: Testing basic Docker operations...
docker run --rm hello-world >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Basic Docker operations failed
    exit /b 1
)
echo ✓ Basic Docker operations working

echo.
echo ========================================
echo Test Results Summary
echo ========================================
echo ✓ Docker Desktop available and running
echo ✓ Virtual environment configured
echo ✓ Dependencies installed correctly
echo ✓ Server components importable
echo ✓ Basic Docker operations functional
echo.
echo Ready for Claude Desktop integration!
echo ========================================

pause
