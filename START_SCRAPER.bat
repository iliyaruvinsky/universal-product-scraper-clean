@echo off
title Universal Product Scraper v1.3
color 07

echo.
echo ==================================================================================
echo  🚀 UNIVERSAL PRODUCT SCRAPER v1.3
echo ==================================================================================
echo  Professional Price Comparison Tool for ZAP.co.il
echo  Corporate Edition - Ready for Production Use
echo ==================================================================================
echo.

:: Check if we're in the correct directory
if not exist "natural_cli.py" (
    echo ❌ ERROR: Scraper files not found in current directory
    echo.
    echo Please ensure you're running this from the installation folder
    echo or use the desktop shortcut.
    echo.
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please run INSTALL.bat first to set up the environment
    echo.
    pause
    exit /b 1
)

:: Quick dependency check
echo 🔍 Checking system dependencies...
python -c "import selenium, openpyxl, requests" >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Required packages not installed
    echo.
    echo Please run INSTALL.bat first to install dependencies
    echo.
    pause
    exit /b 1
)

echo ✅ System check passed
echo.

:: Check Chrome
echo 🔍 Checking Chrome browser...
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version >nul 2>&1
if %errorLevel% neq 0 (
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version >nul 2>&1
    if %errorLevel% neq 0 (
        echo ⚠️  Chrome not detected - WebDriver will auto-download
    ) else (
        echo ✅ Chrome browser found
    )
) else (
    echo ✅ Chrome browser found
)
echo.

:: Create necessary directories
if not exist "output" mkdir output
if not exist "logs" mkdir logs

:: Start the application
echo 🚀 Starting Universal Product Scraper...
echo.
echo ==================================================================================
echo  WELCOME TO UNIVERSAL PRODUCT SCRAPER
echo ==================================================================================
echo.
echo 💡 QUICK START TIPS:
echo    • Choose "Quick scraping wizard" for easiest experience
echo    • Have your Excel file with product list ready
echo    • Results will be saved in the 'output' folder
echo    • Press Ctrl+C to exit safely at any time
echo.
echo 🔐 FIRST TIME LOGIN:
echo    Username: admin
echo    Password: Admin@123
echo    (Change password when prompted)
echo.
echo ==================================================================================
echo.

:: Launch the CLI application
python natural_cli.py

:: Check exit code
if %errorLevel% neq 0 (
    echo.
    echo ==================================================================================
    echo ⚠️  APPLICATION EXITED WITH ERRORS
    echo ==================================================================================
    echo.
    echo If you encountered issues:
    echo  1. Check the logs\ folder for error details
    echo  2. Ensure your internet connection is working  
    echo  3. Try running INSTALL.bat again
    echo  4. Contact IT support if problems persist
    echo.
) else (
    echo.
    echo ==================================================================================
    echo ✅ APPLICATION CLOSED SUCCESSFULLY
    echo ==================================================================================
    echo.
    echo Your results are saved in the 'output' folder
    echo Thank you for using Universal Product Scraper!
    echo.
)

echo Press any key to close this window...
pause >nul