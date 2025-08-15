@echo off
echo 📥 Pull Latest Changes from GitHub
echo ==================================

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

echo ✅ Fetching latest changes...
git fetch origin

echo ✅ Pulling changes...
git pull origin main

echo.
echo 📊 Recent commits:
git log --oneline -5

echo.
echo 🎯 DONE! You now have the latest version.
pause