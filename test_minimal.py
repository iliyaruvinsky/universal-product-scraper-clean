import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Starting minimal test for row 21...")

# Setup Chrome
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

try:
    print("Creating driver...")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    
    print("Navigating to ZAP...")
    driver.get("https://www.zap.co.il")
    
    print("Waiting for search box...")
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "acSearch-input"))
    )
    
    print("Entering search term: Electra A INV 340")
    search.clear()
    search.send_keys("Electra-A-INV-340")
    
    print("Waiting 3 seconds for dropdown...")
    time.sleep(3)
    
    # Check for dropdown
    dropdowns = driver.find_elements(By.CSS_SELECTOR, ".acSearch-row-container")
    print(f"Found {len(dropdowns)} dropdown suggestions")
    
    if dropdowns:
        print("Clicking first dropdown...")
        dropdowns[0].click()
    else:
        print("No dropdown, pressing Enter...")
        from selenium.webdriver.common.keys import Keys
        search.send_keys(Keys.ENTER)
    
    print("Waiting for page load...")
    time.sleep(5)
    
    print(f"Current URL: {driver.current_url}")
    
    # Check what page we're on
    if "model.aspx?modelid=" in driver.current_url:
        print("✅ Direct model page reached!")
    elif "models.aspx" in driver.current_url or "search" in driver.current_url:
        print("📋 Search results page reached")
        # Try to find model links
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='model.aspx?modelid=']")
        print(f"Found {len(links)} model links")
    
    print("Test complete!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Closing driver...")
    driver.quit()
    print("Done!")