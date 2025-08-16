#!/usr/bin/env python3
"""
Analyze HTML structure for better CSS selectors on ZAP search results page
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re

def analyze_html_structure():
    print("🔍 **HTML STRUCTURE ANALYSIS FOR ZAP SEARCH RESULTS**")
    print("=" * 80)
    
    product_name = "Tornado SLIM-SQ-PRO-INV X 25 1 PH"
    
    # Setup Chrome
    chrome_options = Options()
    # Use visible mode to match production scraper settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navigate and search (replicate SUB-OPTION 1B exactly)
        print("📍 **STEP 1: Navigate and Search**")
        driver.get("https://www.zap.co.il")
        time.sleep(3)
        
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#acSearch-input"))
        )
        search_box.clear()
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)
        
        print(f"✅ Current URL: {driver.current_url}")
        print()
        
        # Analyze current CSS selector
        print("📍 **STEP 2: Current CSS Selector Analysis**")
        current_selector = "a[href*='model.aspx?modelid=']"
        current_links = driver.find_elements(By.CSS_SELECTOR, current_selector)
        print(f"🔍 Current selector '{current_selector}' finds: {len(current_links)} elements")
        
        if current_links:
            print("Current selector results:")
            for i, link in enumerate(current_links[:5], 1):
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    print(f"  {i}. Text: '{text}' | URL: {href}")
                except:
                    print(f"  {i}. Error reading element")
        print()
        
        # Search for Tornado mentions
        print("📍 **STEP 3: Search for Tornado Elements**")
        tornado_selectors = [
            "//*[contains(text(), 'Tornado')]",
            "//*[contains(text(), 'TORNADO')]", 
            "//*[contains(text(), 'טורנדו')]",
            "//*[contains(@class, 'tornado')]",
            "//*[contains(@id, 'tornado')]"
        ]
        
        tornado_elements = []
        for selector in tornado_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                tornado_elements.extend(elements)
                print(f"🌪️ Selector '{selector}': {len(elements)} elements")
            except:
                print(f"❌ Selector '{selector}': Failed")
        
        # Remove duplicates
        unique_tornado = list(set(tornado_elements))
        print(f"🎯 Total unique Tornado elements: {len(unique_tornado)}")
        print()
        
        # Analyze Tornado element structure
        print("📍 **STEP 4: Tornado Element Structure Analysis**")
        for i, element in enumerate(unique_tornado[:10], 1):
            try:
                tag = element.tag_name
                text = element.text.strip()
                classes = element.get_attribute('class')
                parent_tag = element.find_element(By.XPATH, "..").tag_name
                parent_classes = element.find_element(By.XPATH, "..").get_attribute('class')
                
                print(f"Tornado Element {i}:")
                print(f"  Tag: <{tag}> | Classes: '{classes}'")
                print(f"  Text: '{text[:100]}...'")
                print(f"  Parent: <{parent_tag}> | Classes: '{parent_classes}'")
                
                # Look for clickable links in this element's vicinity
                nearby_links = element.find_elements(By.XPATH, ".//a | ../a | ../../a")
                if nearby_links:
                    for j, link in enumerate(nearby_links[:3], 1):
                        href = link.get_attribute('href')
                        link_text = link.text.strip()
                        print(f"    Link {j}: '{link_text[:50]}...' -> {href}")
                print()
            except Exception as e:
                print(f"  Error analyzing element {i}: {e}")
        
        # Search for specific price elements from screenshot
        print("📍 **STEP 5: Price Element Analysis**")
        price_patterns = ['3,399', '3,389', '₪3,399', '₪3,389']
        for pattern in price_patterns:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
            print(f"💰 Price '{pattern}': {len(elements)} elements")
            
            for i, element in enumerate(elements[:3], 1):
                try:
                    text = element.text.strip()
                    tag = element.tag_name
                    classes = element.get_attribute('class')
                    print(f"  {i}. <{tag}> class='{classes}': '{text}'")
                    
                    # Find parent container
                    parent = element.find_element(By.XPATH, "../..")
                    parent_text = parent.text.strip()
                    print(f"      Parent container: '{parent_text[:150]}...'")
                except:
                    print(f"  {i}. Error reading price element")
        print()
        
        # Alternative CSS selectors to try
        print("📍 **STEP 6: Alternative CSS Selector Testing**")
        alternative_selectors = [
            "a[href*='/model.aspx']",
            "a[href*='modelid']", 
            "[class*='model']",
            "[class*='product']",
            "[class*='item']",
            "[class*='result']",
            "div[class*='card']",
            "div[class*='item']",
            ".product-item",
            ".search-result",
            ".model-item",
            "article",
            "[data-model]",
            "[data-product]"
        ]
        
        for selector in alternative_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"🔍 '{selector}': {len(elements)} elements")
                
                # Check if any contain Tornado
                tornado_count = 0
                for element in elements[:10]:
                    try:
                        if 'tornado' in element.text.lower() or 'טורנדו' in element.text:
                            tornado_count += 1
                    except:
                        pass
                if tornado_count > 0:
                    print(f"    ⭐ Contains {tornado_count} Tornado mentions!")
            except:
                print(f"❌ '{selector}': Invalid selector")
        print()
        
        # Extract page source for manual inspection
        print("📍 **STEP 7: Page Source Analysis**")
        page_source = driver.page_source
        
        # Look for specific patterns in HTML
        tornado_in_html = page_source.count('Tornado') + page_source.count('TORNADO') + page_source.count('טורנדו')
        slim_in_html = page_source.count('SLIM') + page_source.count('slim')
        
        print(f"📄 Page source analysis:")
        print(f"  Tornado mentions: {tornado_in_html}")
        print(f"  SLIM mentions: {slim_in_html}")
        
        # Save page source for manual inspection
        with open("zap_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"💾 Page source saved: zap_page_source.html")
        
        # Take screenshot
        driver.save_screenshot("zap_analysis_screenshot.png")
        print(f"📸 Screenshot saved: zap_analysis_screenshot.png")
        
        print("\n⏳ Keeping browser open for 10 seconds for manual inspection...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass
        print("\n✅ **Analysis Complete**")

if __name__ == "__main__":
    analyze_html_structure()