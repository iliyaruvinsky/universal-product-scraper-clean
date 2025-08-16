@echo off
echo.
echo ==================================================================================
echo  CREATING CORPORATE DISTRIBUTION PACKAGE
echo ==================================================================================
echo  Universal Product Scraper v1.3 - Corporate Edition
echo ==================================================================================
echo.

set "DIST_NAME=Universal_Product_Scraper_v1.3_Corporate"
set "DIST_DIR=%~dp0dist\"
set "PACKAGE_DIR=%DIST_DIR%%DIST_NAME%\"

:: Clean previous distribution
if exist "%DIST_DIR%" (
    echo 🧹 Cleaning previous distribution...
    rmdir /s /q "%DIST_DIR%"
)

:: Create distribution directory
echo 📁 Creating distribution directory...
mkdir "%PACKAGE_DIR%"

:: Copy essential files
echo 📋 Copying essential application files...

:: Core application files
copy "natural_cli.py" "%PACKAGE_DIR%"
copy "production_scraper.py" "%PACKAGE_DIR%"
copy "excel_validator.py" "%PACKAGE_DIR%"
copy "requirements.txt" "%PACKAGE_DIR%"

:: Distribution files
copy "INSTALL.bat" "%PACKAGE_DIR%"
copy "START_SCRAPER.bat" "%PACKAGE_DIR%"
copy "DISTRIBUTION_README.md" "%PACKAGE_DIR%README.md"
copy "CORPORATE_USER_GUIDE.md" "%PACKAGE_DIR%"

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
copy "SETUP_INSTRUCTIONS.md" "%PACKAGE_DIR%"
copy "EXCEL_VALIDATOR_GUIDE.md" "%PACKAGE_DIR%"

:: Create data directory with sample
echo 📊 Setting up data directory...
mkdir "%PACKAGE_DIR%data\"
copy "data\SOURCE.xlsx" "%PACKAGE_DIR%data\"
copy "data\sample_products.json" "%PACKAGE_DIR%data\"

:: Create empty directories
mkdir "%PACKAGE_DIR%output\"
mkdir "%PACKAGE_DIR%logs\"

:: Create clean auth directory (no existing users)
mkdir "%PACKAGE_DIR%data\auth\"

:: Copy license and legal files
if exist "LICENSE.txt" copy "LICENSE.txt" "%PACKAGE_DIR%"

:: Create version info file
echo Creating version information...
echo # Universal Product Scraper v1.3 Corporate Edition > "%PACKAGE_DIR%VERSION.txt"
echo. >> "%PACKAGE_DIR%VERSION.txt"
echo Release Date: %DATE% >> "%PACKAGE_DIR%VERSION.txt"
echo Build Type: Corporate Distribution >> "%PACKAGE_DIR%VERSION.txt"
echo. >> "%PACKAGE_DIR%VERSION.txt"
echo ## Features Included: >> "%PACKAGE_DIR%VERSION.txt"
echo - HVAC-only product filtering (Samsung Galaxy fix) >> "%PACKAGE_DIR%VERSION.txt"
echo - Enterprise authentication system >> "%PACKAGE_DIR%VERSION.txt"
echo - Automated installation script >> "%PACKAGE_DIR%VERSION.txt"
echo - User-friendly CLI interface >> "%PACKAGE_DIR%VERSION.txt"
echo - Excel validation and reporting >> "%PACKAGE_DIR%VERSION.txt"
echo - Hebrew text processing for Israeli products >> "%PACKAGE_DIR%VERSION.txt"
echo - Chrome WebDriver auto-management >> "%PACKAGE_DIR%VERSION.txt"
echo - Corporate proxy support >> "%PACKAGE_DIR%VERSION.txt"
echo. >> "%PACKAGE_DIR%VERSION.txt"
echo ## Bug Fixes: >> "%PACKAGE_DIR%VERSION.txt"
echo - Fixed Samsung Galaxy phone pollution in HVAC searches >> "%PACKAGE_DIR%VERSION.txt"
echo - Enhanced product filtering and categorization >> "%PACKAGE_DIR%VERSION.txt"
echo - Improved Hebrew character handling >> "%PACKAGE_DIR%VERSION.txt"

:: Create deployment checklist
echo 📋 Creating deployment checklist...
echo # Corporate Deployment Checklist > "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo. >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo ## Pre-Deployment (IT Team): >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Extract package to target location ^(e.g., C:\ProductScraper\^) >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Ensure Python 3.11+ is available ^(or use automated installer^) >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Configure proxy settings if needed ^(config/default_config.json^) >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Whitelist required domains in firewall >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Test installation on pilot machine >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo. >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo ## Installation: >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Right-click INSTALL.bat ^→ "Run as Administrator" >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Verify desktop shortcuts are created >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Test application launch with START_SCRAPER.bat >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Verify login with admin/Admin@123 >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Change default admin password >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo. >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo ## User Training: >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Distribute CORPORATE_USER_GUIDE.md >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Demonstrate quick scraping wizard >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Show Excel format requirements >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Explain result interpretation >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo. >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo ## Post-Deployment Monitoring: >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Monitor logs/ directory for errors >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Collect user feedback >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"
echo - [ ] Document any configuration changes needed >> "%PACKAGE_DIR%DEPLOYMENT_CHECKLIST.md"

:: Create ZIP package (if 7-zip or PowerShell available)
echo 📦 Creating ZIP package...
powershell -command "Compress-Archive -Path '%PACKAGE_DIR%*' -DestinationPath '%DIST_DIR%%DIST_NAME%.zip' -Force" 2>nul
if %errorLevel% equ 0 (
    echo ✅ ZIP package created: %DIST_NAME%.zip
) else (
    echo ⚠️  ZIP creation failed - package folder created instead
)

echo.
echo ==================================================================================
echo ✅ CORPORATE DISTRIBUTION PACKAGE READY!
echo ==================================================================================
echo.
echo 📁 Package Location: %PACKAGE_DIR%
if exist "%DIST_DIR%%DIST_NAME%.zip" (
    echo 📦 ZIP Package: %DIST_NAME%.zip
)
echo.
echo 📋 What's Included:
echo  ✅ Complete application with all fixes
echo  ✅ Automated installation script ^(INSTALL.bat^)
echo  ✅ User-friendly launcher ^(START_SCRAPER.bat^)
echo  ✅ Corporate user guide
echo  ✅ Deployment checklist
echo  ✅ Technical documentation
echo  ✅ Sample data files
echo.
echo 🚀 Ready for Corporate Deployment!
echo.
echo 📤 NEXT STEPS:
echo  1. Test the package on a clean machine
echo  2. Distribute to target computers
echo  3. Follow DEPLOYMENT_CHECKLIST.md
echo  4. Train end users with CORPORATE_USER_GUIDE.md
echo.

pause