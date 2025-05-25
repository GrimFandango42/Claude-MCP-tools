@echo off
echo ===== Pushing Claude MCP Tools to GitHub =====

:: Navigate to the project directory
cd /d "C:\AI_Projects\Claude MCP tools"

:: Check if Git is installed
git --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git is not installed or not in the PATH. Please install Git and try again.
    exit /b 1
)

:: Check if the directory is already a Git repository
if exist ".git" (
    echo This directory is already a Git repository.
) else (
    echo Initializing Git repository...
    git init
    if %ERRORLEVEL% neq 0 (
        echo Failed to initialize Git repository.
        exit /b 1
    )
)

:: Create .gitignore file
echo Creating .gitignore file...
echo # Python > .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *$py.class >> .gitignore
echo .env >> .gitignore
echo .venv >> .gitignore
echo env/ >> .gitignore
echo venv/ >> .gitignore
echo ENV/ >> .gitignore
echo *.log >> .gitignore
echo # VS Code >> .gitignore
echo .vscode/ >> .gitignore
echo # Screenshots >> .gitignore
echo screenshots/ >> .gitignore

:: Add all files to Git
echo Adding files to Git...
git add .
if %ERRORLEVEL% neq 0 (
    echo Failed to add files to Git.
    exit /b 1
)

:: Commit changes
echo Committing changes...
git commit -m "Initial commit of Claude MCP tools"
if %ERRORLEVEL% neq 0 (
    echo Failed to commit changes.
    exit /b 1
)

:: Instructions for creating a GitHub repository
echo.
echo ===== NEXT STEPS =====
echo 1. Go to https://github.com/new to create a new repository
echo 2. Name it "claude-mcp-tools" (or your preferred name)
echo 3. Do NOT initialize with README, .gitignore, or license
echo 4. Click "Create repository"
echo 5. Copy the repository URL (e.g., https://github.com/username/claude-mcp-tools.git)
echo.
set /p REPO_URL="Enter the GitHub repository URL: "

:: Add remote repository
echo Adding remote repository...
git remote add origin %REPO_URL%
if %ERRORLEVEL% neq 0 (
    echo Failed to add remote repository.
    exit /b 1
)

:: Push to GitHub
echo Pushing to GitHub...
git push -u origin master
if %ERRORLEVEL% neq 0 (
    echo Failed to push to GitHub. Trying main branch instead...
    git push -u origin main
    if %ERRORLEVEL% neq 0 (
        echo Failed to push to GitHub.
        echo You may need to manually push using: git push -u origin main
        exit /b 1
    )
)

echo.
echo ===== SUCCESS =====
echo Your Claude MCP tools project has been successfully pushed to GitHub!
echo Repository URL: %REPO_URL%
echo.

pause
