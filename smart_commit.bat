@echo off
echo 🔄 Smart Commit with Version Management
echo ========================================

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

echo.
echo 📋 COMMIT TYPES:
echo [1] 🐛 BUG FIX      - Fixed a problem
echo [2] ✨ NEW FEATURE  - Added new functionality  
echo [3] 🔧 IMPROVEMENT  - Enhanced existing feature
echo [4] 📚 DOCUMENTATION - Updated docs or comments
echo [5] 🧪 TESTING      - Added or updated tests
echo [6] 🚀 RELEASE      - Major milestone (creates version tag)
echo.

set /p choice="Choose commit type (1-6): "

if "%choice%"=="1" (
    set prefix=🐛 BUG FIX:
    set type=fix
)
if "%choice%"=="2" (
    set prefix=✨ NEW FEATURE:
    set type=feat
)
if "%choice%"=="3" (
    set prefix=🔧 IMPROVEMENT:
    set type=enhance
)
if "%choice%"=="4" (
    set prefix=📚 DOCS:
    set type=docs
)
if "%choice%"=="5" (
    set prefix=🧪 TEST:
    set type=test
)
if "%choice%"=="6" (
    set prefix=🚀 RELEASE:
    set type=release
)

set /p description="Enter description: "

echo.
echo ✅ Adding files...
git add .

echo ✅ Committing...
git commit -m "%prefix% %description%"

echo ✅ Pushing to GitHub...
git push origin main

if "%choice%"=="6" (
    echo.
    echo 🏷️ Creating version tag for release...
    set /p version="Enter version (e.g., v1.1): "
    git tag -a %version% -m "Release %version%: %description%"
    git push origin %version%
    echo ✅ Version %version% created!
)

echo.
echo 🎯 DONE! Changes pushed to GitHub.
echo 📱 View at: https://github.com/iliyaruvinsky/universal-product-scraper-clean
pause