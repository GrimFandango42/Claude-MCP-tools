@echo off
REM Docker Orchestration MCP Server Setup Script
REM Automated setup for development environment

echo ========================================
echo Docker Orchestration MCP Server Setup
echo ========================================

echo.
echo Step 1: Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not installed or not in PATH
    echo Please install Docker Desktop and ensure it's running
    exit /b 1
)
echo ✓ Docker Desktop found

echo.
echo Step 2: Checking Docker daemon...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running
    echo Please start Docker Desktop
    exit /b 1
)
echo ✓ Docker daemon is running

echo.
echo Step 3: Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists
) else (
    python -m venv .venv
    echo ✓ Virtual environment created
)

echo.
echo Step 4: Activating virtual environment...
call .venv\Scripts\activate.bat
echo ✓ Virtual environment activated

echo.
echo Step 5: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 6: Installing dependencies...
pip install -r requirements.txt
echo ✓ Dependencies installed

echo.
echo Step 7: Installing package in development mode...
pip install -e .
echo ✓ Package installed in development mode

echo.
echo Step 8: Running basic tests...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed, but setup is complete
) else (
    echo ✓ All tests passed
)

echo.
echo Step 9: Testing Docker connection...
python -c "import docker; client = docker.from_env(); print('✓ Docker client connection successful')"
if %errorlevel% neq 0 (
    echo ERROR: Failed to connect to Docker
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the MCP server:
echo   python src\server.py
echo.
echo To run tests:
echo   python -m pytest tests/ -v
echo.
echo To add to Claude Desktop, add this configuration:
echo.
echo "docker-orchestration": {
echo   "command": "python",
echo   "args": ["%cd%\src\server.py"],
echo   "cwd": "%cd%",
echo   "keepAlive": true,
echo   "stderrToConsole": true
echo }
echo.
echo Remember to restart Claude Desktop after adding the configuration!
echo ========================================

pause
