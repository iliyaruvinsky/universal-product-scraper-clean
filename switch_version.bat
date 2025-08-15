@echo off
echo 🔄 Switch Between Versions
echo ==========================

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

echo.
echo 📋 AVAILABLE OPTIONS:
echo [1] View all versions
echo [2] Switch to specific version
echo [3] Return to latest (main branch)
echo [4] Create new branch for testing
echo.

set /p choice="Choose option (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🏷️ Available versions:
    git tag -l
    echo.
    echo 📝 Recent commits:
    git log --oneline -10
)

if "%choice%"=="2" (
    echo.
    echo 🏷️ Available versions:
    git tag -l
    echo.
    set /p version="Enter version to switch to: "
    git checkout %version%
    echo ✅ Switched to version %version%
    echo ⚠️  You are now in 'detached HEAD' state.
    echo ⚠️  Make changes in a new branch if needed.
)

if "%choice%"=="3" (
    git checkout main
    git pull origin main
    echo ✅ Returned to latest version.
)

if "%choice%"=="4" (
    set /p branch_name="Enter new branch name: "
    git checkout -b %branch_name%
    echo ✅ Created and switched to branch '%branch_name%'
    echo 💡 Push with: git push origin %branch_name%
)

echo.
echo 🎯 Current status:
git status --short
pause