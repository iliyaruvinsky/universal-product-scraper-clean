@echo off
echo.
echo ==================================================================================
echo  UNIVERSAL PRODUCT SCRAPER - Corporate Installation v1.3
echo ==================================================================================
echo  Enterprise Price Comparison Tool for Corporate Deployment
echo  Release: August 16, 2025
echo ==================================================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Administrator privileges required!
    echo.
    echo Please right-click INSTALL.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Administrator privileges confirmed
echo.

:: Set installation directory
set "INSTALL_DIR=%~dp0"
echo 📁 Installation directory: %INSTALL_DIR%
echo.

:: Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python not found! 
    echo.
    echo Please install Python 3.11+ from: https://www.python.org/downloads/
    echo ⚠️  During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

:: Check pip
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ pip not found! Installing pip...
    python -m ensurepip --upgrade
    if %errorLevel% neq 0 (
        echo ❌ Failed to install pip!
        pause
        exit /b 1
    )
)
echo ✅ pip is available
echo.

:: Upgrade pip
echo 🔄 Updating pip to latest version...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip updated
echo.

:: Install requirements
echo 📦 Installing required packages (this may take 2-3 minutes)...
echo    ⏳ Installing selenium, openpyxl, requests, and other dependencies...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo ❌ Failed to install requirements!
    echo.
    echo Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ All packages installed successfully
echo.

:: Create output directory
if not exist "output" (
    mkdir output
    echo ✅ Created output directory
)

:: Create logs directory  
if not exist "logs" (
    mkdir logs
    echo ✅ Created logs directory
)

:: Create desktop shortcut
echo 🔗 Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Universal Product Scraper.lnk"

:: Create VBS script to generate shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%START_SCRAPER.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Universal Product Scraper - Price Comparison Tool" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,21" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

if exist "%SHORTCUT%" (
    echo ✅ Desktop shortcut created
) else (
    echo ⚠️  Could not create desktop shortcut (not critical)
)
echo.

:: Test installation
echo 🧪 Testing installation...
python -c "import selenium, openpyxl, requests; print('✅ Core modules imported successfully')"
if %errorLevel% neq 0 (
    echo ❌ Installation test failed!
    pause
    exit /b 1
)

:: Create user guide shortcut on desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateGuide.vbs
echo sLinkFile = "%DESKTOP%\Product Scraper - User Guide.lnk" >> CreateGuide.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateGuide.vbs
echo oLink.TargetPath = "%INSTALL_DIR%docs\USER_GUIDE.md" >> CreateGuide.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%docs" >> CreateGuide.vbs
echo oLink.Description = "Universal Product Scraper - User Guide" >> CreateGuide.vbs
echo oLink.Save >> CreateGuide.vbs

cscript CreateGuide.vbs >nul 2>&1
del CreateGuide.vbs >nul 2>&1

echo.
echo ==================================================================================
echo  🎉 INSTALLATION COMPLETED SUCCESSFULLY!
echo ==================================================================================
echo.
echo ✅ Universal Product Scraper is ready to use
echo ✅ Desktop shortcut created: "Universal Product Scraper"
echo ✅ User guide shortcut created: "Product Scraper - User Guide"
echo.
echo 🚀 TO START THE APPLICATION:
echo    1. Double-click "Universal Product Scraper" on your desktop
echo    2. OR run: START_SCRAPER.bat from this folder
echo.
echo 👤 FIRST LOGIN:
echo    Username: admin
echo    Password: Admin@123
echo    (You'll be prompted to change the password)
echo.
echo 📖 FOR HELP:
echo    - Read the User Guide (shortcut on desktop)
echo    - Check docs\ folder for detailed documentation
echo.
echo ==================================================================================
echo.

:: Ask if user wants to start now
set /p "START_NOW=Would you like to start the application now? (y/n): "
if /i "%START_NOW%"=="y" (
    echo.
    echo 🚀 Starting Universal Product Scraper...
    call START_SCRAPER.bat
) else (
    echo.
    echo 👍 Installation complete! Use the desktop shortcut to start later.
)

echo.
pause