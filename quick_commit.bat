@echo off
echo 🔄 Quick Commit to GitHub...

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

set /p commit_msg="Enter commit message: "

echo ✅ Adding files...
git add .

echo ✅ Committing...
git commit -m "%commit_msg%"

echo ✅ Pushing to GitHub...
git push origin main

echo 🎯 DONE! Changes pushed to GitHub.
pause