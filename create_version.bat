@echo off
echo 🏷️ Create Version Tag...

cd /d "C:\Users\iliya\OneDrive\Desktop\Skywind_Uni_Prod_Scrap_Protected V1.0\EXTRACT\Universal-Product-Scraper-Clean"

set /p version="Enter version tag (e.g., v1.1-fixed-validation): "
set /p description="Enter version description: "

echo ✅ Creating tag...
git tag -a %version% -m "%description%"

echo ✅ Pushing tag to GitHub...
git push origin %version%

echo 🎯 DONE! Version %version% created.
echo View at: https://github.com/iliyaruvinsky/universal-product-scraper-clean/releases
pause