@echo off
setlocal enabledelayedexpansion

:: Git Operations Script for Claude MCP Tools
:: This script provides a command-line interface for Git operations

:: Set the project directory
set PROJECT_DIR=C:\AI_Projects\Claude MCP tools

:: Parse command line arguments
set COMMAND=%1
shift

:: Navigate to the project directory
cd /d "%PROJECT_DIR%"

:: Check if Git is installed
git --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git is not installed or not in the PATH. Please install Git and try again.
    exit /b 1
)

:: Execute the appropriate command
if "%COMMAND%"=="status" (
    echo Checking Git status...
    git status
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="init" (
    echo Initializing Git repository...
    if exist ".git" (
        echo This directory is already a Git repository.
    ) else (
        git init
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="create-gitignore" (
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
    echo .gitignore file created successfully.
    exit /b 0
)

if "%COMMAND%"=="add" (
    echo Adding files to Git...
    if "%~1"=="" (
        git add .
    ) else (
        git add %*
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="commit" (
    echo Committing changes...
    git commit -m "%*"
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="remote-add" (
    echo Adding remote repository...
    set REMOTE_NAME=%~1
    set REMOTE_URL=%~2
    if "%REMOTE_NAME%"=="" (
        echo Remote name is required.
        exit /b 1
    )
    if "%REMOTE_URL%"=="" (
        echo Remote URL is required.
        exit /b 1
    )
    git remote add %REMOTE_NAME% %REMOTE_URL%
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="push" (
    echo Pushing to remote repository...
    set REMOTE=%~1
    set BRANCH=%~2
    if "%REMOTE%"=="" set REMOTE=origin
    if "%BRANCH%"=="" (
        git push -u %REMOTE% main || git push -u %REMOTE% master
    ) else (
        git push -u %REMOTE% %BRANCH%
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="pull" (
    echo Pulling from remote repository...
    set REMOTE=%~1
    set BRANCH=%~2
    if "%REMOTE%"=="" set REMOTE=origin
    if "%BRANCH%"=="" (
        git pull %REMOTE%
    ) else (
        git pull %REMOTE% %BRANCH%
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="clone" (
    echo Cloning repository...
    set REPO_URL=%~1
    set TARGET_DIR=%~2
    if "%REPO_URL%"=="" (
        echo Repository URL is required.
        exit /b 1
    )
    if "%TARGET_DIR%"=="" (
        git clone %REPO_URL%
    ) else (
        git clone %REPO_URL% %TARGET_DIR%
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="branch" (
    echo Managing branches...
    set BRANCH_NAME=%~1
    if "%BRANCH_NAME%"=="" (
        git branch
    ) else (
        git branch %BRANCH_NAME%
    )
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="checkout" (
    echo Checking out branch...
    set BRANCH_NAME=%~1
    if "%BRANCH_NAME%"=="" (
        echo Branch name is required.
        exit /b 1
    )
    git checkout %BRANCH_NAME%
    exit /b %ERRORLEVEL%
)

if "%COMMAND%"=="setup-repo" (
    echo Setting up repository for GitHub...
    
    :: Initialize repository if needed
    if not exist ".git" (
        echo Initializing Git repository...
        git init
        if %ERRORLEVEL% neq 0 (
            echo Failed to initialize Git repository.
            exit /b 1
        )
    )
    
    :: Create .gitignore
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
    
    :: Add all files
    echo Adding files to Git...
    git add .
    if %ERRORLEVEL% neq 0 (
        echo Failed to add files to Git.
        exit /b 1
    )
    
    :: Commit changes
    echo Committing changes...
    set COMMIT_MSG=%~1
    if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit of Claude MCP tools
    git commit -m "%COMMIT_MSG%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to commit changes.
        exit /b 1
    )
    
    :: Add remote if provided
    set REPO_URL=%~2
    if not "%REPO_URL%"=="" (
        echo Adding remote repository...
        git remote add origin %REPO_URL%
        if %ERRORLEVEL% neq 0 (
            echo Failed to add remote repository.
            exit /b 1
        )
        
        :: Push to remote
        echo Pushing to GitHub...
        git push -u origin main || git push -u origin master
        if %ERRORLEVEL% neq 0 (
            echo Failed to push to GitHub.
            echo You may need to manually push using: git push -u origin main
            exit /b 1
        )
    ) else (
        echo.
        echo Repository setup complete!
        echo To push to GitHub, create a repository at https://github.com/new
        echo Then run: git_operations.bat remote-add origin YOUR_REPO_URL
        echo Followed by: git_operations.bat push
    )
    
    exit /b 0
)

echo Unknown command: %COMMAND%
echo.
echo Available commands:
echo   status            - Show repository status
echo   init              - Initialize a Git repository
echo   create-gitignore  - Create a .gitignore file
echo   add [files]       - Add files to staging (default: all files)
echo   commit "message"  - Commit changes with a message
echo   remote-add name url - Add a remote repository
echo   push [remote] [branch] - Push to remote (default: origin main/master)
echo   pull [remote] [branch] - Pull from remote
echo   clone url [dir]   - Clone a repository
echo   branch [name]     - Create or list branches
echo   checkout branch   - Switch to a branch
echo   setup-repo [msg] [url] - Setup repository for GitHub

exit /b 1
