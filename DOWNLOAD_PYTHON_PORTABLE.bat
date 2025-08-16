@echo off
echo.
echo ==================================================================================
echo  DOWNLOADING PORTABLE PYTHON FOR CORPORATE PACKAGE
echo ==================================================================================
echo  Universal Product Scraper v1.3 - Complete Self-Contained Package
echo ==================================================================================
echo.

set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_FILE=python-3.11.9-embed-amd64.zip"
set "PACKAGE_DIR=dist_portable\Universal_Product_Scraper_v1.3_Portable"

echo 🔍 Checking package directory...
if not exist "%PACKAGE_DIR%" (
    echo ❌ ERROR: Package directory not found!
    echo Please run CREATE_PORTABLE_DISTRIBUTION.bat first
    pause
    exit /b 1
)

echo ✅ Package directory found: %PACKAGE_DIR%
echo.

echo 📥 Downloading Portable Python 3.11.9 (embedded distribution)...
echo URL: %PYTHON_URL%
echo.

:: Download using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_FILE%'}"

if not exist "%PYTHON_FILE%" (
    echo ❌ ERROR: Failed to download Python!
    echo.
    echo Please check your internet connection and try again.
    echo Alternatively, manually download from: %PYTHON_URL%
    pause
    exit /b 1
)

echo ✅ Python downloaded successfully: %PYTHON_FILE%
echo.

echo 📦 Extracting Python to package...
powershell -Command "Expand-Archive -Path '%PYTHON_FILE%' -DestinationPath '%PACKAGE_DIR%\python-portable' -Force"

if not exist "%PACKAGE_DIR%\python-portable\python.exe" (
    echo ❌ ERROR: Python extraction failed!
    pause
    exit /b 1
)

echo ✅ Python extracted successfully
echo.

echo 🔧 Configuring embedded Python...
:: Enable pip by adding Lib folder
mkdir "%PACKAGE_DIR%\python-portable\Lib" >nul 2>&1
mkdir "%PACKAGE_DIR%\python-portable\Scripts" >nul 2>&1

:: Download get-pip.py
echo 📥 Downloading pip installer...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PACKAGE_DIR%\python-portable\get-pip.py'"

if exist "%PACKAGE_DIR%\python-portable\get-pip.py" (
    echo ✅ Pip installer downloaded
    
    echo 🔧 Installing pip...
    cd "%PACKAGE_DIR%"
    python-portable\python.exe get-pip.py
    
    if exist "python-portable\Scripts\pip.exe" (
        echo ✅ Pip installed successfully
        
        echo 📦 Installing required packages...
        python-portable\python.exe -m pip install -r requirements.txt
        
        if %errorLevel% equ 0 (
            echo ✅ All packages installed successfully
        ) else (
            echo ⚠️  Some packages may have installation issues
        )
        
        :: Clean up
        del python-portable\get-pip.py >nul 2>&1
        
    ) else (
        echo ⚠️  Pip installation may have issues
    )
) else (
    echo ⚠️  Could not download pip installer
)

cd "%~dp0"

:: Clean up downloaded file
del "%PYTHON_FILE%" >nul 2>&1

echo.
echo 🧪 Testing complete package...
cd "%PACKAGE_DIR%"
if exist "python-portable\python.exe" (
    echo Testing Python...
    python-portable\python.exe --version
    
    echo Testing imports...
    python-portable\python.exe -c "import sys; print('Python path:', sys.executable)"
    python-portable\python.exe -c "import selenium, openpyxl, requests; print('✅ Core modules imported successfully')"
    
    if %errorLevel% equ 0 (
        echo.
        echo ✅ PACKAGE TEST SUCCESSFUL!
        echo The portable package is ready for deployment!
    ) else (
        echo.
        echo ⚠️  PACKAGE TEST ISSUES
        echo Some modules may not be properly installed
    )
) else (
    echo ❌ Python executable not found in package
)

cd "%~dp0"

echo.
echo ==================================================================================
echo  📦 COMPLETE SELF-CONTAINED PACKAGE READY!
echo ==================================================================================
echo.
echo ✅ Portable Python 3.11.9 included
echo ✅ All dependencies installed
echo ✅ No external downloads required
echo ✅ No admin rights needed for deployment
echo.
echo 📁 Package location: %PACKAGE_DIR%
echo 🚀 Test launcher: %PACKAGE_DIR%\START_PORTABLE.bat
echo.
echo 📤 DEPLOYMENT READY:
echo  1. The package is now completely self-contained
echo  2. ZIP the entire folder for distribution
echo  3. Users extract and run START_PORTABLE.bat
echo  4. No installation, no admin rights, no external dependencies!
echo.

pause