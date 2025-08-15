#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION SCRAPER - FIXED UNIFIED VERSION
Unified extraction logic for both explicit and headless modes
Based on proven HTML structure comparison results
"""

import sys
import os
import time
import re
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path for imports
sys.path.append(os.path.join(os.getcwd(), 'src'))
from excel.source_reader import SourceExcelReader

# Global headless mode flag
HEADLESS_MODE = False

def create_driver():
    """Create Chrome driver with unified configuration."""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    if HEADLESS_MODE:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
    
    driver = webdriver.Chrome(options=chrome_options)
    if HEADLESS_MODE:
        driver.set_window_size(1920, 1080)
    
    return driver

def search_and_filter_product(driver, product_name):
    """Search for product and navigate to model page using breakthrough method."""
    print(f"\n🔍 SEARCHING FOR: {product_name}")
    print(f"🤖 Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
    
    try:
        # Step 1: Navigate to ZAP homepage
        driver.get("https://zap.co.il")
        time.sleep(2)
        
        # Step 2: Find and use search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#acSearch-input"))
        )
        search_box.click()
        time.sleep(1)
        
        # Try hyphenated approach first (breakthrough method)
        hyphenated = product_name.replace(" ", "-")
        search_box.clear()
        search_box.send_keys(hyphenated)
        time.sleep(3)
        
        # Step 3: Look for dropdown suggestions
        dropdown_containers = driver.find_elements(By.CSS_SELECTOR, ".acSearch-row-container")
        
        if dropdown_containers:
            print(f"✅ Found {len(dropdown_containers)} dropdown suggestions")
            # Look for suggestions with model ID in data-search-link
            for container in dropdown_containers:
                try:
                    # Find the clickable div with data-search-link attribute
                    suggestion_div = container.find_element(By.CSS_SELECTOR, ".acSearch-row.acSearch-row-img[data-search-link*='modelid=']")
                    search_link = suggestion_div.get_attribute('data-search-link')
                    
                    # Extract model ID from the data-search-link
                    if 'modelid=' in search_link:
                        import re
                        model_id_match = re.search(r'modelid=(\d+)', search_link)
                        if model_id_match:
                            model_id = model_id_match.group(1)
                            # Construct direct model page URL
                            model_url = f"https://www.zap.co.il/model.aspx?modelid={model_id}"
                            print(f"📍 Found model ID {model_id} in dropdown")
                            print(f"📍 Navigating directly to: {model_url}")
                            
                            # Navigate directly to the model page
                            driver.get(model_url)
                            time.sleep(5 if HEADLESS_MODE else 3)
                            return "success", model_url
                except:
                    continue
            
            # Fallback: click the first suggestion if no model ID found
            try:
                first_suggestion = dropdown_containers[0].find_element(By.CSS_SELECTOR, ".acSearch-row.acSearch-row-img")
                print(f"📍 Clicking first dropdown suggestion")
                first_suggestion.click()
                time.sleep(5 if HEADLESS_MODE else 3)
                return "success", driver.current_url
            except:
                pass
        
        # Step 4: If no dropdown, press Enter to search
        print(f"⚠️ No dropdown found, pressing Enter to search")
        search_box.send_keys(Keys.ENTER)
        time.sleep(5 if HEADLESS_MODE else 3)
        
        # Step 5: Look for product links in search results
        try:
            product_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='model.aspx?modelid=']")
            if product_links:
                print(f"✅ Found {len(product_links)} product links in results")
                first_link = product_links[0]
                model_url = first_link.get_attribute('href')
                print(f"📍 Navigating to: {model_url}")
                driver.get(model_url)
                time.sleep(5 if HEADLESS_MODE else 3)
                return "success", model_url
            else:
                print(f"❌ No product links found")
                return "no_products", driver.current_url
        except Exception as e:
            print(f"❌ Error finding product links: {e}")
            return "failed", driver.current_url
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return "failed", driver.current_url

def extract_zap_product_name(driver):
    """Extract product name from ZAP page using working ZapScraper pattern."""
    try:
        # Try multiple selectors (copied from working ZapScraper._extract_product_name)
        selectors = [
            "h1", "h2.product-title",
            "[class*='product-name']", "[class*='product-title']",
            "[itemprop='name']", ".title", ".product_title"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if text and 5 < len(text) < 200:
                    print(f"✅ Extracted ZAP product name: {text}")
                    return text
                    
    except Exception as e:
        print(f"⚠️ Could not extract ZAP product name: {e}")
        
    return "Unknown Product"

def extract_individual_vendor_product_name(driver, vendor_url, vendor_name):
    """Extract product name from individual vendor page (like working ZapScraper)."""
    if not vendor_url:
        return f"Unknown Product ({vendor_name})"
    
    # Save current window
    original_window = driver.current_window_handle
    
    try:
        # Open vendor page in new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        print(f"   🔍 Visiting {vendor_name} page for product name...")
        driver.get(vendor_url)
        time.sleep(2)
        
        # Extract product name using same selectors as ZapScraper
        selectors = [
            "h1", "h2.product-title",
            "[class*='product-name']", "[class*='product-title']",
            "[itemprop='name']", ".title", ".product_title"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if text and 5 < len(text) < 200:
                    print(f"   ✅ Extracted from {vendor_name}: {text}")
                    return text
        
        print(f"   ⚠️ Could not extract product name from {vendor_name}")
        return f"Unknown Product ({vendor_name})"
        
    except Exception as e:
        print(f"   ❌ Failed to visit {vendor_name}: {e}")
        return f"Unknown Product ({vendor_name})"
        
    finally:
        # Close vendor tab and return to original
        try:
            driver.close()
            driver.switch_to.window(original_window)
        except:
            pass

def extract_vendors_unified(driver, zap_product_name="Unknown Product"):
    """UNIFIED vendor extraction - identical logic for both modes."""
    print(f"\n🏪 UNIFIED VENDOR EXTRACTION")
    print(f"🤖 Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
    
    vendors = []
    
    try:
        # UNIFIED: Same selectors for both modes (HTML structures are identical)
        vendor_rows = driver.find_elements(By.CSS_SELECTOR, ".compare-item-row.product-item")
        print(f"✅ Found {len(vendor_rows)} vendor rows using unified selector")
        
        if len(vendor_rows) == 0:
            # Simple fallback for both modes
            vendor_rows = driver.find_elements(By.CSS_SELECTOR, ".compare-item-row")
            print(f"✅ Fallback found {len(vendor_rows)} rows")
        
        for i, row in enumerate(vendor_rows, 1):
            try:
                print(f"\n🔍 Processing vendor {i}:")
                
                # UNIFIED: Extract vendor name (same logic for both modes)
                vendor_name = f"Vendor {i}"
                try:
                    logo_img = row.find_element(By.CSS_SELECTOR, ".compare-item-image.store a img[title]")
                    vendor_title = logo_img.get_attribute('title')
                    if vendor_title and vendor_title.lower() not in ['bullet', 'icon']:
                        vendor_name = vendor_title
                except:
                    try:
                        all_imgs = row.find_elements(By.CSS_SELECTOR, "img[title]")
                        for img in all_imgs:
                            title = img.get_attribute('title')
                            if title and title.lower() not in ['bullet', 'icon', ''] and len(title) > 2:
                                vendor_name = title
                                break
                    except:
                        pass
                
                # UNIFIED: Extract vendor URL (same logic for both modes)
                vendor_url = ""
                button_text = "לפרטים נוספים"
                try:
                    details_section = row.find_element(By.CSS_SELECTOR, ".compare-item-details")
                    vendor_link = details_section.find_element(By.CSS_SELECTOR, "a[href*='/fs']")
                    vendor_url = vendor_link.get_attribute('href')
                    button_text = vendor_link.text.strip() or "לפרטים נוספים"
                except:
                    pass
                
                # UNIFIED: Extract individual vendor product name (visit vendor page)
                individual_vendor_product_name = extract_individual_vendor_product_name(driver, vendor_url, vendor_name)
                
                # UNIFIED: Extract price using PROVEN working selector
                vendor_price = 0
                try:
                    # Use the WORKING selector proven by test: ".compare-item-details span"
                    price_element = row.find_element(By.CSS_SELECTOR, ".compare-item-details span")
                    price_text = price_element.text.strip()
                    print(f"   🔍 Price text: '{price_text}'")
                    
                    if price_text:
                        price_match = re.search(r'[\d,]+', price_text)
                        if price_match:
                            price_str = price_match.group().replace(',', '')
                            if price_str.isdigit() and len(price_str) >= 3:
                                vendor_price = int(price_str)
                                print(f"   ✅ Price extracted: ₪{vendor_price}")
                
                except Exception as e:
                    print(f"   ❌ Price extraction failed: {e}")
                
                vendors.append({
                    'vendor_name': vendor_name,
                    'vendor_price': vendor_price,
                    'vendor_url': vendor_url,
                    'button_text': button_text,
                    'vendor_product_name': individual_vendor_product_name
                })
                
                print(f"  {i}. {vendor_name} - ₪{vendor_price}")
                
            except Exception as e:
                print(f"  Error extracting vendor {i}: {e}")
                continue
        
        return vendors
        
    except Exception as e:
        print(f"❌ Unified vendor extraction failed: {e}")
        return []

def process_single_product(product_name, original_price, line_number):
    """Process a single product with unified approach."""
    driver = create_driver()
    start_time = time.time()
    
    try:
        print(f"\n{'='*70}")
        print(f"🚀 PROCESSING LINE {line_number}")
        print(f"📋 Product: {product_name}")
        print(f"💰 Original Price: ₪{original_price}")
        print(f"🤖 Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
        print(f"{'='*70}")
        
        # Step 1: Search and navigate to product page
        search_result, model_url = search_and_filter_product(driver, product_name)
        
        if search_result != "success":
            print(f"❌ Search failed: {search_result}")
            return {
                'line_number': line_number,
                'product_name': product_name,
                'original_price': original_price,
                'vendors': [],
                'search_result': search_result,
                'processing_time': time.time() - start_time,
                'model_url': model_url
            }
        
        # Step 2: Extract ZAP product name from current page
        zap_product_name = extract_zap_product_name(driver)
        
        # Step 3: Extract vendors using unified logic
        vendors = extract_vendors_unified(driver, zap_product_name)
        
        processing_time = time.time() - start_time
        
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   Line: {line_number}")
        print(f"   Product: {product_name}")
        print(f"   Vendors found: {len(vendors)}")
        print(f"   Processing time: {processing_time:.1f}s")
        print(f"   Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
        
        # Keep browser open briefly for verification (shorter in headless)
        if not HEADLESS_MODE:
            print(f"🔍 Browser open for 3 seconds for verification...")
            time.sleep(3)
        
        return {
            'line_number': line_number,
            'product_name': product_name,
            'original_price': original_price,
            'vendors': vendors,
            'search_result': search_result,
            'processing_time': processing_time,
            'model_url': model_url
        }
        
    finally:
        driver.quit()

def create_excel_file(results, filename=None):
    """Create Excel file with CORRECT Hebrew format matching target_writer structure."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/Lines_{'-'.join(str(r['line_number']) for r in results)}_Report_{timestamp}.xlsx"
    
    # Create directories
    os.makedirs("output", exist_ok=True)
    
    # Create workbook with two sheets
    wb = openpyxl.Workbook()
    
    # Sheet 1: Details (פירוט) - CORRECT Hebrew headers
    details_sheet = wb.active
    details_sheet.title = "פירוט"
    
    # Headers matching the expected format exactly
    details_headers = [
        "שורת מקור",           # A - Source Row
        "שם מוצר",             # B - Product Name  
        "מחיר",                # C - Original Price
        "שם ספק",              # D - Vendor Name
        "שם מוצר באתר הספק",    # E - Product on Vendor Site
        "מחיר ZAP",            # F - ZAP Price (vendor price)
        "הפרש מחיר",           # G - Price Difference
        "% הפרש",              # H - Percentage Difference  
        "טקסט הכפתור",         # I - Button Text
        "קישור",               # J - Link
        "זמן עדכון",           # K - Update Timestamp
        "Model ID",            # L - Model ID
        "Method Used"          # M - Method Used
    ]
    
    # Style headers
    from openpyxl.styles import Font, PatternFill, Alignment
    for col, header in enumerate(details_headers, 1):
        cell = details_sheet.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    # Sheet 2: Summary (סיכום) - CORRECT Hebrew headers
    summary_sheet = wb.create_sheet("סיכום")
    summary_headers = [
        "שורת מקור",           # A - Source Row
        "שם המוצר",            # B - Product Name
        "Model ID",            # C - Model ID  
        "מחיר מקורי",          # D - Original Price
        "סה\"כ ספקים",         # E - Total Vendors
        "מחיר מינימלי",        # F - Min Price
        "מחיר מקסימלי",        # G - Max Price
        "מחיר ממוצע",          # H - Average Price
        "חיסכון מקסימלי",      # I - Maximum Savings
        "שיטת חיפוש",          # J - Search Method
        "זמן עיבוד"            # K - Processing Time
    ]
    
    # Style summary headers
    for col, header in enumerate(summary_headers, 1):
        cell = summary_sheet.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")
    
    # Fill data
    for result in results:
        line_num = result['line_number']
        product_name = result['product_name']
        original_price = result['original_price']
        vendors = result['vendors']
        processing_time = result['processing_time']
        model_url = result.get('model_url', '')
        
        # Extract Model ID from URL
        model_id = ""
        if 'modelid=' in model_url:
            import re
            match = re.search(r'modelid=(\d+)', model_url)
            if match:
                model_id = match.group(1)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if vendors:
            # Details sheet - one row per vendor with PROPER FORMATTING
            for i, vendor in enumerate(vendors, 2):  # Start from row 2
                if vendor['vendor_price'] > 0:
                    price_diff = vendor['vendor_price'] - original_price
                    price_diff_pct = (price_diff / original_price * 100) if original_price > 0 else 0
                    
                    # Format prices with ₪ symbol
                    formatted_original = f"₪{original_price:,.1f}"
                    formatted_vendor = f"₪{vendor['vendor_price']:,}"
                    formatted_diff = f"₪{price_diff:,.1f}"
                    
                    details_sheet.append([
                        str(line_num),              # שורת מקור
                        product_name,               # שם מוצר
                        formatted_original,         # מחיר
                        vendor['vendor_name'],      # שם ספק
                        vendor.get('vendor_product_name', 'Unknown Product'),  # שם מוצר באתר הספק
                        formatted_vendor,           # מחיר ZAP
                        formatted_diff,             # הפרש מחיר
                        f"{price_diff_pct:.1f}%",   # % הפרש
                        vendor.get('button_text', 'לפרטים נוספים'),  # טקסט הכפתור
                        vendor['vendor_url'],       # קישור
                        timestamp,                  # זמן עדכון
                        model_id,                   # Model ID
                        "Breakthrough - Dropdown"   # Method Used
                    ])
            
            # Summary sheet - one row per product with PROPER FORMATTING
            valid_prices = [v['vendor_price'] for v in vendors if v['vendor_price'] > 0]
            if valid_prices:
                min_price = min(valid_prices)
                max_price = max(valid_prices)
                avg_price = sum(valid_prices) / len(valid_prices)
                max_savings = original_price - min_price
            else:
                min_price = max_price = avg_price = max_savings = 0
            
            summary_sheet.append([
                str(line_num),                  # שורת מקור
                product_name,                   # שם המוצר
                model_id,                       # Model ID
                f"₪{original_price:,.1f}",     # מחיר מקורי
                str(len(vendors)),              # סה"כ ספקים
                f"₪{min_price:,}",             # מחיר מינימלי
                f"₪{max_price:,}",             # מחיר מקסימלי
                f"₪{avg_price:,.0f}",          # מחיר ממוצע
                f"₪{max_savings:,.1f}",        # חיסכון מקסימלי
                "Breakthrough - Dropdown",      # שיטת חיפוש
                f"{processing_time:.1f}s"       # זמן עיבוד
            ])
        else:
            # No vendors found
            summary_sheet.append([
                str(line_num), product_name, model_id, f"₪{original_price:,.1f}", 
                "0", "₪0", "₪0", "₪0", "₪0", "Failed", f"{processing_time:.1f}s"
            ])
    
    # Auto-adjust column widths
    for sheet in [details_sheet, summary_sheet]:
        for column in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Save file
    wb.save(filename)
    print(f"📊 Excel file saved: {filename}")
    return filename

def main():
    """Main function with unified processing."""
    global HEADLESS_MODE
    
    parser = argparse.ArgumentParser(description='Production Universal Product Scraper - UNIFIED VERSION')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('lines', nargs='+', type=int, help='Line numbers to process')
    
    args = parser.parse_args()
    
    HEADLESS_MODE = args.headless
    target_lines = args.lines
    
    print("🚀 UNIFIED PRODUCTION SCRAPER")
    print("="*70)
    print(f"📋 Processing Lines: {target_lines}")
    print(f"🤖 Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
    print("="*70)
    
    # Read source data
    try:
        reader = SourceExcelReader(start_row=2)
        products = reader.read_products('data/SOURCE.xlsx')
        print(f"✅ Loaded {len(products)} products from source")
    except Exception as e:
        print(f"❌ Failed to read source data: {e}")
        return
    
    # Process specified lines - NOW USING EXCEL ROW NUMBERS DIRECTLY
    results = []
    for line_num in target_lines:
        # Find product with matching Excel row number
        product_found = None
        for product in products:
            if product.row_number == line_num:
                product_found = product
                break
        
        if product_found:
            result = process_single_product(
                product_found.name, 
                product_found.original_price, 
                line_num
            )
            results.append(result)
        else:
            print(f"❌ Excel row {line_num} not found in source data (might be empty or header row)")
    
    # Create Excel output
    if results:
        excel_file = create_excel_file(results)
        
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"   Lines processed: {len(results)}")
        print(f"   Mode: {'HEADLESS' if HEADLESS_MODE else 'VISIBLE'}")
        print(f"   Excel file: {excel_file}")
        
        # Show key statistics
        total_vendors = sum(len(r['vendors']) for r in results)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"   Total vendors: {total_vendors}")
        print(f"   Avg processing time: {avg_processing_time:.1f}s")
        
        return excel_file
    
    return None

if __name__ == "__main__":
    main()