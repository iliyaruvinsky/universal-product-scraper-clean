@echo off
echo 🚀 Pushing EXTRACT to GitHub...

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

echo ✅ Setting remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/iliyaruvinsky/universal-product-scraper-clean.git

echo ✅ Pushing to GitHub...
git push -u origin main

echo 🎯 DONE! Repository available at:
echo https://github.com/iliyaruvinsky/universal-product-scraper-clean

pause