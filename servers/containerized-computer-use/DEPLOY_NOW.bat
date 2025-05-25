@echo off
cls
echo ============================================================
echo  AUTONOMOUS DEPLOYMENT - Containerized Computer Use MCP
echo ============================================================
echo.
echo This script will automatically:
echo   1. Validate prerequisites
echo   2. Build Docker image
echo   3. Start container
echo   4. Run tests
echo   5. Update Claude Desktop config
echo   6. Report what manual steps are needed
echo.
echo ============================================================
echo.
echo Press any key to start autonomous deployment...
pause > nul

REM Run the autonomous deployment script
python autonomous_deploy.py

echo.
echo ============================================================
echo.
echo Deployment complete! Check the summary above.
echo.
echo If successful, you only need to:
echo   1. Restart Claude Desktop
echo   2. Test with "Take a screenshot using the containerized computer"
echo.
pause
