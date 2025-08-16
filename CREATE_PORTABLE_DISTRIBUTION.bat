@echo off
echo.
echo ==================================================================================
echo  CREATING PORTABLE CORPORATE DISTRIBUTION (NO ADMIN REQUIRED)
echo ==================================================================================
echo  Universal Product Scraper v1.3 - Self-Contained Corporate Edition
echo ==================================================================================
echo.

set "DIST_NAME=Universal_Product_Scraper_v1.3_Portable"
set "DIST_DIR=%~dp0dist_portable\"
set "PACKAGE_DIR=%DIST_DIR%%DIST_NAME%\"

:: Clean previous distribution
if exist "%DIST_DIR%" (
    echo 🧹 Cleaning previous portable distribution...
    rmdir /s /q "%DIST_DIR%"
)

:: Create portable distribution directory
echo 📁 Creating portable distribution directory...
mkdir "%PACKAGE_DIR%"

:: Copy essential files
echo 📋 Copying essential application files...
copy "natural_cli.py" "%PACKAGE_DIR%"
copy "production_scraper.py" "%PACKAGE_DIR%"
copy "excel_validator.py" "%PACKAGE_DIR%"
copy "requirements.txt" "%PACKAGE_DIR%"

:: Copy src directory
echo 📦 Copying source code...
xcopy /E /I "src" "%PACKAGE_DIR%src\"

:: Copy config directory
echo ⚙️ Copying configuration...
xcopy /E /I "config" "%PACKAGE_DIR%config\"

:: Copy documentation
echo 📖 Copying documentation...
xcopy /E /I "docs" "%PACKAGE_DIR%docs\"

:: Copy essential documentation files
copy "QUICKSTART.md" "%PACKAGE_DIR%"
copy "EXCEL_VALIDATOR_GUIDE.md" "%PACKAGE_DIR%"

:: Create data directory with sample
echo 📊 Setting up data directory...
mkdir "%PACKAGE_DIR%data\"
copy "data\SOURCE.xlsx" "%PACKAGE_DIR%data\"
copy "data\sample_products.json" "%PACKAGE_DIR%data\"

:: Create empty directories
mkdir "%PACKAGE_DIR%output\"
mkdir "%PACKAGE_DIR%logs\"
mkdir "%PACKAGE_DIR%data\auth\"

:: Create portable launcher (NO ADMIN REQUIRED)
echo 🚀 Creating portable launcher...
echo @echo off > "%PACKAGE_DIR%START_PORTABLE.bat"
echo title Universal Product Scraper v1.3 - Portable Edition >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo color 07 >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ================================================================================== >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo  🚀 UNIVERSAL PRODUCT SCRAPER v1.3 - PORTABLE EDITION >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ================================================================================== >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo  Professional Price Comparison Tool - No Installation Required >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo  Corporate Edition - Run from Any Location >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ================================================================================== >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ✅ PORTABLE MODE: No admin rights required >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ✅ SELF-CONTAINED: Python included >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ✅ READY TO USE: Just run and go! >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo ================================================================================== >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo echo 🔍 Checking portable Python... >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo if exist "python-portable\python.exe" ( >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo ✅ Portable Python found >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo 🚀 Starting application... >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     python-portable\python.exe natural_cli.py >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo ^) else ( >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo ❌ ERROR: Portable Python not found! >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo This package requires the portable Python installation. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo Please contact IT support for the complete package. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     echo. >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo     pause >> "%PACKAGE_DIR%START_PORTABLE.bat"
echo ^) >> "%PACKAGE_DIR%START_PORTABLE.bat"

:: Create portable setup instructions
echo 📋 Creating portable setup instructions...
echo # Universal Product Scraper v1.3 - Portable Corporate Edition > "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo **🎯 ZERO-INSTALLATION CORPORATE PACKAGE** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo **No Admin Rights Required • No Dependencies • Just Run!** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo --- >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ## 🚀 Quick Start ^(30 Seconds^) >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 1. **Extract** the ZIP file to any location ^(Desktop, Documents, USB drive^) >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 2. **Double-click** `START_PORTABLE.bat` >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 3. **Login** with: admin/Admin@123 >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 4. **Choose** "Quick scraping wizard" >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 5. **Done!** 🎉 >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ## ✅ Corporate Advantages >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **No Admin Rights** - Runs with standard user permissions >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **No Installation** - Extract and run from anywhere >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **Self-Contained** - Includes Python and all dependencies >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **USB Friendly** - Can run from removable drives >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **Network Safe** - No system modifications required >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **IT Approved** - Standard user deployment model >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ## 📋 Complete Package Contents >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo To make this package complete, you need to add: >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 1. **Portable Python 3.11+** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo    - Download from: https://www.python.org/downloads/windows/ >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo    - Choose "Windows installer ^(64-bit^)" >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo    - Install to: `python-portable/` folder >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 2. **Pre-installed Dependencies** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo    - Run: `python-portable\python.exe -m pip install -r requirements.txt` >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo    - All packages will be included in the portable Python >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ## 🔧 IT Administrator Instructions >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ### Step 1: Prepare Complete Package >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ```cmd >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 1. Download Python 3.11+ portable from python.org >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 2. Extract Python to: python-portable/ folder >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 3. Install dependencies: python-portable\python.exe -m pip install -r requirements.txt >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 4. Test: START_PORTABLE.bat >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo 5. Package: Create ZIP with complete folder >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ``` >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ### Step 2: Corporate Deployment >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **Share via:** Network drive, email, USB, or file server >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **User Instructions:** "Extract and double-click START_PORTABLE.bat" >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo - **No Support Needed:** Self-contained, no installation issues >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo ## 🆘 Troubleshooting >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo **Q: "Portable Python not found"** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo A: The python-portable folder is missing. Contact IT for complete package. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo **Q: "Access denied"** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo A: Extract to a location where you have write permissions ^(Documents, Desktop^). >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo **Q: "Chrome not found"** >> "%PACKAGE_DIR%PORTABLE_SETUP.md"
echo A: WebDriver will download automatically. Wait 30 seconds on first run. >> "%PACKAGE_DIR%PORTABLE_SETUP.md"

:: Create enhanced readme for portable version
echo 📖 Creating portable README...
echo # Universal Product Scraper v1.3 - Portable Corporate Edition > "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo **🎯 Zero-Installation Corporate Package** >> "%PACKAGE_DIR%README.md"
echo **Professional Price Comparison Tool • No Admin Rights Required** >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo --- >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo ## 🚀 For End Users ^(30-Second Start^) >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo 1. **Double-click**: `START_PORTABLE.bat` >> "%PACKAGE_DIR%README.md"
echo 2. **Login**: admin / Admin@123 >> "%PACKAGE_DIR%README.md"
echo 3. **Choose**: Quick scraping wizard >> "%PACKAGE_DIR%README.md"
echo 4. **Upload**: Your Excel file with products >> "%PACKAGE_DIR%README.md"
echo 5. **Wait**: 2-3 minutes per product >> "%PACKAGE_DIR%README.md"
echo 6. **Get**: Excel report with price comparisons >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo **That's it!** No installation, no admin rights, no hassle! 🎉 >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo ## ✅ Corporate Benefits >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo - ✅ **No Admin Rights** - Works with standard user permissions >> "%PACKAGE_DIR%README.md"
echo - ✅ **No Installation** - Extract and run from anywhere >> "%PACKAGE_DIR%README.md"
echo - ✅ **Self-Contained** - All dependencies included >> "%PACKAGE_DIR%README.md"
echo - ✅ **Portable** - Run from USB, network drive, or local folder >> "%PACKAGE_DIR%README.md"
echo - ✅ **IT Friendly** - No system changes or registry modifications >> "%PACKAGE_DIR%README.md"
echo - ✅ **Professional** - Clean interface, corporate-appropriate colors >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo ## 📋 What's Included >> "%PACKAGE_DIR%README.md"
echo. >> "%PACKAGE_DIR%README.md"
echo - Complete scraper application with Samsung Galaxy filtering fix >> "%PACKAGE_DIR%README.md"
echo - Portable Python runtime ^(when package is complete^) >> "%PACKAGE_DIR%README.md"
echo - All required dependencies pre-installed >> "%PACKAGE_DIR%README.md"
echo - User guides and documentation >> "%PACKAGE_DIR%README.md"
echo - Sample Excel templates >> "%PACKAGE_DIR%README.md"
echo - Enterprise authentication system >> "%PACKAGE_DIR%README.md"

echo.
echo ==================================================================================
echo ✅ PORTABLE DISTRIBUTION PACKAGE CREATED!
echo ==================================================================================
echo.
echo 📁 Package Location: %PACKAGE_DIR%
echo.
echo 📋 What's Included:
echo  ✅ Complete application ^(no admin rights required^)
echo  ✅ Portable launcher ^(START_PORTABLE.bat^)
echo  ✅ Setup instructions for IT teams
echo  ✅ End-user documentation
echo  ✅ Professional color scheme ^(subtle gray^)
echo.
echo ⚠️  TO COMPLETE THE PACKAGE:
echo.
echo 1. Add Portable Python 3.11+ to: python-portable/ folder
echo 2. Install dependencies in portable Python
echo 3. Test with START_PORTABLE.bat
echo 4. Package as ZIP for distribution
echo.
echo 📤 NEXT STEPS FOR IT TEAM:
echo  1. Follow instructions in PORTABLE_SETUP.md
echo  2. Create complete self-contained package
echo  3. Test on machine without Python
echo  4. Distribute to end users
echo.

pause