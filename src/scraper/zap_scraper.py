"""
ZAP Scraper for Universal Product Scraper.

Real implementation for scraping product prices from zap.co.il.
"""

import time
import re
import os
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException
)

from src.models.data_models import (
    ProductInput, 
    VendorOffer, 
    ProductScrapingResult,
    ScraperConfig
)
from src.hebrew.text_processor import HebrewTextProcessor
from src.parsers.product_parser import ProductParser
from src.utils.logger import get_logger
from src.utils.performance_optimizer import PerformanceOptimizer
from src.utils.exceptions import (
    WebDriverException as CustomWebDriverException,
    ProductNotFoundException,
    RateLimitException
)


logger = get_logger(__name__)

def get_vendor_logger():
    """Get vendor processing logger (ensures it's available when needed)."""
    return get_logger("vendor_processing")


class ZapScraper:
    """Real ZAP.co.il web scraper implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ZAP scraper with configuration."""
        self.config = ScraperConfig.from_dict(config)
        self.driver = None
        self.hebrew_processor = HebrewTextProcessor()
        self.product_parser = ProductParser()
        self.is_initialized = False
        
        # Initialize performance optimizer
        self.performance_optimizer = PerformanceOptimizer()
        logger.info("Performance optimizer initialized")
        
    def initialize(self) -> bool:
        """Initialize the WebDriver and configure settings.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self.is_initialized:
            logger.warning("Scraper already initialized")
            return True
            
        try:
            logger.info("Initializing ZAP scraper...")
            
            # Chrome options with performance optimizations
            options = webdriver.ChromeOptions()
            
            # Get performance-optimized browser settings
            browser_optimizations = self.performance_optimizer.optimize_browser_settings()
            
            # Apply headless mode if configured
            if getattr(self.config, 'headless', False):
                options.add_argument('--headless=new')
                
                # Apply performance optimizations for headless mode
                for optimization in browser_optimizations['memory_optimization']:
                    options.add_argument(optimization)
                for optimization in browser_optimizations['performance_optimization']:
                    options.add_argument(optimization)
                
                # Additional aggressive optimizations if memory usage is high
                if 'aggressive_memory' in browser_optimizations:
                    for optimization in browser_optimizations['aggressive_memory']:
                        options.add_argument(optimization)
                
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
                options.add_argument('--disable-images')
                options.add_argument('--disable-javascript-harmony-shipping')
                options.add_argument('--disable-client-side-phishing-detection')
                options.add_argument('--disable-ipc-flooding-protection')
                # Stealth options to avoid bot detection
                options.add_experimental_option("useAutomationExtension", False)
                options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                logger.info("Running in HEADLESS mode with performance optimizations")
            elif getattr(self.config, 'minimize', False):
                options.add_argument('--start-minimized')
                # Apply basic memory optimizations for minimized mode
                for optimization in browser_optimizations['memory_optimization']:
                    options.add_argument(optimization)
                logger.info("Running in MINIMIZED mode with memory optimizations")
            else:
                # Even in explicit mode, apply basic optimizations
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                logger.info("Running in EXPLICIT mode (visible browser)")
            
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Disable popups and notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Enhanced ChromeDriver setup with fallback options
            try:
                logger.info("Attempting ChromeDriver setup via webdriver-manager...")
                driver_path = ChromeDriverManager().install()
                # Fix the path to point to the actual executable
                driver_dir = os.path.dirname(driver_path)
                chromedriver_path = os.path.join(driver_dir, "chromedriver.exe")
                
                # Initialize driver with Service
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ ChromeDriver initialized via webdriver-manager")
                
            except Exception as wdm_error:
                logger.warning(f"WebDriver Manager failed: {wdm_error}")
                logger.info("Attempting fallback ChromeDriver initialization...")
                
                try:
                    # Fallback 1: Try without specifying chromedriver path (use system PATH)
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("✅ ChromeDriver initialized via system PATH")
                    
                except Exception as system_error:
                    logger.warning(f"System PATH ChromeDriver failed: {system_error}")
                    
                    try:
                        # Fallback 2: Try with specific Chrome binary path
                        chrome_binary_paths = [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                        ]
                        
                        for chrome_path in chrome_binary_paths:
                            if os.path.exists(chrome_path):
                                options.binary_location = chrome_path
                                logger.info(f"Trying Chrome binary: {chrome_path}")
                                self.driver = webdriver.Chrome(options=options)
                                logger.info("✅ ChromeDriver initialized with explicit Chrome binary")
                                break
                        else:
                            raise Exception("No Chrome binary found")
                            
                    except Exception as binary_error:
                        logger.error(f"All ChromeDriver initialization methods failed")
                        logger.error(f"WebDriver Manager: {wdm_error}")
                        logger.error(f"System PATH: {system_error}")
                        logger.error(f"Binary Path: {binary_error}")
                        raise Exception(f"ChromeDriver initialization failed: {binary_error}")
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.is_initialized = True
            logger.info("ZAP scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            self.is_initialized = False
            return False
    
    def close(self) -> None:
        """Close the WebDriver and cleanup performance monitoring resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
        
        # Force cleanup of performance optimizer resources
        if hasattr(self, 'performance_optimizer'):
            self.performance_optimizer.force_cleanup()
            
        self.is_initialized = False
    
    def get_chunking_recommendation(self, remaining_products: int) -> Dict[str, Any]:
        """Get chunking recommendation for optimal performance."""
        return self.performance_optimizer.should_chunk_processing(remaining_products)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        return self.performance_optimizer.get_performance_summary()
    
    def scrape_product(self, product: ProductInput) -> ProductScrapingResult:
        """Scrape a single product from ZAP using DUAL APPROACH STRATEGY."""
        logger.info(f"🚀 DUAL APPROACH SCRAPING: {product.name}")
        
        try:
            # STRATEGY 1: USE PRODUCTION SCRAPER METHOD DIRECTLY
            # Import and use the EXACT working function from production_scraper.py
            import sys
            import importlib.util
            from pathlib import Path
            
            # Add production_scraper.py to path
            prod_path = Path(__file__).parent.parent.parent / "production_scraper.py"
            if prod_path.exists():
                spec = importlib.util.spec_from_file_location("production_scraper", prod_path)
                production_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(production_module)
                
                logger.info(f"🎯 Using EXACT Production Scraper Breakthrough Method")
                search_method, model_id, final_url = production_module.search_product_breakthrough(self.driver, product.name)
                
                breakthrough_result = {
                    'success': search_method != "failed",
                    'method_used': f'Production Method ({search_method})',
                    'url': final_url,
                    'model_id': model_id
                }
            else:
                # Fallback to internal method if production_scraper.py not found
                logger.warning("⚠️ production_scraper.py not found, using internal method")
                breakthrough_result = self._search_product_breakthrough_method(product.name)
            
            if breakthrough_result.get('success', False):
                # Breakthrough approach found valid URL - scrape from that URL  
                validated_url = breakthrough_result.get('url')
                method_used = breakthrough_result.get('method_used', 'Breakthrough Method')
                
                logger.info(f"✅ Breakthrough approach successful using {method_used}")
                logger.info(f"🔗 Scraping from validated URL: {validated_url}")
                
                # Use existing working scraper logic to process the validated URL
                result = self._scrape_from_validated_url(product, validated_url, breakthrough_result)
                if result and result.status == "success":
                    # Add breakthrough URLs to the result for Excel summary
                    result.option1_url = breakthrough_result.get('url', '')
                    result.model_id = breakthrough_result.get('model_id', '')
                    result.listing_count = len(breakthrough_result.get('listings', []))
                    result.method_used = method_used
                    
                    logger.info(f"✅ Breakthrough approach scraping successful: {len(result.vendor_offers)} vendors")
                    logger.info(f"🔗 Breakthrough URL: {result.option1_url}")
                    return result
                
                logger.warning("❌ Breakthrough approach validation succeeded but scraping failed")
            else:
                logger.warning(f"❌ Breakthrough approach failed: {breakthrough_result.get('failure_reason', 'Unknown')}")
                
                # Generate failure result with dual approach metadata
                from ..excel.target_writer import TargetExcelWriter
                excel_writer = TargetExcelWriter()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                failure_filename = f"output/DUAL_APPROACH_FAILURE_{timestamp}.xlsx"
                excel_writer.write_failure_results(product, breakthrough_result, failure_filename)
                
                logger.info(f"📁 Failure Excel generated: {failure_filename}")
                
                # Create failure result but include any discovered model_id for statistics
                failure_result = ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="dual_approach_failed",
                    error_message=f"Dual approach validation failed: {breakthrough_result.get('failure_reason', 'Unknown')}"
                )
                
                # Add model_id even if approach failed (for statistics)
                failure_result.model_id = breakthrough_result.get('model_id', '')
                failure_result.option1_url = breakthrough_result.get('url', '')
                
                # Don't return yet - try fallback strategies
                # return failure_result
            
            # If dual approach failed, try fallback strategies
            # STRATEGY 2: Smart keyword search with variant detection  
            logger.info(f"🔍 Smart search strategy for: {product.name}")
            result = self._scrape_smart_search(product)
            if result and result.status == "success":
                logger.info(f"✅ Smart search successful: {len(result.vendor_offers)} vendors")
                return result
                
            # STRATEGY 3: Fallback to original search method
            logger.info(f"🔄 Falling back to original search method")
            result = self._scrape_original_method(product)
            if result:
                return result
            
            # If all strategies failed, return the dual approach failure result
            if 'failure_result' in locals():
                return failure_result
            else:
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="error",
                    error_message="All scraping strategies failed"
                )
            
        except Exception as e:
            logger.error(f"Error in hybrid scraping {product.name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )

    def _scrape_from_validated_url(self, product: ProductInput, validated_url: str, dual_result: Dict[str, Any]) -> ProductScrapingResult:
        """
        SIMPLIFIED: Scrape vendors from dual-approach validated URL using EXISTING WORKING METHODS.
        
        INHERITANCE: Uses existing working vendor extraction methods instead of reinventing.
        """
        logger.info(f"🔗 Scraping from dual-approach validated URL: {validated_url}")
        
        try:
            # Navigate to the validated URL
            self.driver.get(validated_url)
            time.sleep(8)  # Wait for page load
            
            # Check URL type and use appropriate extraction method
            method_used = dual_result.get('method_used', '')
            
            if 'Search' in method_used:
                # This is a search results page - extract vendors from search results ONLY
                logger.info("🔍 Extracting vendors from search results page (validated by dual approach)")
                vendor_offers = self._extract_vendors_from_search_results(product)
                
                if vendor_offers:
                    logger.info(f"✅ Successfully extracted {len(vendor_offers)} vendor offers from search results")
                    return ProductScrapingResult(
                        input_product=product,
                        vendor_offers=vendor_offers,
                        status="success"
                    )
                else:
                    logger.warning("⚠️ No vendor offers found in search results")
                    
            else:
                # This is a model page - use existing working method
                logger.info("📊 Using existing working _extract_vendors_from_model_page method")
                vendor_offers = self._extract_vendors_from_model_page(product)
                
                if vendor_offers:
                    logger.info(f"✅ Successfully extracted {len(vendor_offers)} vendor offers from model page")
                    return ProductScrapingResult(
                        input_product=product,
                        vendor_offers=vendor_offers,
                        status="success"
                    )
                
                logger.warning("⚠️ No vendor offers found with any existing working method")
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="no_vendors_found"
                )
                
        except Exception as e:
            logger.error(f"Error scraping from validated URL {validated_url}: {e}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=f"Error scraping validated URL: {str(e)}"
            )

    def _extract_vendors_from_search_results(self, product: ProductInput) -> List[VendorOffer]:
        """
        Extract vendors ONLY from search results section (not ads or related products).
        
        This method specifically targets the main search results and ignores:
        - Advertisement sections at the top
        - Related products
        - Other page elements
        """
        logger.info("🔍 Extracting vendors from search results section only")
        
        try:
            from selenium.webdriver.common.by import By
            import re
            
            vendor_offers = []
            
            # Target search results using DISCOVERED WORKING SELECTORS
            # From debug analysis: SearchResults container with ModelRow items
            search_result_selectors = [
                # PROVEN WORKING: Individual product items from debug
                ".ModelRow",                           # Individual product containers - FOUND IN DEBUG
                "#SearchResults .ModelRow",            # Products within search results container  
                ".search-results .ModelRow",           # Alternative search results selector
                # Fallback selectors
                "#SearchResults div",                  # Any divs in search results
                ".search-results div",                 # Any divs in search results container
                "div[class*='ModelRow']"               # Model row variations
            ]
            
            search_results = []
            for selector in search_result_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.debug(f"Found {len(elements)} elements with selector: {selector}")
                        # Filter out advertisement elements AND duplicates
                        filtered_elements = []
                        seen_texts = set()
                        
                        for elem in elements:
                            try:
                                elem_text = elem.text.strip()
                                elem_html = elem.get_attribute('outerHTML').lower()
                                
                                # Skip if this looks like an advertisement (more specific check)
                                # Only skip if explicitly marked as ad AND doesn't contain elco
                                is_explicit_ad = ('מודעה' in elem_text or 
                                                'sponsored' in elem_html or 
                                                'banner' in elem_html)
                                contains_target_product = 'elco' in elem_text.lower()
                                
                                if is_explicit_ad and not contains_target_product:
                                    logger.debug("Skipping advertisement element (explicit ad without target product)")
                                    continue
                                
                                # Skip if text is too short or duplicate
                                if len(elem_text) < 20:
                                    logger.debug("Skipping element with too short text")
                                    continue
                                
                                # Skip duplicates (same text content)
                                if elem_text in seen_texts:
                                    logger.debug("Skipping duplicate element")
                                    continue
                                
                                # Must contain ELCO and price to be a valid result
                                if 'elco' not in elem_text.lower():
                                    logger.debug("Skipping element without ELCO")
                                    continue
                                
                                if '₪' not in elem_text:
                                    logger.debug("Skipping element without price")
                                    continue
                                
                                # This looks like a valid, unique product
                                filtered_elements.append(elem)
                                seen_texts.add(elem_text)
                                
                            except Exception as e:
                                logger.debug(f"Error filtering element: {e}")
                                continue
                        
                        if filtered_elements:
                            search_results = filtered_elements
                            logger.info(f"✅ Found {len(search_results)} unique, valid search results with selector: {selector}")
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not search_results:
                logger.warning("❌ No search results found")
                return []
            
            # Extract vendor data from each search result
            for idx, result_element in enumerate(search_results):
                try:
                    # Extract product name - ZAP specific patterns
                    product_name = "Unknown Product"
                    result_text = result_element.text
                    
                    # ZAP search results: look for the main product title
                    lines = result_text.split('\n')
                    
                    # Strategy 1: Look for lines with both ELCO and model number
                    for line in lines:
                        line = line.strip()
                        if ('elco' in line.lower() and 'slim' in line.lower() and 
                            ('40/1' in line or '40 /1' in line) and 
                            len(line) > 20 and len(line) < 200):
                            product_name = line
                            break
                    
                    # Strategy 2: Look for manufacturer | product pattern  
                    if product_name == "Unknown Product":
                        for line in lines:
                            line = line.strip()
                            if ('electra' in line.lower() and 'elco' in line.lower() and 
                                '|' in line and len(line) > 20):
                                # Clean up the line (remove extra info)
                                if '|' in line:
                                    parts = line.split('|')
                                    if len(parts) >= 2:
                                        product_name = parts[1].strip()
                                        break
                                else:
                                    product_name = line
                                    break
                    
                    # Strategy 3: Fallback to any line with ELCO (but clean it up)
                    if product_name == "Unknown Product":
                        for line in lines:
                            line = line.strip()
                            if ('elco' in line.lower() and len(line) > 15 and 
                                not line.startswith('ב-') and  # Not vendor info
                                not 'לפרטים' in line):         # Not "more details"
                                # Take first 100 chars to avoid long descriptions
                                product_name = line[:100]
                                break
                    
                    # Extract price - ZAP specific patterns  
                    price = 0.0
                    # ZAP uses format like "₪6,618" or "6,618 ₪"
                    price_patterns = [
                        r'₪\s*([0-9,]+)',           # ₪6,618
                        r'([0-9,]+)\s*₪',           # 6,618 ₪
                        r'(\d{4,})',                # 4+ digit numbers (like 6618)
                    ]
                    
                    for pattern in price_patterns:
                        price_matches = re.findall(pattern, result_text)
                        for match in price_matches:
                            try:
                                clean_price = match.replace(',', '')
                                candidate_price = float(clean_price)
                                # Filter reasonable prices for air conditioners (1000-10000)
                                if 1000 <= candidate_price <= 10000:
                                    price = candidate_price
                                    break
                            except:
                                continue
                        if price > 0:
                            break
                    
                    if price <= 0:
                        logger.debug(f"Skipping result {idx} - no valid price found in: {result_text[:100]}")
                        continue
                    
                    # Extract vendor name - ZAP specific patterns
                    vendor_name = f"ZAP Vendor {idx + 1}"
                    
                    # Look for vendor info patterns in ZAP
                    # Often appears after "ב-" (at/in) 
                    vendor_patterns = [
                        r'ב-\s*([^)(\n]+)',         # ב- vendor name
                        r'לפרטים נוספים\s*ב-\s*([^)(\n]+)',  # more details at vendor
                    ]
                    
                    for pattern in vendor_patterns:
                        vendor_match = re.search(pattern, result_text)
                        if vendor_match:
                            vendor_candidate = vendor_match.group(1).strip()
                            if len(vendor_candidate) < 50:  # Reasonable vendor name length
                                vendor_name = vendor_candidate
                                break
                    
                    # Get vendor URL
                    vendor_url = ""
                    try:
                        link_elem = result_element.find_element(By.CSS_SELECTOR, "a")
                        vendor_url = link_elem.get_attribute('href') or ""
                    except:
                        pass
                    
                    # Create vendor offer
                    offer = VendorOffer(
                        vendor_name=vendor_name,
                        product_name=product_name,
                        price=price,
                        url=vendor_url
                    )
                    
                    vendor_offers.append(offer)
                    logger.debug(f"✅ Extracted: {vendor_name} - ₪{price} - {product_name[:50]}...")
                    
                except Exception as e:
                    logger.debug(f"Failed to extract from search result {idx}: {e}")
                    continue
            
            logger.info(f"📋 Successfully extracted {len(vendor_offers)} vendors from search results")
            return vendor_offers
            
        except Exception as e:
            logger.error(f"Error extracting vendors from search results: {e}")
            return []

    def _scrape_original_method(self, product: ProductInput) -> ProductScrapingResult:
        """Original scraping method as fallback."""
        logger.info(f"Using original scraping method for: {product.name}")
        
        try:
            # Navigate to ZAP
            self._navigate_to_zap()
            
            # Search for product
            self._search_product(product.name)
            
            # Select from dropdown
            selected = self._select_from_dropdown(product.name)
            if not selected:
                logger.warning(f"Could not find exact match for: {product.name} - proceeding anyway")
            
            # Wait for results page
            self._wait_for_page_ready()
            
            # Click comparison button to get to vendor list
            comparison_url = self._click_comparison_button()
            if not comparison_url:
                logger.warning(f"No comparison page found for: {product.name}")
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="no_results"
                )
            
            # Process comparison page to get vendor offers
            vendor_offers = self._process_comparison_page(comparison_url, product)
            
            # Apply delay
            self._apply_delay()
            
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=vendor_offers,
                status="success" if vendor_offers else "no_results"
            )
            
        except TimeoutException as e:
            logger.error(f"Timeout while scraping {product.name}: {e}")
            # Take a screenshot for debugging
            try:
                screenshot_path = f"logs/error_{product.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to: {screenshot_path}")
            except:
                pass
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=f"Timeout: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error scraping product {product.name}: {e}")
            logger.error(f"Current URL: {self.driver.current_url if self.driver else 'No driver'}")
            # Take a screenshot for debugging
            try:
                screenshot_path = f"logs/error_{product.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot saved to: {screenshot_path}")
            except:
                pass
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )

    def _search_product_breakthrough_method(self, product_name: str) -> Dict[str, Any]:
        """
        BREAKTHROUGH SEARCH METHOD copied from production_scraper.py.
        Uses hyphenated-first approach per OPTION_1_DETAILED_FLOW.md.
        
        Args:
            product_name: Product name to search (original format)
            
        Returns:
            Dictionary with success status, method used, URL, and model_id if found
        """
        logger.info(f"🎯 BREAKTHROUGH SEARCH: {product_name}")
        
        try:
            # Navigate to ZAP homepage
            self.driver.get("https://www.zap.co.il")
            time.sleep(3)
            
            # Find search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#acSearch-input"))
            )
            search_box.click()
            time.sleep(1)
            
            # SUB-OPTION 1A: Try HYPHENATED approach FIRST (per OPTION_1_DETAILED_FLOW.md)
            logger.info(f"🔍 SUB-OPTION 1A: Trying HYPHENATED approach first...")
            hyphenated = product_name.replace(" ", "-")
            search_box.clear()
            search_box.send_keys(hyphenated)
            time.sleep(3)
            
            # Check for dropdown and try to select working option
            try:
                dropdown_options = self.driver.find_elements(By.CSS_SELECTOR, ".acSearch-row-container")
                if dropdown_options:
                    logger.info(f"✅ Found {len(dropdown_options)} dropdown options")
                    # Try to find Hebrew description option first
                    for option in dropdown_options:
                        option_text = option.text
                        if "מזגן" in option_text:  # Hebrew product description
                            logger.info(f"🎯 Selecting Hebrew option: {option_text[:50]}")
                            option.click()
                            time.sleep(5)
                            current_url = self.driver.current_url
                            logger.info(f"📍 URL after Hebrew option click: {current_url}")
                            
                            # Check if we landed on model page
                            if "model.aspx?modelid=" in current_url:
                                model_id = current_url.split("modelid=")[1].split("&")[0]
                                logger.info(f"✅ SUB-OPTION 1A SUCCESS: Direct model page - ID {model_id}")
                                return {
                                    'success': True,
                                    'method_used': 'SUB-OPTION 1A (Hyphenated Dropdown)',
                                    'url': current_url,
                                    'model_id': model_id
                                }
                            else:
                                logger.warning(f"⚠️ Hebrew option didn't lead to model page: {current_url}")
                            break
                else:
                    logger.info("⚠️ No dropdown options found - trying Enter key")
                    search_box.send_keys(Keys.ENTER)
                    time.sleep(5)
                    
            except Exception as e:
                logger.warning(f"SUB-OPTION 1A dropdown failed: {e}")
            
            # Check current URL after SUB-OPTION 1A
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL after 1A: {current_url}")
            
            # SUB-OPTION 1B: Fallback to SPACED approach if 1A didn't work
            if "model.aspx?modelid=" not in current_url:
                logger.info(f"🔍 SUB-OPTION 1B: Trying SPACED approach...")
                
                # Go back to homepage for clean search
                self.driver.get("https://www.zap.co.il") 
                time.sleep(2)
                
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#acSearch-input"))
                )
                search_box.click()
                time.sleep(1)
                
                # Use original spaced product name
                search_box.clear()
                search_box.send_keys(product_name)
                search_box.send_keys(Keys.ENTER)
                time.sleep(5)
                
                current_url = self.driver.current_url
                logger.info(f"📍 Current URL after 1B: {current_url}")
            
            # Extract model ID if on model page
            if "model.aspx?modelid=" in current_url:
                model_id = current_url.split("modelid=")[1].split("&")[0] 
                logger.info(f"✅ BREAKTHROUGH SUCCESS: Model ID {model_id}")
                return {
                    'success': True,
                    'method_used': 'Breakthrough Search Method',
                    'url': current_url,
                    'model_id': model_id
                }
            else:
                # Success but no direct model page - use current URL
                logger.info(f"✅ BREAKTHROUGH SUCCESS: Search results page")
                return {
                    'success': True,
                    'method_used': 'Breakthrough Search Method',
                    'url': current_url,
                    'model_id': None
                }
                
        except Exception as e:
            logger.error(f"❌ Breakthrough search failed: {e}")
            return {
                'success': False,
                'method_used': 'Breakthrough Search Method - Failed',
                'url': None,
                'model_id': None,
                'error': str(e)
            }

    def scrape_product_dual_session(self, product: ProductInput) -> ProductScrapingResult:
        """Scrape product using dual-session approach: P1-only vs P1→P2, then choose best results."""
        logger.info(f"🔄 DUAL-SESSION SCRAPING: {product.name}")
        
        session_a_driver = None
        session_b_driver = None
        
        try:
            # Initialize two separate WebDriver sessions
            session_a_driver = self._create_new_driver()
            session_b_driver = self._create_new_driver()
            
            logger.info("🅰️ Starting Session A (P1 only - direct Enter)")
            logger.info("🅱️ Starting Session B (P1→P2 - dropdown selection)")
            
            # Run sessions SEQUENTIALLY to avoid ZAP rate limiting
            logger.info("🏃 Starting Session A execution (P1-only)...")
            try:
                session_a_results = self._run_session_p1_only(session_a_driver, product)
                logger.info("✅ Session A completed successfully")
            except Exception as e:
                logger.error(f"❌ Session A failed: {e}")
                session_a_results = {'listing_names': [], 'comparison_url': None, 'vendor_offers': []}
            
            # Small delay between sessions to prevent ZAP rate limiting
            logger.info("⏸️ Brief pause between sessions...")
            time.sleep(3)
            
            logger.info("🏃 Starting Session B execution (P1→P2)...")
            try:
                session_b_results = self._run_session_p1_p2(session_b_driver, product)
                logger.info("✅ Session B completed successfully")
            except Exception as e:
                logger.error(f"❌ Session B failed: {e}")
                session_b_results = {'listing_names': [], 'comparison_url': None, 'vendor_offers': []}
            
            # Compare results and choose the best session
            best_session = self._compare_session_results(product.name, session_a_results, session_b_results)
            
            logger.info(f"🏆 WINNER: Session {best_session['session']} (score: {best_session['score']:.2f})")
            
            return best_session['result']
            
        except Exception as e:
            logger.error(f"Error in dual-session scraping: {e}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )
        finally:
            # Clean up both sessions with detailed logging
            logger.info("🧹 CLEANING UP DUAL-SESSION BROWSERS")
            try:
                if session_a_driver:
                    logger.info("🅰️ Closing Session A browser...")
                    session_a_driver.quit()
                    logger.info("✅ Session A browser closed")
                else:
                    logger.warning("⚠️ Session A driver was None")
            except Exception as cleanup_error:
                logger.error(f"❌ Error closing Session A: {cleanup_error}")
                # Force kill if quit() fails
                try:
                    session_a_driver.close()
                except:
                    pass
                    
            try:
                if session_b_driver:
                    logger.info("🅱️ Closing Session B browser...")
                    session_b_driver.quit()
                    logger.info("✅ Session B browser closed")
                else:
                    logger.warning("⚠️ Session B driver was None")
            except Exception as cleanup_error:
                logger.error(f"❌ Error closing Session B: {cleanup_error}")
                # Force kill if quit() fails
                try:
                    session_b_driver.close()
                except:
                    pass
                    
            logger.info("🏁 Dual-session cleanup completed")
    
    def scrape_batch(self, products: List[ProductInput]) -> List[ProductScrapingResult]:
        """Scrape multiple products with performance monitoring."""
        logger.info(f"Starting batch scrape of {len(products)} products")
        
        # Start performance monitoring
        self.performance_optimizer.start_monitoring()
        results = []
        
        for i, product in enumerate(products):
            logger.info(f"Processing product {i+1}/{len(products)}: {product.name}")
            
            # Check memory usage before processing
            memory_status = self.performance_optimizer.check_memory_usage()
            if memory_status['needs_restart']:
                logger.warning(f"Memory usage high ({memory_status['memory_mb']}MB) - consider restarting browser")
            
            try:
                product_start_time = time.time()
                result = self.scrape_product(product)
                product_processing_time = time.time() - product_start_time
                
                # Count vendor timeouts for this product
                vendor_timeout_count = 0  # This would be tracked in vendor processing
                
                # Record product completion
                vendor_count = len(result.vendor_offers) if result.vendor_offers else 0
                self.performance_optimizer.record_product_completion(
                    product_processing_time, vendor_count, vendor_timeout_count
                )
                
                results.append(result)
                
                # Log summary with performance info
                if result.vendor_offers:
                    logger.info(f"  Found {len(result.vendor_offers)} vendors in {product_processing_time:.1f}s")
                else:
                    logger.warning(f"  No vendors found")
                
                # Log performance summary every 5 products
                if (i + 1) % 5 == 0:
                    perf_summary = self.performance_optimizer.get_performance_summary()
                    logger.info(f"Performance summary after {i+1} products: "
                              f"{perf_summary['avg_time_per_product_min']:.1f}min/product, "
                              f"{perf_summary['memory_usage_mb']:.1f}MB memory")
                    
            except Exception as e:
                logger.error(f"Failed to scrape product {product.name}: {e}")
                results.append(ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="error",
                    error_message=str(e)
                ))
        
        # Final performance summary
        final_summary = self.performance_optimizer.get_performance_summary()
        logger.info(f"Batch scraping complete. Success rate: "
                   f"{sum(1 for r in results if r.status == 'success')}/{len(results)}")
        logger.info(f"Performance summary: {final_summary['avg_time_per_product_min']:.1f}min/product, "
                   f"{final_summary['memory_usage_mb']:.1f}MB memory, "
                   f"{final_summary['vendor_success_rate']:.1f}% vendor success rate")
        
        return results
    
    def _navigate_to_zap(self) -> None:
        """Navigate to ZAP homepage."""
        logger.debug("Navigating to ZAP...")
        self.driver.get("https://www.zap.co.il/")
        self._wait_for_page_ready()
        self._close_popups()
    
    def _search_product(self, product_name: str) -> None:
        """Search for a product on ZAP."""
        logger.info(f"🔍 SEARCHING FOR ORIGINAL PRODUCT: '{product_name}'")
        
        try:
            # Wait for page to fully load - longer wait for headless mode
            if getattr(self.config, 'headless', False):
                time.sleep(8)  # Longer wait for headless
                logger.info("Extended wait for headless mode page load")
            else:
                time.sleep(3)
            
            # Debug: Log current URL and check if we're on the right page
            logger.info(f"Current URL before search: {self.driver.current_url}")
            
            # Scroll to top first to ensure search box is visible
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Find search box - try multiple selectors with extended list for headless compatibility
            search_box = None
            search_selectors = [
                "input[type='search']",
                "input[type='text']",
                "input[placeholder*='חיפוש']",
                "input[placeholder*='חפש']", 
                "input.search-input",
                "input#search",
                "input[name='search']",
                "input[class*='search']",
                "input[id*='search']",
                "textarea[placeholder*='חיפוש']",
                "#searchbox input",
                ".search-container input",
                "form input[type='text']"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found search box with selector: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                # Debug: Log available input elements
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.warning(f"Available input elements: {len(all_inputs)}")
                    for i, inp in enumerate(all_inputs[:5]):  # Log first 5
                        logger.warning(f"Input {i}: type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}, id={inp.get_attribute('id')}")
                except Exception as e:
                    logger.warning(f"Could not log input elements: {e}")
                
                # Fallback: Try to navigate directly to search results page
                logger.warning("Search box not found, trying direct search URL...")
                self._fallback_search(product_name)
                return
            
            if not search_box:
                raise NoSuchElementException("Could not find search box")
            
            # Click to focus
            search_box.click()
            time.sleep(0.5)
            
            # 🎯 HYPHENATED-FIRST APPROACH (Fix for Tornado issue)
            logger.info(f"🔍 SUB-OPTION 1A: Trying HYPHENATED approach first...")
            hyphenated = product_name.replace(" ", "-")
            logger.info(f"🔧 DEBUG: Original: {repr(product_name)}")
            logger.info(f"🔧 DEBUG: Hyphenated: {repr(hyphenated)}")
            
            # Clear and enter HYPHENATED search term
            search_box.clear()
            logger.info(f"💬 TYPING HYPHENATED INTO SEARCH BOX: '{hyphenated}'")
            search_box.send_keys(hyphenated)
            logger.info(f"🔧 DEBUG: Sent to search box: {repr(hyphenated)}")
            
            # Check what's actually in the search box after typing
            actual_value = search_box.get_attribute('value')
            logger.info(f"📝 SEARCH BOX CONTAINS: '{actual_value}'")
            
            time.sleep(5)  # Extended wait for dropdown (was 1.5)
            
            # 🔧 WORKING DROPDOWN SELECTION LOGIC (from production_scraper.py)
            # Try to select from dropdown using the PROVEN working method
            hyphenated_success = self._try_working_dropdown_selection(hyphenated, product_name)
            
            if hyphenated_success:
                logger.info(f"✅ SUB-OPTION 1A: Hyphenated dropdown selection successful")
                return  # Exit successfully - no need for fallback
            else:
                logger.info(f"⚠️ SUB-OPTION 1A: Dropdown selection failed - trying SUB-OPTION 1B fallback")
            
        except Exception as e:
            logger.error(f"Error searching for product: {e}")
            raise
    
    def _fallback_search(self, product_name: str) -> None:
        """Fallback search method using direct URL navigation."""
        try:
            import urllib.parse
            
            # Clean the product name for URL encoding
            search_term = product_name.strip()
            encoded_term = urllib.parse.quote(search_term)
            
            # Try ZAP's search URL format
            search_url = f"https://www.zap.co.il/search.aspx?keyword={encoded_term}"
            logger.info(f"Trying fallback search URL: {search_url}")
            
            self.driver.get(search_url)
            time.sleep(5)  # Wait for page to load
            
            logger.info("Fallback search completed")
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            raise
    
    def _try_working_dropdown_selection(self, hyphenated_search: str, original_product: str) -> bool:
        """Working dropdown selection logic ported from production_scraper.py"""
        try:
            logger.info(f"🔍 Trying working dropdown selection for hyphenated search: {hyphenated_search}")
            
            # Try multiple selectors for dropdown detection
            dropdown_containers = self.driver.find_elements(By.CSS_SELECTOR, ".acSearch-row-container")
            if not dropdown_containers:
                logger.info(f"🔧 Primary selector failed, trying backup selectors...")
                dropdown_containers = self.driver.find_elements(By.CSS_SELECTOR, "[class*='acSearch'], [class*='dropdown'], [class*='suggestion']")
            
            logger.info(f"🔧 Found {len(dropdown_containers)} dropdown containers")
            
            if not dropdown_containers:
                logger.info(f"❌ No dropdown containers found")
                return False
                
            # Select best match using documented scoring system
            best_option = None
            best_score = 0
            
            logger.info(f"🔍 DROPDOWN INVESTIGATION - Using DOCUMENTED SCORING SYSTEM:")
            
            # Parse target product components 
            target_components = self._parse_target_product_components(original_product)
            logger.info(f"   Target: Manufacturer='{target_components['manufacturer']}', Series={target_components['series']}, Model='{target_components['model']}'")
            
            for i, container in enumerate(dropdown_containers, 1):
                text = container.text.strip()
                logger.info(f"   Option {i}: '{text}'")
                
                # Apply documented scoring system
                score = self._calculate_documented_score(text, target_components)
                logger.info(f"      Documented Score: {score:.1f}/10.0")
                
                if score > best_score:
                    best_score = score
                    best_option = container
            
            if best_option and best_score > 0:
                selected_text = best_option.text.strip()
                logger.info(f"✅ SELECTED OPTION (Score {best_score:.1f}): '{selected_text}'")
                logger.info(f"🔧 DEBUG: Clicking dropdown option...")
                best_option.click()
                time.sleep(7)  # Increased wait time for page load
                
                # Check if we reached a successful page
                current_url = self.driver.current_url
                logger.info(f"📍 Current URL after dropdown click: {current_url}")
                
                # Check for success indicators
                if "model.aspx?modelid=" in current_url:
                    logger.info(f"✅ DROPDOWN SUCCESS: Direct model page reached")
                    return True
                elif "models.aspx" in current_url:
                    # Check if there are actual product listings
                    vendor_check = self.driver.find_elements(By.CSS_SELECTOR, ".compare-item-row.product-item, .noModelRow.ModelRow")
                    if len(vendor_check) > 0:
                        logger.info(f"✅ DROPDOWN SUCCESS: Found {len(vendor_check)} results")
                        return True
                    
                # Check for "no results" indicators
                no_results_indicators = [
                    "לא נמצאו תוצאות",
                    "no results", 
                    "search.aspx?keyword="
                ]
                
                page_source = self.driver.page_source.lower()
                if any(indicator in page_source for indicator in no_results_indicators):
                    logger.info(f"⚠️ DROPDOWN: No results found with selected option")
                    return False
                else:
                    logger.info(f"✅ DROPDOWN: Results found, considering successful")
                    return True
                    
            else:
                logger.info(f"❌ No suitable dropdown option found (best score: {best_score:.1f})")
                return False
                
        except Exception as e:
            logger.error(f"Error in working dropdown selection: {e}")
            return False
    
    def _parse_target_product_components(self, product_name: str) -> dict:
        """Parse target product components (OPTION_1_DETAILED_FLOW.md Phase 2.3)"""
        import re
        
        # Extract model number using documented regex
        model_match = re.search(r'(\d+(?:\/\d+[A-Z]*)?)', product_name)
        model_number = model_match.group(1) if model_match else ""
        
        # Extract manufacturer (first word)
        words = product_name.split()
        manufacturer = words[0] if words else ""
        
        # Extract series words (everything except manufacturer and model)
        series_words = []
        for word in words[1:]:  # Skip manufacturer
            if word != model_number and not re.match(r'^\d+(?:\/\d+[A-Z]*)?$', word):
                series_words.append(word.upper())
        
        return {
            'manufacturer': manufacturer.upper(),
            'series': series_words,
            'model': model_number
        }

    def _calculate_documented_score(self, product_text: str, target_components: dict) -> float:
        """Calculate score using DOCUMENTED SCORING SYSTEM (OPTION_1_DETAILED_FLOW.md Phase 4)"""
        
        # PHASE 3: CRITICAL GATES FIRST
        
        # STEP 1: Model Number Gate (Phase 3.1.2)
        import re
        text_model_match = re.search(r'(\d+(?:\/\d+[A-Z]*)?)', product_text)
        text_model = text_model_match.group(1) if text_model_match else ""
        
        if text_model != target_components['model']:
            logger.info(f"      ❌ MODEL NUMBER GATE FAILED: '{text_model}' ≠ '{target_components['model']}'")
            return 0.0  # DISQUALIFIED
        
        logger.info(f"      ✅ Model Number Gate PASSED: '{text_model}'")
        
        # STEP 2: Product Type Gate (Phase 3.1.3)
        target_has_inv = any(word in ['INV', 'INVERTER'] for word in target_components['series'])
        text_has_inv = 'INV' in product_text.upper() or 'INVERTER' in product_text.upper()
        
        if target_has_inv and not text_has_inv:
            logger.info(f"      ❌ PRODUCT TYPE GATE FAILED: Target has INV but text missing INV/INVERTER")
            return 0.0  # DISQUALIFIED
        
        if target_has_inv:
            logger.info(f"      ✅ Product Type Gate PASSED: Both have INV/INVERTER")
        
        # PHASE 4: COMPONENT SCORING (after passing gates)
        total_score = 0.0
        
        # 4.1.1: Manufacturer Scoring (0-1.0 points = 10%)
        text_upper = product_text.upper()
        if target_components['manufacturer'] in text_upper:
            manufacturer_score = 1.0
            logger.info(f"      ✅ Manufacturer: +1.0 (exact match)")
        else:
            manufacturer_score = 0.0
            logger.info(f"      ❌ Manufacturer: +0.0 (no match)")
        
        total_score += manufacturer_score
        
        # 4.1.2: Model Name Scoring (0-4.0 points = 40%)
        if target_components['series']:
            series_matches = 0
            for word in target_components['series']:
                if word in text_upper or (word == 'INV' and 'INVERTER' in text_upper):
                    series_matches += 1
            
            series_percentage = series_matches / len(target_components['series'])
            series_score = series_percentage * 4.0
            logger.info(f"      ✅ Series: +{series_score:.1f} ({series_matches}/{len(target_components['series'])} = {series_percentage:.1%})")
        else:
            series_score = 4.0  # No series words to match
            logger.info(f"      ✅ Series: +4.0 (no series words to match)")
        
        total_score += series_score
        
        # 4.1.3: Model Number Scoring (0-5.0 points = 50%)
        model_score = 5.0  # Already passed gate, so gets full points
        logger.info(f"      ✅ Model: +5.0 (passed gate)")
        total_score += model_score
        
        # 4.1.4: Extra Words Penalty (minor)
        text_words = product_text.upper().split()
        target_words = [target_components['manufacturer']] + target_components['series'] + [target_components['model']]
        extra_words = [word for word in text_words if not any(target in word for target in target_words)]
        extra_penalty = len(extra_words) * 0.1
        
        if extra_penalty > 0:
            logger.info(f"      ⚠️ Extra words penalty: -{extra_penalty:.1f}")
        
        final_score = total_score - extra_penalty
        return max(0.0, final_score)  # Don't go below 0
    
    def _select_from_dropdown(self, product_name: str) -> bool:
        """Select best match from search dropdown for any product string."""
        logger.debug(f"Selecting from dropdown for: {product_name}")
        
        try:
            # ENHANCED DROPDOWN SEARCH (2025-08-05)
            # Use improved algorithm that handles current ZAP dropdown structure
            return self._enhanced_dropdown_search(product_name)
            
        except Exception as e:
            logger.error(f"Enhanced dropdown search failed: {e}")
            # Fall back to original method
            return self._original_select_from_dropdown(product_name)
    
    def _enhanced_dropdown_search(self, product_name: str) -> bool:
        """Enhanced dropdown search algorithm for current ZAP interface."""
        logger.info(f"🔍 Enhanced dropdown search for: {product_name}")
        
        try:
            # Wait longer for dropdown to stabilize
            time.sleep(3)
            
            # Extract key terms for matching
            key_terms = self._extract_key_search_terms(product_name)
            logger.info(f"Key terms extracted: {key_terms}")
            
            # Try multiple dropdown detection strategies
            dropdown_items = []
            
            # Modern ZAP dropdown selectors (based on 2025 interface)
            modern_selectors = [
                "div[role='option']",
                "li[role='option']",
                "[data-testid*='suggestion']",
                "[class*='suggestion']",
                "[class*='autocomplete']",
                "div[class*='dropdown'] a",
                "ul[class*='suggestions'] li",
                "div[onclick*='product']",
                "[href*='models.aspx']"  # ZAP product links
            ]
            
            for selector in modern_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        logger.info(f"✅ Found {len(items)} items with selector: {selector}")
                        for item in items:
                            text = item.text.strip()
                            if text and len(text) > 2:
                                dropdown_items.append({
                                    'element': item,
                                    'text': text,
                                    'selector': selector
                                })
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # XPath patterns for dynamic content
            xpath_patterns = [
                "//div[contains(text(), 'INV') or contains(text(), 'ISKA') or contains(text(), 'ELECTRA')]",
                "//a[contains(@href, 'product') and (contains(text(), 'INV') or contains(text(), 'ISKA'))]",
                "//li[contains(text(), 'INV') or contains(text(), 'ISKA')]",
                "//*[@onclick and (contains(text(), 'INV') or contains(text(), 'ISKA'))]"
            ]
            
            for xpath in xpath_patterns:
                try:
                    items = self.driver.find_elements(By.XPATH, xpath)
                    if items:
                        logger.info(f"✅ Found {len(items)} items with XPath")
                        for item in items:
                            text = item.text.strip()
                            if text and len(text) > 2:
                                dropdown_items.append({
                                    'element': item,
                                    'text': text,
                                    'selector': f'xpath'
                                })
                except Exception as e:
                    logger.debug(f"XPath {xpath} failed: {e}")
                    continue
            
            # Remove duplicates
            unique_items = {}
            for item in dropdown_items:
                text_key = item['text'].lower().strip()
                if text_key not in unique_items:
                    unique_items[text_key] = item
            
            dropdown_items = list(unique_items.values())
            logger.info(f"Found {len(dropdown_items)} unique dropdown items")
            
            if not dropdown_items:
                logger.warning("No dropdown items found")
                return False
            
            # Score and rank items
            scored_items = []
            for item in dropdown_items:
                score = self._calculate_enhanced_match_score(item['text'], key_terms, product_name)
                if score > 0:
                    scored_items.append({**item, 'score': score})
            
            scored_items.sort(key=lambda x: x['score'], reverse=True)
            
            if scored_items:
                logger.info("Top 3 matches found:")
                for i, item in enumerate(scored_items[:3], 1):
                    logger.info(f"  {i}. {item['text']} (score: {item['score']:.2f})")
            
            # Select best match if score is adequate
            if scored_items and scored_items[0]['score'] >= 2.5:  # Lower threshold for testing
                best_item = scored_items[0]
                logger.info(f"🎯 Selecting: {best_item['text']} (score: {best_item['score']:.2f})")
                
                try:
                    element = best_item['element']
                    
                    # Try multiple click methods
                    try:
                        element.click()
                        time.sleep(2)
                        logger.info("✅ Click successful")
                        return True
                    except:
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                        logger.info("✅ JavaScript click successful")
                        return True
                        
                except Exception as e:
                    logger.error(f"Error clicking dropdown item: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Enhanced dropdown search error: {e}")
            return False
    
    def _extract_key_search_terms(self, product_name: str) -> dict:
        """Extract key terms for enhanced matching."""
        import re
        product_upper = product_name.upper()
        tokens = re.split(r'[\s\-_/\\,\.]+', product_upper)
        
        terms = {
            'all': [t for t in tokens if len(t) > 1],
            'alphanumeric': [],
            'numeric': [],
            'alpha': [],
            'brand': []
        }
        
        brands = ['ISKA', 'ELECTRA', 'TORNADO', 'SMART', 'CLASSIC']
        
        for token in terms['all']:
            if token.isdigit():
                terms['numeric'].append(token)
            elif token.isalpha():
                terms['alpha'].append(token)
                if token in brands:
                    terms['brand'].append(token)
            elif any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
                terms['alphanumeric'].append(token)
        
        return terms
    
    def _calculate_enhanced_match_score(self, item_text: str, key_terms: dict, original_product: str) -> float:
        """Calculate enhanced relevance score."""
        item_upper = item_text.upper()
        original_upper = original_product.upper()
        
        score = 0.0
        
        # Brand match (highest priority)
        for brand in key_terms['brand']:
            if brand in item_upper:
                score += 5.0
        
        # Alphanumeric matches (model numbers)
        for term in key_terms['alphanumeric']:
            if term in item_upper:
                score += 3.0
        
        # Numeric matches
        for term in key_terms['numeric']:
            if term in item_upper:
                score += 2.0
        
        # Alpha matches
        for term in key_terms['alpha']:
            if term in item_upper and term not in key_terms['brand']:
                score += 1.5
        
        # Exact phrase bonus
        if original_upper in item_upper:
            score += 4.0
        
        # Penalty for very long items
        if len(item_text) > 100:
            score -= 1.0
        
        return max(0, score)
    
    def _original_select_from_dropdown(self, product_name: str) -> bool:
        """Original dropdown selection method as fallback."""
        try:
            time.sleep(2.5)
            logger.info("Looking for autocomplete dropdown items...")
            
            dropdown_items = []
            
            # Smart term extraction from product name
            # This will work for any product string
            product_terms = self._extract_significant_terms(product_name)
            
            logger.info(f"Product terms extracted: {product_terms}")
            
            # Try multiple strategies to find dropdown items
            dropdown_items = self._find_dropdown_items(product_terms)
            
            if not dropdown_items:
                logger.warning("No dropdown items found - trying fallback")
                return self._fallback_search()
            
            # Score and select the best matching item
            best_item = self._select_best_match(dropdown_items, product_terms, product_name)
            
            # NEW: Component-based decision logic - should we use bold option vs dropdown?
            component_decision = self._evaluate_bold_vs_dropdown_decision(product_name, best_item)
            logger.info(f"🎯 COMPONENT DECISION: {component_decision['choice']} - {component_decision['reason']}")
            
            # If component analysis says use bold option (P1 results), skip dropdown
            if component_decision['choice'] == 'bold':
                logger.info(f"🔄 COMPONENT ANALYSIS: Using P1 results instead of dropdown")
                return False  # Don't click dropdown, use P1 search results
            
            # Define minimum quality threshold for dropdown matches
            MIN_MATCH_SCORE = 8.0  # Require extremely high match quality - reject poor matches like "Classic 21" for "Classic INV 240"
            
            if best_item and best_item['score'] >= MIN_MATCH_SCORE:
                logger.info(f"✅ Clicking on good match: {best_item['text']} (score: {best_item['score']})")
                
                try:
                    best_item['element'].click()
                except:
                    # If regular click fails, try JavaScript click
                    self.driver.execute_script("arguments[0].click();", best_item['element'])
                
                time.sleep(3)
                return True
            else:
                if best_item:
                    logger.warning(f"❌ REJECTING poor match: '{best_item['text']}' (score: {best_item['score']:.2f}) - threshold: {MIN_MATCH_SCORE}")
                    logger.info(f"🔄 STAYING WITH P1 RESULTS instead of dropdown")
                else:
                    logger.warning("❌ No dropdown matches found - staying with P1 results")
                
                # Don't click dropdown - use original search (P1 results) instead
                logger.info(f"✅ USING P1 SEARCH RESULTS FOR: '{product_name}'")
                return False  # This will use P1 results with original search term
            
        except Exception as e:
            logger.error(f"Error in dropdown selection: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _extract_significant_terms(self, product_name: str) -> dict:
        """Extract significant terms from any product name string."""
        # Convert to uppercase for consistent matching
        product_upper = product_name.upper()
        
        # Split by various delimiters
        import re
        tokens = re.split(r'[\s\-_/\\,\.]+', product_upper)
        
        # Categorize terms
        terms = {
            'all': [],
            'alphanumeric': [],  # Model numbers like "65T", "INV-42"
            'numeric': [],       # Pure numbers like "42", "65"
            'alpha': [],         # Pure letters like "EMD", "SQ"
            'long': []          # Terms longer than 3 characters
        }
        
        for token in tokens:
            if len(token) > 1:  # Skip single characters
                terms['all'].append(token)
                
                if token.isdigit():
                    terms['numeric'].append(token)
                elif token.isalpha():
                    terms['alpha'].append(token)
                    if len(token) > 3:
                        terms['long'].append(token)
                elif any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
                    terms['alphanumeric'].append(token)
        
        # Also keep the original string for exact matching
        terms['original'] = product_name
        terms['original_upper'] = product_upper
        
        return terms
    
    def _find_dropdown_items(self, product_terms: dict) -> list:
        """Find dropdown items using multiple strategies."""
        dropdown_items = []
        found_selectors = set()  # Track which selectors found items
        
        # Strategy 1: Look for anchor tags (most common for dropdown items)
        items = self._find_by_tag_and_terms("a", product_terms)
        if items:
            dropdown_items.extend(items)
            found_selectors.add("anchor_tags")
        
        # Strategy 2: Look for list items
        items = self._find_by_css_selectors([
            "li",
            "[role='option']",
            "[class*='suggestion']",
            "[class*='autocomplete']",
            "[class*='result']"
        ], product_terms)
        if items:
            dropdown_items.extend(items)
            found_selectors.add("list_items")
        
        # Strategy 3: Look for clickable divs
        items = self._find_by_xpath_patterns([
            "//div[@onclick]",
            "//div[@data-href]",
            "//div[contains(@class, 'clickable')]",
            "//span[@onclick]"
        ], product_terms)
        if items:
            dropdown_items.extend(items)
            found_selectors.add("clickable_divs")
        
        # Strategy 4: Find by proximity to search box
        items = self._find_by_proximity_to_search(product_terms)
        if items:
            dropdown_items.extend(items)
            found_selectors.add("proximity_search")
        
        logger.info(f"Found {len(dropdown_items)} items using strategies: {found_selectors}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in dropdown_items:
            elem_id = id(item)
            if elem_id not in seen:
                seen.add(elem_id)
                unique_items.append(item)
        
        return unique_items
    
    def _find_by_tag_and_terms(self, tag: str, product_terms: dict) -> list:
        """Find elements by tag that contain product terms."""
        items = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, tag)
            
            for elem in elements:
                if elem.is_displayed() and elem.text.strip():
                    text = elem.text.strip()
                    text_upper = text.upper()
                    
                    # Check if contains any significant terms
                    if self._matches_product_terms(text_upper, product_terms):
                        # For links, check if it's a product link
                        if tag == "a":
                            href = elem.get_attribute('href')
                            if href and any(pattern in href for pattern in ['model', 'product', 'item']):
                                items.append(elem)
                                logger.debug(f"Found {tag} with href: {text[:50]}...")
                        else:
                            items.append(elem)
                            logger.debug(f"Found {tag}: {text[:50]}...")
        except Exception as e:
            logger.debug(f"Error finding by tag {tag}: {e}")
        
        return items
    
    def _find_by_css_selectors(self, selectors: list, product_terms: dict) -> list:
        """Find elements using CSS selectors that contain product terms."""
        items = []
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    if elem.is_displayed() and elem.text.strip():
                        text_upper = elem.text.strip().upper()
                        
                        if self._matches_product_terms(text_upper, product_terms):
                            items.append(elem)
                            logger.debug(f"Found with selector '{selector}': {elem.text[:50]}...")
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
        
        return items
    
    def _find_by_xpath_patterns(self, patterns: list, product_terms: dict) -> list:
        """Find elements using XPath patterns."""
        items = []
        
        for pattern in patterns:
            try:
                elements = self.driver.find_elements(By.XPATH, pattern)
                
                for elem in elements:
                    if elem.is_displayed() and elem.text.strip():
                        text_upper = elem.text.strip().upper()
                        
                        if self._matches_product_terms(text_upper, product_terms):
                            items.append(elem)
                            logger.debug(f"Found with XPath '{pattern}': {elem.text[:50]}...")
            except Exception as e:
                logger.debug(f"Error with XPath {pattern}: {e}")
        
        return items
    
    def _find_by_proximity_to_search(self, product_terms: dict) -> list:
        """Find elements near the search box that contain product terms."""
        items = []
        
        try:
            search_box = self.driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
            search_box_y = search_box.location['y']
            search_box_x = search_box.location['x']
            
            # Build dynamic XPath based on product terms
            conditions = []
            # Use the most significant terms (alphanumeric and long terms first)
            significant_terms = (product_terms.get('alphanumeric', [])[:2] + 
                               product_terms.get('long', [])[:2] + 
                               product_terms.get('alpha', [])[:2])[:3]
            
            for term in significant_terms:
                conditions.append(f"contains(translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{term}')")
            
            if conditions:
                xpath = f"//*[{' or '.join(conditions)}]"
                elements = self.driver.find_elements(By.XPATH, xpath)
                
                for elem in elements:
                    if elem.is_displayed() and elem != search_box:
                        loc = elem.location
                        # Must be below search box and reasonably close horizontally
                        if (loc['y'] > search_box_y and 
                            abs(loc['x'] - search_box_x) < 500):  # Within 500px horizontally
                            
                            text = elem.text.strip()
                            if text and len(text) > 10:  # Meaningful text
                                items.append(elem)
                                logger.debug(f"Found near search box: {text[:50]}...")
        
        except Exception as e:
            logger.debug(f"Error in proximity search: {e}")
        
        return items
    
    def _matches_product_terms(self, text: str, product_terms: dict) -> bool:
        """Check if text matches product terms with smart matching."""
        text_upper = text.upper()
        
        # Check for exact match first
        if product_terms['original_upper'] in text_upper:
            return True
        
        # Count matches from different term categories
        matches = 0
        total_terms = 0
        
        # Alphanumeric terms are usually most specific (like model numbers)
        alphanumeric_terms = product_terms.get('alphanumeric', [])
        for term in alphanumeric_terms:
            total_terms += 1
            if term in text_upper:
                matches += 2  # Weight these higher
        
        # Long alpha terms are also important
        long_terms = product_terms.get('long', [])
        for term in long_terms:
            total_terms += 1
            if term in text_upper:
                matches += 1.5
        
        # Regular alpha terms
        alpha_terms = product_terms.get('alpha', [])
        for term in alpha_terms:
            if term not in long_terms:  # Avoid double counting
                total_terms += 1
                if term in text_upper:
                    matches += 1
        
        # Numeric terms (less specific, lower weight)
        numeric_terms = product_terms.get('numeric', [])
        for term in numeric_terms:
            total_terms += 1
            if term in text_upper:
                matches += 0.5
        
        # Decision logic
        if total_terms == 0:
            return False
        
        match_ratio = matches / total_terms
        
        # Require at least 40% match ratio or 2 weighted matches
        return match_ratio >= 0.4 or matches >= 2
    
    def _select_best_match(self, dropdown_items: list, product_terms: dict, original_product: str) -> dict:
        """Select the best matching item from dropdown items."""
        scored_items = []
        
        for item in dropdown_items:
            try:
                text = item.text.strip()
                text_upper = text.upper()
                
                score = self._calculate_match_score(text, text_upper, product_terms, original_product)
                
                scored_items.append({
                    'element': item,
                    'text': text,
                    'score': score
                })
            except Exception as e:
                logger.debug(f"Error scoring item: {e}")
        
        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x['score'], reverse=True)
        
        # Log top matches for debugging
        logger.info("Top dropdown matches:")
        for i, item in enumerate(scored_items[:3]):
            logger.info(f"  {i+1}. Score {item['score']:.2f}: {item['text'][:60]}...")
        
        return scored_items[0] if scored_items else None
    
    def _calculate_match_score(self, text: str, text_upper: str, product_terms: dict, original_product: str) -> float:
        """Calculate match score for a dropdown item."""
        score = 0.0
        
        # Exact match bonus
        if product_terms['original_upper'] in text_upper:
            score += 5.0
        
        # Check if this is just a search suggestion (usually lowercase, no Hebrew)
        is_search_suggestion = (
            text.lower() == text and  # All lowercase
            not any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in text) and  # No Hebrew
            len(text) < 50  # Short text
        )
        
        # If it's just a search suggestion, heavily penalize it
        if is_search_suggestion:
            score *= 0.1  # Reduce score by 90%
        
        # Count term matches
        term_matches = 0
        
        # Alphanumeric terms (highest weight - usually model numbers)
        # These are critical - if they don't match, heavily penalize
        original_numbers = [t for t in product_terms.get('alphanumeric', []) if t.isdigit()]
        found_numbers = []
        
        for term in product_terms.get('alphanumeric', []):
            if term in text_upper:
                score += 2.0
                term_matches += 1
                if term.isdigit():
                    found_numbers.append(term)
        
        # Heavy penalty for mismatched numbers (like 240 vs 21)
        for orig_num in original_numbers:
            if orig_num not in found_numbers:
                # Check if there's a different number in the text that might be conflicting
                import re
                text_numbers = re.findall(r'\b\d+\b', text_upper)
                if text_numbers and orig_num not in text_numbers:
                    score -= 3.0  # Heavy penalty for wrong numbers
                    logger.debug(f"Number mismatch penalty: expected '{orig_num}', found {text_numbers}")
        
        # Additional penalty for significantly different numbers  
        if original_numbers and found_numbers:
            for orig in original_numbers:
                for found in found_numbers:
                    if abs(int(orig) - int(found)) > 50:  # 240 vs 21 = 219 difference
                        score -= 2.0  # Extra penalty for very different numbers
                        logger.debug(f"Large number difference penalty: {orig} vs {found}")
        
        # Long terms (brand names, series)
        for term in product_terms.get('long', []):
            if term in text_upper:
                score += 1.5
                term_matches += 1
        
        # Alpha terms
        for term in product_terms.get('alpha', []):
            if term in text_upper:
                score += 1.0
                term_matches += 1
        
        # Numeric terms (lower weight)
        for term in product_terms.get('numeric', []):
            if term in text_upper:
                score += 0.5
                term_matches += 1
        
        # STRONG bonus for Hebrew text (indicates actual product listing)
        has_hebrew = any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in text)
        if has_hebrew:
            score += 3.0  # Increased from 1.0
            
            # Extra bonus if it contains specific Hebrew product terms
            hebrew_product_terms = ['מזגן', 'מיני מרכזי', 'עילי', 'רצפתי']
            for term in hebrew_product_terms:
                if term in text:
                    score += 1.0
        
        # Bonus for longer descriptions (real products have detailed names)
        if len(text) > 80:
            score += 2.0
        elif len(text) > 50:
            score += 1.0
        elif len(text) > 30:
            score += 0.5
        
        # Penalty for too short (likely just search text)
        if len(text) < 20:
            score *= 0.3
        
        # CRITICAL: Check if ALL significant terms are present
        # This helps distinguish between "60T" and "40T" versions
        all_terms_present = True
        significant_terms = (
            product_terms.get('alphanumeric', []) + 
            [t for t in product_terms.get('numeric', []) if len(t) > 1]  # Exclude single digits
        )
        
        for term in significant_terms:
            if term not in text_upper:
                all_terms_present = False
                break
        
        if all_terms_present and significant_terms:
            score += 3.0  # Big bonus for having all terms
        
        # Use string similarity as tiebreaker
        similarity = self._calculate_string_similarity(original_product.upper(), text_upper)
        score += similarity * 0.5
        
        return score
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        # Simple character overlap ratio
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _fallback_search(self) -> bool:
        """Fallback when no dropdown items found - just press Enter."""
        try:
            search_box = self.driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
            search_box.send_keys(Keys.RETURN)
            logger.info("No dropdown items found - pressed Enter as fallback")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return False
    
    def _click_comparison_button(self) -> Optional[str]:
        """
        Click the comparison button if needed.
        NOTE: After dropdown selection, we're usually already on the comparison page.
        This method is kept for compatibility but may not be needed.
        """
        logger.debug("Checking if we need to click comparison button...")
        
        try:
            # Wait for page to load
            self._wait_for_page_ready()
            
            # Check if we're already on a comparison page
            current_url = self.driver.current_url
            if 'model.aspx' in current_url or 'Compare' in current_url:
                logger.info("Already on comparison page")
                return current_url
            
            # If not on comparison page, look for comparison button
            # Note: This is rarely needed after proper dropdown selection
            comparison_selectors = [
                "a[href*='Compare']",
                "[class*='compare'] a",
                "[class*='Compare'] a"
            ]
            
            for selector in comparison_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            href = button.get_attribute('href')
                            if href and 'Compare' in href:
                                logger.info(f"Found comparison button: {href[:60]}...")
                                button.click()
                                time.sleep(2)
                                return self.driver.current_url
                except:
                    continue
                    
            logger.warning("No comparison button found - may already be on comparison page")
            return current_url
            
        except Exception as e:
            logger.error(f"Error checking comparison button: {e}")
            return None
    
    def _process_comparison_page(self, comparison_url: str, product: ProductInput) -> List[VendorOffer]:
        """Process comparison page and extract vendor offers."""
        logger.debug(f"Processing comparison page: {comparison_url[:60]}...")
        
        vendor_offers = []
        
        try:
            # Get expected count before finding buttons
            expected_count = self._get_expected_vendor_count()
            
            # Find vendor buttons (this also extracts price and vendor name)
            vendor_buttons = self._find_vendor_buttons()
            logger.info(f"  Found {len(vendor_buttons)} vendor buttons" + 
                       (f" (expected: {expected_count})" if expected_count else ""))
            get_vendor_logger().info(f"VENDOR DISCOVERY: Found {len(vendor_buttons)} vendor buttons for product '{product.name}'" + 
                                   (f" (expected: {expected_count})" if expected_count else ""))
            
            # Process each vendor
            successful_vendors = 0
            
            # Use the vendor data we already extracted
            if hasattr(self, '_vendor_data'):
                for idx, vendor_info in enumerate(self._vendor_data):
                    try:
                        logger.debug(f"  Processing vendor {idx + 1}/{len(self._vendor_data)}: {vendor_info['vendor_name']}")
                        
                        button = vendor_info['button']
                        vendor_url = vendor_info['href']
                        
                        if not vendor_url:
                            continue
                        
                        # We already have price, vendor name, and product listing name from the listing page
                        price_str = vendor_info['price']
                        vendor_name = vendor_info['vendor_name']
                        product_listing_name = vendor_info.get('product_listing_name', product.name)  # Fallback to original if not found
                        button_text = vendor_info.get('button_text', '')
                        
                        # Parse price
                        try:
                            # Remove ₪ and commas, then convert to float
                            price = float(price_str.replace('₪', '').replace(',', '').strip())
                        except Exception as e:
                            get_vendor_logger().warning(f"SKIPPED vendor {idx + 1} '{vendor_name}': Could not parse price '{price_str}'. Error: {e}")
                            logger.warning(f"    SKIPPED vendor {idx + 1} '{vendor_name}': Could not parse price '{price_str}'. Error: {e}")
                            continue
                        
                        # Special handling for ZAP internal store entries
                        is_zapstore = ('zapstore' in vendor_name.lower() or 'zap shop' in vendor_name.lower())
                        
                        if is_zapstore:
                            # For zapstore entries, use the original ZAP URL without redirection
                            logger.debug(f"    Processing ZAP internal store vendor {idx + 1}: {vendor_name} - ₪{price:,.0f}")
                            vendor_offer = VendorOffer(
                                vendor_name="ZAP Store",  # Standardize zapstore name
                                product_name=product_listing_name,  # Use product name as it appears in listing
                                price=price,
                                url=vendor_url,  # Use original ZAP URL
                                button_text=button_text  # Include button text
                            )
                            # Store zapstore entries separately to add them at the end
                            if not hasattr(self, '_zapstore_offers'):
                                self._zapstore_offers = []
                            self._zapstore_offers.append(vendor_offer)
                            successful_vendors += 1
                            logger.debug(f"    Successfully processed ZAP Store vendor {idx + 1}: ZAP Store - ₪{price:,.0f}")
                        else:
                            # Regular external vendor processing with RETRY LOGIC
                            final_url = self._process_vendor_with_retry(vendor_url, vendor_name, idx)
                            
                            # Create vendor offer with data we already have (if URL was successfully captured)
                            if final_url and 'zap.co.il' not in final_url:
                                vendor_offer = VendorOffer(
                                    vendor_name=vendor_name,
                                    product_name=product_listing_name,  # Use product name as it appears in listing
                                    price=price,
                                    url=final_url,
                                    button_text=button_text  # Include button text
                                )
                                vendor_offers.append(vendor_offer)
                                successful_vendors += 1
                                logger.debug(f"    Successfully processed external vendor {idx + 1}: {vendor_name} - ₪{price:,.0f}")
                            elif final_url and 'zap.co.il' in final_url:
                                get_vendor_logger().warning(f"SKIPPED vendor {idx + 1} '{vendor_name}': URL didn't redirect properly (still contains zap.co.il). Final URL: {final_url}")
                                logger.warning(f"    SKIPPED vendor {idx + 1} '{vendor_name}': URL didn't redirect properly (still contains zap.co.il). Final URL: {final_url}")
                            else:
                                get_vendor_logger().warning(f"SKIPPED vendor {idx + 1} '{vendor_name}': Failed to capture URL within timeout")
                                logger.warning(f"    SKIPPED vendor {idx + 1} '{vendor_name}': Failed to capture URL within timeout")
                        
                    except Exception as e:
                        vendor_name = vendor_info.get('vendor_name', 'Unknown')
                        logger.warning(f"    SKIPPED vendor {idx + 1} '{vendor_name}': Error during processing - {e}")
                        # Make sure we're back on main tab
                        if len(self.driver.window_handles) > 1:
                            self._close_tab_and_return()
                        continue
            
            # Add ZAP Store entries at the end of the vendor list
            zapstore_count = 0
            if hasattr(self, '_zapstore_offers') and self._zapstore_offers:
                vendor_offers.extend(self._zapstore_offers)
                zapstore_count = len(self._zapstore_offers)
                logger.info(f"  Added {zapstore_count} ZAP Store entries at the end of vendor list")
            
            total_found = len(self._vendor_data) if hasattr(self, '_vendor_data') else len(vendor_buttons)
            external_vendors = successful_vendors - zapstore_count
            skipped_count = total_found - successful_vendors
            
            logger.info(f"  VENDOR PROCESSING SUMMARY: {external_vendors} external vendors, {zapstore_count} ZAP Store entries, {skipped_count} skipped, {total_found} total found")
            if skipped_count > 0:
                logger.info(f"  NOTE: {skipped_count} vendors were skipped due to redirect failures, price parsing errors, or processing exceptions")
            
            # Detailed vendor processing log
            get_vendor_logger().info(f"VENDOR PROCESSING SUMMARY for '{product.name}': {external_vendors} external vendors, {zapstore_count} ZAP Store entries, {skipped_count} skipped, {total_found} total found")
            if skipped_count > 0:
                get_vendor_logger().warning(f"NOTE: {skipped_count} vendors were skipped due to redirect failures, price parsing errors, or processing exceptions")
            
        except Exception as e:
            logger.error(f"Error processing comparison page: {e}")
        
        return vendor_offers
    
    def _process_vendor_with_retry(self, vendor_url: str, vendor_name: str, vendor_idx: int) -> Optional[str]:
        """
        Process vendor with retry logic - tries twice with 30s timeout each.
        
        Args:
            vendor_url: URL to visit
            vendor_name: Vendor name for logging
            vendor_idx: Vendor index for logging
            
        Returns:
            Final URL if successful, None if all attempts failed
        """
        import time
        
        # Attempt 1
        get_vendor_logger().info(f"Processing vendor {vendor_idx + 1} '{vendor_name}' (attempt 1/2)")
        result = self._process_vendor_with_timeout(vendor_url, vendor_name, vendor_idx, self.config.vendor_timeout)
        
        if result:
            return result
            
        # Wait before retry
        get_vendor_logger().warning(f"Vendor {vendor_idx + 1} '{vendor_name}' failed on attempt 1, retrying in {self.config.retry_delay}s...")
        time.sleep(self.config.retry_delay)
        
        # Attempt 2
        get_vendor_logger().info(f"Processing vendor {vendor_idx + 1} '{vendor_name}' (attempt 2/2)")
        result = self._process_vendor_with_timeout(vendor_url, vendor_name, vendor_idx, self.config.vendor_timeout)
        
        if result:
            return result
            
        # Both attempts failed - log final failure
        get_vendor_logger().warning(f"SKIPPED vendor {vendor_idx + 1} '{vendor_name}': Failed both attempts (30s timeout each)")
        return None

    def _process_vendor_with_timeout(self, vendor_url: str, vendor_name: str, vendor_idx: int, timeout_seconds: int = 30) -> Optional[str]:
        """
        Process vendor page with ACTIVE timeout protection to prevent getting stuck.
        
        Args:
            vendor_url: URL to visit
            vendor_name: Vendor name for logging
            vendor_idx: Vendor index for logging
            timeout_seconds: Maximum time to spend on vendor page (30s default)
            
        Returns:
            Final URL if successful, None if timeout or error
        """
        import threading
        from selenium.common.exceptions import TimeoutException, WebDriverException
        
        final_url = None
        timeout_occurred = False
        processing_complete = False
        
        def force_timeout():
            nonlocal timeout_occurred
            if not processing_complete:
                timeout_occurred = True
                get_vendor_logger().warning(f"FORCE TIMEOUT: Vendor {vendor_idx + 1} '{vendor_name}' exceeded {timeout_seconds}s - ACTIVELY CLOSING")
                logger.warning(f"    FORCE TIMEOUT: Vendor {vendor_idx + 1} '{vendor_name}' exceeded {timeout_seconds}s - ACTIVELY CLOSING")
                # Immediately try to force close any stuck tabs
                try:
                    self._emergency_tab_close()
                except:
                    pass
        
        # Set up aggressive timeout
        timer = threading.Timer(timeout_seconds, force_timeout)
        
        try:
            timer.start()
            
            # Step 1: Open vendor page with immediate timeout check
            if not timeout_occurred:
                try:
                    self._open_in_new_tab(vendor_url)
                except Exception as e:
                    get_vendor_logger().warning(f"TIMEOUT: Failed to open tab for vendor {vendor_idx + 1} '{vendor_name}': {e}")
                    logger.warning(f"    TIMEOUT: Failed to open tab for vendor {vendor_idx + 1} '{vendor_name}': {e}")
                    timeout_occurred = True
            
            # Step 2: Quick wait with frequent timeout checks
            if not timeout_occurred:
                total_wait = 0
                while total_wait < 5 and not timeout_occurred:  # Max 5 seconds wait (increased from 3)
                    time.sleep(0.5)
                    total_wait += 0.5
            
            # Step 3: Get URL quickly
            if not timeout_occurred:
                try:
                    final_url = self.driver.current_url
                    processing_complete = True  # Mark as complete to prevent force timeout
                except Exception as e:
                    get_vendor_logger().warning(f"TIMEOUT: Could not get URL for vendor {vendor_idx + 1} '{vendor_name}': {e}")
                    logger.warning(f"    TIMEOUT: Could not get URL for vendor {vendor_idx + 1} '{vendor_name}': {e}")
                    timeout_occurred = True
            
            # Step 4: Close and return (or force close if timeout)
            if not timeout_occurred and processing_complete:
                self._close_tab_and_return()
            else:
                self._emergency_tab_close()
                
        except Exception as e:
            get_vendor_logger().warning(f"TIMEOUT: Critical error processing vendor {vendor_idx + 1} '{vendor_name}': {e}")
            logger.warning(f"    TIMEOUT: Critical error processing vendor {vendor_idx + 1} '{vendor_name}': {e}")
            timeout_occurred = True
            processing_complete = True  # Prevent further force timeout
            self._emergency_tab_close()
            
        finally:
            processing_complete = True  # Ensure timer doesn't fire after we're done
            timer.cancel()
        
        return None if timeout_occurred else final_url
    
    def _find_vendor_buttons(self) -> List:
        """
        Find vendor buttons/links on ZAP comparison page.
        Updated approach: Look for vendor redirect links (fs.aspx) directly,
        then validate they have price and vendor info nearby.
        """
        vendor_data = []  # Will store tuples of (button, price, vendor_name, container)
        
        # Get expected vendor count from page
        expected_count = self._get_expected_vendor_count()
        if expected_count:
            logger.info(f"Page shows {expected_count} vendors available")
        
        # CRITICAL: Scroll to footer first to ensure all content is visible
        logger.info("Scrolling to page footer to reveal all vendor listings...")
        self._scroll_to_end()
        
        # Find vendor redirect links (these go to vendor pages)
        # Updated to include all ZAP vendor link patterns: fs.aspx, fsbid.aspx, fs/mp
        vendor_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='fs.aspx'], a[href*='/fs/'], a[href*='fsbid.aspx'], a[href*='fs/mp']")
        logger.info(f"Found {len(vendor_links)} vendor redirect links")
        
        # Filter out carousel/slider items if they exist
        non_carousel_links = []
        for link in vendor_links:
            try:
                # Check if in carousel by looking up the DOM
                in_carousel = False
                element = link
                for _ in range(5):
                    element = element.find_element(By.XPATH, "..")
                    class_name = element.get_attribute('class') or ''
                    if 'carousel' in class_name.lower() or 'slider' in class_name.lower():
                        in_carousel = True
                        break
                
                if not in_carousel:
                    non_carousel_links.append(link)
                else:
                    logger.debug("Skipping carousel vendor link")
            except:
                # If we can't check, include it
                non_carousel_links.append(link)
        
        logger.info(f"Found {len(non_carousel_links)} non-carousel vendor links")
        
        # STEP 2: For each vendor link, check for price and vendor info
        seen_hrefs = set()  # To avoid duplicates
        
        for link in non_carousel_links:
            try:
                if not link.is_displayed():
                    continue
                
                # Get href
                href = link.get_attribute('href')
                if not href or 'fs' not in href:
                    continue
                
                # Skip duplicates
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)
                
                # Find the vendor container
                vendor_container = None
                vendor_name = None
                price_text = None
                
                # Go up to find the container that has the complete vendor info
                element = link
                for i in range(8):
                    try:
                        element = element.find_element(By.XPATH, "..")
                        
                        # Check if this container has all the key elements
                        element_text = element.text
                        
                        # Must have price
                        if '₪' not in element_text:
                            continue
                        
                        # Must have vendor logo (image)
                        imgs = element.find_elements(By.TAG_NAME, "img")
                        if not imgs:
                            continue
                        
                        # Check if any image has vendor info in tooltip/alt
                        has_vendor_logo = False
                        for img in imgs:
                            tooltip_attrs = [
                                img.get_attribute('title'),
                                img.get_attribute('alt'),
                                img.get_attribute('data-tooltip')
                            ]
                            if any(attr and len(attr.strip()) > 1 for attr in tooltip_attrs):
                                has_vendor_logo = True
                                break
                        
                        if has_vendor_logo:
                            vendor_container = element
                            logger.debug(f"Found vendor container with price and logo: <{element.tag_name}>")
                            break
                            
                    except:
                        break
                
                if vendor_container:
                    container_text = vendor_container.text
                    
                    # Extract price - ENHANCED: Select main price using visual size, position, and value
                    if '₪' in container_text:
                        import re
                        
                        # Find all price elements with their context and styling
                        price_elements = vendor_container.find_elements(By.CSS_SELECTOR, "*")
                        candidate_prices = []
                        
                        for element in price_elements:
                            element_text = element.text.strip()
                            if '₪' in element_text:
                                # Extract price matches from this element
                                price_matches = re.findall(r'[\d,]+\s*₪', element_text)
                                for price_str in price_matches:
                                    try:
                                        # Parse price value
                                        price_val = float(price_str.replace('₪', '').replace(',', '').strip())
                                        if 100 <= price_val <= 50000:  # Reasonable range for air conditioners
                                            
                                            # Analyze element characteristics for main vs delivery price
                                            element_html = element.get_attribute('outerHTML') or ''
                                            element_classes = element.get_attribute('class') or ''
                                            
                                            # Score this price based on multiple criteria
                                            score = 0
                                            
                                            # 1. VALUE SCORE: Higher price gets higher score (main prices > delivery)
                                            score += price_val / 1000  # Normalize: ₪4,870 = 4.87 points, ₪39 = 0.039 points
                                            
                                            # 2. VISUAL SIZE SCORE: Look for visual prominence indicators
                                            # Large font indicators
                                            if any(indicator in element_html.lower() for indicator in ['font-size', 'large', 'big', 'h1', 'h2', 'h3']):
                                                score += 10
                                            if any(indicator in element_classes.lower() for indicator in ['price', 'main', 'primary', 'big', 'large']):
                                                score += 5
                                            
                                            # 3. POSITION SCORE: Elements higher in DOM typically have main prices
                                            try:
                                                element_rect = element.location
                                                # Lower Y coordinate = higher on page = more likely main price
                                                if element_rect['y'] < 500:  # Top half of typical listing
                                                    score += 3
                                            except:
                                                pass
                                            
                                            # 4. CONTEXT PENALTIES: Avoid delivery-related prices
                                            context_text = element_text.lower()
                                            parent_text = element.find_element(By.XPATH, "..").text.lower() if element else ""
                                            
                                            # Penalize delivery/shipping indicators
                                            delivery_keywords = ['משלוח', 'shipping', 'delivery', 'הובלה', 'מסירה']
                                            if any(keyword in context_text or keyword in parent_text for keyword in delivery_keywords):
                                                score -= 15  # Heavy penalty for delivery context
                                            
                                            candidate_prices.append({
                                                'price_val': price_val,
                                                'price_str': price_str,
                                                'score': score,
                                                'element': element,
                                                'context': element_text[:50]  # First 50 chars for debugging
                                            })
                                            
                                    except ValueError:
                                        continue
                        
                        # Select the highest-scored price (best combination of size, position, value)
                        if candidate_prices:
                            best_price = max(candidate_prices, key=lambda x: x['score'])
                            price_text = best_price['price_str']
                            logger.debug(f"Found {len(candidate_prices)} prices, selected BEST-SCORED: {price_text} (score: {best_price['score']:.2f}, context: '{best_price['context']}')")
                        else:
                            # Fallback to simple regex if sophisticated method fails
                            price_matches = re.findall(r'[\d,]+\s*₪', container_text)
                            if price_matches:
                                # Simple fallback: just take highest value
                                parsed_prices = []
                                for price_str in price_matches:
                                    try:
                                        price_val = float(price_str.replace('₪', '').replace(',', '').strip())
                                        if 100 <= price_val <= 50000:
                                            parsed_prices.append((price_val, price_str))
                                    except ValueError:
                                        continue
                                
                                if parsed_prices:
                                    largest_price_val, price_text = max(parsed_prices, key=lambda x: x[0])
                                    logger.debug(f"Fallback: Found {len(price_matches)} prices, selected LARGEST by value: {price_text}")
                    
                    # Extract product name from listing (4th artifact)
                    product_listing_name = ""
                    try:
                        # Strategy 1: Look for longer text elements that might contain product names
                        all_text_elements = vendor_container.find_elements(By.CSS_SELECTOR, "a, span, div, h1, h2, h3, h4, h5, h6")
                        for element in all_text_elements:
                            element_text = element.text.strip()
                            # Look for text that's long enough and contains key product identifiers
                            if (len(element_text) > 15 and 
                                ('INV' in element_text.upper() or 'MASTER' in element_text.upper() or 
                                 'TORNADO' in element_text.upper() or 'מזגן' in element_text)):
                                product_listing_name = element_text
                                logger.debug(f"Found product listing name: {product_listing_name}")
                                break
                        
                        # Strategy 2: If not found, look for any text containing numbers and letters (product codes)
                        if not product_listing_name:
                            for element in all_text_elements:
                                element_text = element.text.strip()
                                if (len(element_text) > 10 and 
                                    any(char.isdigit() for char in element_text) and
                                    any(char.isalpha() for char in element_text) and
                                    'EUR' not in element_text and '₪' not in element_text):
                                    product_listing_name = element_text
                                    logger.debug(f"Found product listing name (fallback): {product_listing_name}")
                                    break
                                    
                        # Strategy 3: Use container text if nothing else found
                        if not product_listing_name:
                            container_lines = container_text.split('\n')
                            for line in container_lines:
                                line = line.strip()
                                if (len(line) > 15 and 
                                    any(char.isdigit() for char in line) and
                                    'EUR' not in line and '₪' not in line and
                                    'לפרטים' not in line and 'קנו עכשיו' not in line):
                                    product_listing_name = line
                                    logger.debug(f"Found product listing name (container): {product_listing_name}")
                                    break
                                    
                    except Exception as e:
                        logger.debug(f"Could not extract product listing name: {e}")
                    
                    # Extract vendor name
                    # Method 1: Look for vendor logo images with tooltips
                    imgs = vendor_container.find_elements(By.TAG_NAME, "img")
                    for img in imgs:
                        # Check for tooltip attributes (title, alt, or data-tooltip)
                        vendor_name_sources = [
                            img.get_attribute('title'),
                            img.get_attribute('alt'),
                            img.get_attribute('data-tooltip'),
                            img.get_attribute('aria-label')
                        ]
                        
                        for source in vendor_name_sources:
                            if source and len(source.strip()) > 1:
                                vendor_name = source.strip()
                                logger.debug(f"Found vendor from image tooltip/alt: {vendor_name}")
                                break
                        
                        if vendor_name:
                            break
                    
                    # Method 2: Look for text patterns
                    if not vendor_name:
                        # For table-based layouts, vendor name might be in a specific cell
                        if vendor_container.tag_name.lower() == 'tr':
                            cells = vendor_container.find_elements(By.TAG_NAME, "td")
                            # Usually vendor is in one of the first few cells
                            for cell in cells[:3]:
                                cell_text = cell.text.strip()
                                # Skip cells with just price or button
                                if cell_text and '₪' not in cell_text and cell_text not in hebrew_button_texts:
                                    if len(cell_text) > 2 and len(cell_text) < 50:
                                        vendor_name = cell_text
                                        logger.debug(f"Found vendor from table cell: {vendor_name}")
                                        break
                        
                        # For other layouts, look for vendor name in text
                        if not vendor_name:
                            lines = container_text.split('\n')
                            for line in lines:
                                line = line.strip()
                                # Skip empty lines, prices, and button text
                                if (line and 
                                    '₪' not in line and 
                                    line not in hebrew_button_texts and
                                    len(line) > 2 and 
                                    len(line) < 50):
                                    # Check for common patterns
                                    if any(domain in line.lower() for domain in ['.co.il', '.com', 'בע"מ']):
                                        vendor_name = line
                                        logger.debug(f"Found vendor with domain/company: {vendor_name}")
                                        break
                                    # Otherwise take first reasonable text
                                    elif not vendor_name:
                                        vendor_name = line
                                        logger.debug(f"Found vendor from text: {vendor_name}")
                
                # Validate we found all 3 artifacts
                if vendor_container and vendor_name and price_text:
                    # Extract button text for zapstore detection
                    button_text = ''
                    try:
                        button_text = link.text.strip() if link.text else ''
                    except:
                        pass
                    
                    # Store all the data we need (4 artifacts + extras)
                    vendor_data.append({
                        'button': link,  # Using the link as the clickable element
                        'price': price_text,
                        'vendor_name': vendor_name,
                        'product_listing_name': product_listing_name,  # 4th artifact
                        'container': vendor_container,
                        'href': href,
                        'button_text': button_text
                    })
                    
                    logger.info(f"✓ Valid vendor found: {vendor_name} - {price_text}")
                else:
                    # Log why this button was rejected
                    if not vendor_container:
                        logger.debug(f"Button rejected: No container found")
                    elif not price_text:
                        logger.debug(f"Button rejected: No price found")
                    elif not vendor_name:
                        logger.debug(f"Button rejected: No vendor name found")
                
            except Exception as e:
                logger.debug(f"Error validating button: {e}")
                continue
        
        found_count = len(vendor_data)
        logger.info(f"Found {found_count} validated vendor offerings")
        
        if expected_count and found_count < expected_count:
            logger.warning(f"Found {found_count} vendors, expected {expected_count}")
            logger.info("Some vendors may not have valid button/price/vendor combinations on same line")
        
        # Store vendor data for later use
        self._vendor_data = vendor_data
        
        # Return just the buttons for compatibility
        return [v['button'] for v in vendor_data]
    
    def _validate_vendor_button(self, button_element) -> bool:
        """Validate if button has associated vendor data."""
        try:
            # Check if button is visible and enabled
            if not button_element.is_displayed() or not button_element.is_enabled():
                return False
            
            # Check for href
            href = button_element.get_attribute('href')
            if not href:
                return False
            
            # Check for vendor indicators nearby
            parent = button_element.find_element(By.XPATH, "./..")
            parent_text = parent.text.lower()
            
            # Look for price or vendor name indicators
            if any(indicator in parent_text for indicator in ['₪', 'מחיר', 'price']):
                return True
            
            return True  # Default to true if basic checks pass
            
        except:
            return False
    
    def _validate_vendor_button_enhanced(self, button_element) -> bool:
        """
        Enhanced validation according to ZAP-SCRAPING-GUIDE criteria.
        Each button MUST have:
        1. Price Information: Visible pricing
        2. Vendor Name: Vendor identification
        3. Complete Listing: Full product information
        """
        try:
            # Check if button is visible and enabled
            if not button_element.is_displayed() or not button_element.is_enabled():
                return False
            
            # Check for href
            href = button_element.get_attribute('href')
            if not href or not ('/fs' in href or 'fs.aspx' in href):
                return False
            
            # Find the parent container (could be row, div, li, etc.)
            # Try multiple levels up to find the vendor listing container
            container = None
            for i in range(1, 6):  # Check up to 5 levels up
                try:
                    xpath = "/".join([".."] * i)
                    potential_container = button_element.find_element(By.XPATH, xpath)
                    container_text = potential_container.text
                    
                    # Check if this looks like a vendor listing (has price)
                    if '₪' in container_text:
                        container = potential_container
                        break
                except:
                    continue
            
            if not container:
                logger.debug(f"No container with price found for button: {button_element.text}")
                return False
            
            container_text = container.text
            
            # Validation Criteria from guide:
            
            # 1. Price Information - MUST have price
            has_price = '₪' in container_text
            if not has_price:
                logger.debug("Button rejected: No price information")
                return False
            
            # 2. Vendor Name - Look for vendor indicators
            # Common vendor name patterns in Hebrew
            vendor_indicators = [
                'חנות',      # Store
                'ספק',       # Supplier
                'מוכר',      # Seller
                'מחיר',      # Price
                'הצעה',      # Offer
                '.co.il',    # Domain names
                '.com',
                'בע"מ',      # Ltd
                'שיווק',     # Marketing
                'מכירות'    # Sales
            ]
            
            has_vendor = any(indicator in container_text for indicator in vendor_indicators)
            
            # Also check if there's reasonable text length (vendor listings have descriptions)
            text_length = len(container_text)
            has_content = text_length > 20  # Minimum reasonable length
            
            # 3. Button text validation - should be one of the expected Hebrew texts
            button_text = button_element.text.strip()
            valid_button_text = button_text in ["קנו עכשיו", "לפרטים נוספים"]
            
            # If button has no text, it might be an image or styled button
            # In that case, check the href pattern
            if not button_text and ('/fs' in href or 'fs.aspx' in href):
                valid_button_text = True
            
            # Log validation results for debugging
            if not (has_vendor or has_content):
                logger.debug(f"Button rejected: No vendor info or insufficient content (length: {text_length})")
                return False
            
            if not valid_button_text and button_text:
                logger.debug(f"Button has unexpected text: '{button_text}'")
            
            # All criteria met
            return True
            
        except Exception as e:
            logger.debug(f"Error in enhanced validation: {e}")
            return False
    
    def _extract_vendor_data(self, vendor_url: str) -> Optional[VendorOffer]:
        """Extract vendor data from vendor page."""
        try:
            # Wait for page to load
            self._wait_for_page_ready()
            
            # Scroll to reveal prices
            self._scroll_to_end()
            
            # Extract vendor name
            vendor_name = self._extract_vendor_name(vendor_url)
            
            # Extract product name
            product_name = self._extract_product_name()
            
            # Extract price
            price = self._extract_price()
            
            if price:
                return VendorOffer(
                    vendor_name=vendor_name,
                    product_name=product_name,
                    price=price,
                    url=vendor_url
                )
            else:
                logger.warning(f"No price found on vendor page: {vendor_url[:60]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting vendor data: {e}")
            return None
    
    def _extract_vendor_name(self, url: str) -> str:
        """Extract vendor name from URL or page."""
        try:
            # From domain
            domain = urlparse(url).netloc
            if domain and 'zap.co.il' not in domain:
                vendor_name = domain.replace('www.', '').split('.')[0]
                return vendor_name.title()
            
            # From page title
            if self.driver.title:
                title_parts = re.split(r'[-|]', self.driver.title)
                if title_parts:
                    return title_parts[0].strip()
                    
        except:
            pass
        
        return "Unknown Vendor"
    
    def _extract_product_name(self) -> str:
        """Extract product name from vendor page."""
        try:
            # Try multiple selectors
            selectors = [
                "h1", "h2.product-title",
                "[class*='product-name']", "[class*='product-title']",
                "[itemprop='name']", ".title", ".product_title"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and 5 < len(text) < 200:
                        return text
                        
        except:
            pass
        
        return "Unknown Product"
    
    def _extract_price(self) -> Optional[float]:
        """Extract price from vendor page."""
        try:
            # Method 1: Structured data
            try:
                price_meta = self.driver.find_element(By.CSS_SELECTOR, "meta[itemprop='price']")
                price_content = price_meta.get_attribute('content')
                if price_content:
                    return float(re.sub(r'[^\d.]', '', price_content))
            except:
                pass
            
            # Method 2: Price elements
            price_selectors = [
                "[class*='price']:not([class*='old']):not([class*='strike'])",
                "[class*='Price']:not([class*='old']):not([class*='strike'])",
                "[id*='price']:not([class*='old'])",
                ".current-price", ".final-price",
                "span[itemprop='price']"
            ]
            
            for selector in price_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    price = self.hebrew_processor.extract_price_from_hebrew(elem.text)
                    if price and 100 < price < 50000:
                        return price
            
            # Method 3: Page text search
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            price = self.hebrew_processor.extract_price_from_hebrew(page_text)
            if price and 100 < price < 50000:
                return price
                
        except Exception as e:
            logger.debug(f"Price extraction error: {e}")
        
        return None
    
    def _open_in_new_tab(self, url: str = None) -> None:
        """Open new tab and switch to it."""
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if url:
            self.driver.get(url)
    
    def _close_tab_and_return(self) -> None:
        """Close current tab and return to main window."""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
    
    def _wait_for_page_ready(self, timeout: int = 10) -> None:
        """Wait for page to be ready."""
        try:
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Wait for jQuery if present
            try:
                self.driver.execute_script("return typeof jQuery !== 'undefined' && jQuery.active === 0")
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return typeof jQuery !== 'undefined' && jQuery.active === 0")
                )
            except:
                pass  # jQuery might not be present
            
            # Additional wait for dynamic content
            time.sleep(1)
            
        except TimeoutException:
            logger.warning("Page load timeout - continuing anyway")
        except Exception as e:
            logger.error(f"Error waiting for page ready: {e}")
    
    def _close_popups(self) -> None:
        """Try to close any popups."""
        try:
            # Wait a moment for popups to appear
            time.sleep(2)
            
            # Common popup close selectors
            close_selectors = [
                "button[aria-label='close']",
                "button.close",
                "[class*='close-button']",
                "[class*='popup-close']",
                "svg[class*='close']",
                "[class*='close']", 
                "[class*='Close']",
                "[aria-label*='close']", 
                "[aria-label*='Close']",
                "button[class*='popup-close']"
            ]
            
            closed_count = 0
            for selector in close_selectors:
                try:
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed() and button.is_enabled():
                            try:
                                button.click()
                                closed_count += 1
                                logger.debug(f"Closed popup with selector: {selector}")
                                time.sleep(0.5)
                            except:
                                continue
                except:
                    continue
            
            if closed_count > 0:
                logger.info(f"Closed {closed_count} popup(s)")
                
        except Exception as e:
            logger.debug(f"Error closing popups: {e}")
    
    def _scroll_to_end(self) -> None:
        """Enhanced scrolling to ensure all content is loaded."""
        max_scrolls = 10
        no_change_count = 0
        
        for i in range(max_scrolls):
            # Get current height and vendor count
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            vendor_count_before = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='fs']"))
            
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for content to load
            time.sleep(2)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            vendor_count_after = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='fs']"))
            
            logger.debug(f"Scroll {i+1}: Height {last_height}->{new_height}, Vendors: {vendor_count_before}->{vendor_count_after}")
            
            # If no changes in height or vendor count
            if new_height == last_height and vendor_count_after == vendor_count_before:
                no_change_count += 1
                
                # Try alternate scrolling strategy
                if no_change_count == 1:
                    # Scroll up a bit then down again
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 500);")
                    time.sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)
                elif no_change_count == 2:
                    # Try scrolling to middle then bottom
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                    time.sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)
                elif no_change_count >= 3:
                    # No more content to load
                    break
            else:
                # Reset counter if new content was loaded
                no_change_count = 0
    
    def _get_expected_vendor_count(self) -> Optional[int]:
        """Extract the expected vendor count from the page."""
        try:
            # Look for count in various patterns
            count_patterns = [
                r'השוואת הצעות \((\d+)\)',  # "Comparison of offers (19)"
                r'(\d+) הצעות',              # "19 offers"
                r'(\d+) חנויות',             # "19 stores"
                r'(\d+) מוכרים',             # "19 sellers"
                r'נמצאו (\d+)',              # "Found 19"
                r'\((\d+)\)',                # Any number in parentheses
            ]
            
            # Try to find the count in page text
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            for pattern in count_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Return the first reasonable number (between 1 and 100)
                    for match in matches:
                        count = int(match)
                        if 1 <= count <= 100:
                            logger.info(f"Found expected vendor count: {count}")
                            return count
            
            # Try specific elements that might contain the count
            count_selectors = [
                "[class*='count']",
                "[class*='number']",
                "[class*='total']",
                "[class*='results']",
                ".comparison-header",
                ".offer-count"
            ]
            
            for selector in count_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text
                        for pattern in count_patterns:
                            match = re.search(pattern, text)
                            if match:
                                count = int(match.group(1))
                                if 1 <= count <= 100:
                                    logger.info(f"Found expected vendor count in element: {count}")
                                    return count
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Could not extract vendor count: {e}")
        
        return None
    
    def _click_load_more_buttons(self) -> bool:
        """Click any 'load more' buttons to reveal all vendors."""
        clicked_any = False
        
        # Various "load more" button patterns
        load_more_selectors = [
            "button[class*='load-more']",
            "button[class*='show-more']",
            "a[class*='load-more']",
            "a[class*='show-more']",
            "[class*='more-vendors']",
            "[class*='show-all']",
            "[class*='view-all']",
            "[class*='see-all']",
            "button[onclick*='more']",
            "a[onclick*='more']"
        ]
        
        # Hebrew text patterns for load more
        hebrew_patterns = [
            "//button[contains(text(), 'עוד')]",
            "//button[contains(text(), 'הצג עוד')]",
            "//button[contains(text(), 'טען עוד')]",
            "//button[contains(text(), 'ראה עוד')]",
            "//button[contains(text(), 'כל')]",
            "//a[contains(text(), 'עוד')]",
            "//a[contains(text(), 'הצג עוד')]",
            "//a[contains(text(), 'טען עוד')]",
            "//a[contains(text(), 'ראה עוד')]",
            "//a[contains(text(), 'כל')]"
        ]
        
        # Try CSS selectors first
        for selector in load_more_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        logger.info(f"Found load more button: {button.text[:30]}")
                        button.click()
                        clicked_any = True
                        time.sleep(2)  # Wait for content to load
            except:
                continue
        
        # Try XPath patterns for Hebrew text
        for xpath in hebrew_patterns:
            try:
                buttons = self.driver.find_elements(By.XPATH, xpath)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        logger.info(f"Found Hebrew load more button: {button.text}")
                        button.click()
                        clicked_any = True
                        time.sleep(2)
            except:
                continue
        
        return clicked_any
    
    def _apply_delay(self) -> None:
        """Apply random delay between requests."""
        import random
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        time.sleep(delay) 

    def _emergency_tab_close(self):
        """EMERGENCY: Force close all tabs and return to main - for stuck situations."""
        try:
            logger.warning("EMERGENCY TAB CLOSE: Forcing browser tab closure")
            
            # Get all handles
            all_handles = self.driver.window_handles
            
            if len(all_handles) > 1:
                main_handle = all_handles[0]
                
                # Force close ALL other tabs immediately
                for handle in all_handles[1:]:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                        logger.debug(f"Force closed stuck tab: {handle}")
                    except:
                        pass  # Ignore errors, just close everything
                
                # Force switch back to main
                try:
                    self.driver.switch_to.window(main_handle)
                    logger.debug("Returned to main tab after emergency close")
                except:
                    # If main tab switch fails, try to navigate back to ZAP
                    try:
                        self.driver.get("https://zap.co.il")
                        logger.warning("Emergency navigation back to ZAP")
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"Emergency tab close failed: {e}")
            # Last resort: try to navigate to a safe page
            try:
                self.driver.get("https://zap.co.il")
            except:
                pass
    
    def _evaluate_bold_vs_dropdown_decision(self, product_name: str, best_dropdown_item: dict) -> dict:
        """
        Evaluate whether to use bold option (P1 results) or dropdown option (P2).
        
        Args:
            product_name: Original search term (bold option)
            best_dropdown_item: Best scored dropdown item with 'text' and 'score'
            
        Returns:
            dict with 'choice' ('bold' or 'dropdown') and 'reason'
        """
        try:
            # Parse components of original search term
            search_components = self._parse_product_components(product_name)
            logger.info(f"🧩 SEARCH COMPONENTS: {search_components}")
            
            # If no dropdown item, use bold
            if not best_dropdown_item:
                return {
                    'choice': 'bold',
                    'reason': 'No dropdown alternatives available'
                }
            
            # Parse components of best dropdown option  
            dropdown_text = best_dropdown_item.get('text', '')
            dropdown_components = self._parse_product_components(dropdown_text)
            logger.info(f"🧩 DROPDOWN COMPONENTS: {dropdown_components}")
            
            # Score bold option (original search term)
            bold_score = self._score_component_match(search_components, search_components)  # Perfect self-match
            
            # Score dropdown option
            dropdown_score = self._score_component_match(search_components, dropdown_components)
            
            logger.info(f"📊 COMPONENT SCORES: Bold={bold_score:.1f}, Dropdown={dropdown_score:.1f}")
            
            # Decision rules
            return self._make_component_decision(search_components, bold_score, dropdown_score, dropdown_text)
            
        except Exception as e:
            logger.error(f"Error in component analysis: {e}")
            # Fallback to existing logic
            return {
                'choice': 'dropdown',
                'reason': f'Component analysis failed, using existing logic: {e}'
            }
    
    def _parse_product_components(self, product_name: str) -> dict:
        """
        Parse product name into Manufacturer + Series + Model components.
        
        Examples:
        "Electra AI INV 150" → Manufacturer: "Electra", Series: "AI INV", Model: "150"
        "ELCO Slim A SQ INV 40/1P" → Manufacturer: "ELCO", Series: "Slim A SQ INV", Model: "40/1P"  
        "Classic INV 240" → Manufacturer: "", Series: "Classic INV", Model: "240"
        """
        import re
        
        product_upper = product_name.upper().strip()
        
        # Known manufacturers (expandable list)
        manufacturers = [
            'ELECTRA', 'ELCO', 'TADIRAN', 'LG', 'SAMSUNG', 'HAIER', 'GREE', 
            'MIDEA', 'TORNADO', 'CARRIER', 'YORK', 'TRANE', 'DAIKIN', 'FUJITSU'
        ]
        
        # Extract manufacturer (if present at start)
        manufacturer = ""
        for mfg in manufacturers:
            if product_upper.startswith(mfg + ' '):
                manufacturer = mfg
                break
        
        # Extract model (numbers/alphanumeric at end)
        # Patterns: "150", "240", "40/1P", "18000", "12K", etc.
        model_patterns = [
            r'\b(\d+/\d+[A-Z]*)\b$',      # "40/1P", "50/3P"
            r'\b(\d+[A-Z]+)\b$',          # "12K", "18BTU"  
            r'\b(\d{3,})\b$',             # "240", "150", "18000"
            r'\b([A-Z]+\d+)\b$',          # "INV240", "BTU150"
        ]
        
        model = ""
        for pattern in model_patterns:
            match = re.search(pattern, product_upper)
            if match:
                model = match.group(1)
                break
        
        # Extract series (everything between manufacturer and model)
        series = product_upper
        if manufacturer:
            series = series.replace(manufacturer, '').strip()
        if model:
            series = re.sub(r'\b' + re.escape(model) + r'\b$', '', series).strip()
        
        return {
            'manufacturer': manufacturer,
            'series': series,
            'model': model,
            'original': product_name
        }
    
    def _score_component_match(self, search_components: dict, candidate_components: dict) -> float:
        """
        Score how well candidate components match search components.
        
        Priority: Model (highest) > Series (high) > Manufacturer (medium)
        """
        score = 0.0
        
        # Model match (CRITICAL - must match exactly)
        search_model = search_components.get('model', '')
        candidate_model = candidate_components.get('model', '')
        
        if search_model and candidate_model:
            if search_model == candidate_model:
                score += 5.0  # Perfect model match
                logger.debug(f"✅ Model match: {search_model} = {candidate_model}")
            elif self._models_similar(search_model, candidate_model):
                score += 2.0  # Similar models
                logger.debug(f"⚠️ Similar models: {search_model} ~ {candidate_model}")
            else:
                score -= 3.0  # Wrong model is serious penalty
                logger.debug(f"❌ Model mismatch: {search_model} ≠ {candidate_model}")
        
        # Series match (IMPORTANT)
        search_series = search_components.get('series', '')
        candidate_series = candidate_components.get('series', '')
        
        if search_series and candidate_series:
            if search_series in candidate_series or candidate_series in search_series:
                score += 3.0  # Series match
                logger.debug(f"✅ Series match: '{search_series}' <-> '{candidate_series}'")
            elif self._series_similar(search_series, candidate_series):
                score += 1.5  # Partial series match
                logger.debug(f"⚠️ Similar series: '{search_series}' ~ '{candidate_series}'")
        
        # Manufacturer match (HELPFUL but not critical)
        search_mfg = search_components.get('manufacturer', '')
        candidate_mfg = candidate_components.get('manufacturer', '')
        
        if search_mfg and candidate_mfg:
            if search_mfg == candidate_mfg:
                score += 2.0  # Same manufacturer
                logger.debug(f"✅ Manufacturer match: {search_mfg}")
            else:
                score -= 1.0  # Different manufacturer is penalty
                logger.debug(f"❌ Manufacturer mismatch: {search_mfg} ≠ {candidate_mfg}")
        
        return score
    
    def _make_component_decision(self, search_components: dict, bold_score: float, dropdown_score: float, dropdown_text: str) -> dict:
        """Apply decision rules based on component analysis."""
        
        # Rule 1: Model number mismatch in dropdown = use bold
        search_model = search_components.get('model', '')
        if search_model and search_model not in dropdown_text.upper():
            return {
                'choice': 'bold',
                'reason': f'Dropdown missing model "{search_model}" - using P1 results'
            }
        
        # Rule 2: If dropdown has significantly better score, use it
        if dropdown_score >= 8.0 and bold_score < 4.0:
            return {
                'choice': 'dropdown', 
                'reason': f'Dropdown much better: {dropdown_score:.1f} vs {bold_score:.1f}'
            }
        
        # Rule 3: If bold has good score and dropdown is poor, use bold
        if bold_score >= 5.0 and dropdown_score < 3.0:
            return {
                'choice': 'bold',
                'reason': f'Bold better: {bold_score:.1f} vs {dropdown_score:.1f}'
            }
        
        # Rule 4: Generic search term = prefer dropdown specificity
        if self._is_generic_search(search_components) and dropdown_score >= 4.0:
            return {
                'choice': 'dropdown',
                'reason': 'Generic search - dropdown provides specificity'
            }
        
        # Default: Use bold (preserve original search intent)
        return {
            'choice': 'bold',
            'reason': f'Default to original search intent (Bold: {bold_score:.1f}, Dropdown: {dropdown_score:.1f})'
        }
    
    def _models_similar(self, model1: str, model2: str) -> bool:
        """Check if two model numbers are similar enough."""
        import re
        
        # Extract numbers from both models
        nums1 = re.findall(r'\d+', model1)
        nums2 = re.findall(r'\d+', model2)
        
        if not nums1 or not nums2:
            return False
        
        # Check if main numbers are close (within 10%)
        try:
            main1 = int(nums1[0])
            main2 = int(nums2[0])
            diff_pct = abs(main1 - main2) / max(main1, main2)
            return diff_pct <= 0.1  # Within 10%
        except:
            return False
    
    def _series_similar(self, series1: str, series2: str) -> bool:
        """Check if two series names are similar."""
        # Simple word overlap check
        words1 = set(series1.split())
        words2 = set(series2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        
        return overlap / total >= 0.5  # At least 50% word overlap
    
    def _is_generic_search(self, components: dict) -> bool:
        """Check if search is generic (lacks specific manufacturer or detailed model)."""
        has_manufacturer = bool(components.get('manufacturer'))
        has_detailed_model = bool(components.get('model') and len(components['model']) > 2)
        
        return not (has_manufacturer and has_detailed_model)
    
    # ============== DUAL-SESSION HELPER METHODS ==============
    
    def _create_new_driver(self):
        """Create a new WebDriver instance for dual-session scraping."""
        # Create Chrome options with performance optimizations
        options = webdriver.ChromeOptions()
        
        # Get performance-optimized browser settings
        browser_optimizations = self.performance_optimizer.optimize_browser_settings()
        
        # Apply headless mode if configured
        if getattr(self.config, 'headless', False):
            options.add_argument('--headless=new')
            logger.info("Running in HEADLESS mode")
        else:
            logger.info("Running in EXPLICIT mode (visible browser)")
        
        # Apply performance optimizations
        for arg in browser_optimizations.get('chrome_args', []):
            options.add_argument(arg)
        
        # Set window size for consistent behavior
        options.add_argument('--window-size=1920,1080')
        
        try:
            # Try webdriver-manager first
            logger.info("Attempting ChromeDriver setup via webdriver-manager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("✅ ChromeDriver initialized via webdriver-manager")
            
        except Exception as wdm_error:
            logger.warning(f"WebDriver Manager failed: {wdm_error}")
            
            try:
                # Fallback: try system ChromeDriver
                logger.info("Attempting fallback ChromeDriver initialization...")
                driver = webdriver.Chrome(options=options)
                logger.info("✅ ChromeDriver initialized via system PATH")
                
            except Exception as system_error:
                logger.error(f"System ChromeDriver failed: {system_error}")
                
                # Final fallback: try common binary locations
                possible_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe",
                    "chromedriver.exe"
                ]
                
                driver = None
                for path in possible_paths:
                    try:
                        if os.path.exists(path):
                            logger.info(f"Trying ChromeDriver at: {path}")
                            service = Service(path)
                            driver = webdriver.Chrome(service=service, options=options)
                            logger.info(f"✅ ChromeDriver initialized from: {path}")
                            break
                    except Exception as binary_error:
                        logger.warning(f"Failed with {path}: {binary_error}")
                        continue
                
                if not driver:
                    raise Exception("Could not initialize ChromeDriver with any method")
        
        # Configure timeouts and settings
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Anti-bot protection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _run_session_p1_only(self, driver, product: ProductInput) -> dict:
        """Run P1-only session: type product name and press Enter directly."""
        try:
            # Temporarily switch to this driver
            original_driver = self.driver
            self.driver = driver
            
            # Set shorter timeouts for session to prevent hanging
            driver.set_page_load_timeout(15)  # Shorter timeout
            driver.implicitly_wait(5)         # Shorter wait
            
            logger.info("🅰️📍 Navigating to ZAP...")
            try:
                # Use direct navigation with timeout instead of _navigate_to_zap() 
                driver.get("https://www.zap.co.il/")
                time.sleep(2)  # Brief wait for page load
                logger.info("🅰️✅ Navigation complete")
            except Exception as nav_error:
                logger.error(f"🅰️❌ Navigation failed: {nav_error}")
                raise
            
            logger.info("🅰️🔍 Starting P1-only search...")
            self._search_product_p1_only(product.name)
            logger.info("🅰️✅ Search complete")
            
            logger.info("🅰️⏳ Waiting for results page...")
            self._wait_for_page_ready()
            logger.info("🅰️✅ Results page ready")
            
            logger.info("🅰️📝 Extracting listing names...")
            listing_names = self._extract_listing_names_from_results()
            logger.info(f"🅰️✅ Extracted {len(listing_names)} listings")
            
            logger.info("🅰️🔗 Looking for comparison button...")
            comparison_url = self._click_comparison_button()
            logger.info(f"🅰️✅ Comparison URL: {comparison_url is not None}")
            
            result = {
                'listing_names': listing_names,
                'comparison_url': comparison_url,
                'vendor_offers': []
            }
            
            if comparison_url:
                logger.info("🅰️🏪 Processing vendor offers...")
                result['vendor_offers'] = self._process_comparison_page(comparison_url, product)
                logger.info(f"🅰️✅ Found {len(result['vendor_offers'])} vendor offers")
            
            return result
            
        except Exception as e:
            logger.error(f"Session A (P1-only) failed: {e}")
            # Immediately try to close this driver if it's stuck
            try:
                if driver:
                    logger.warning("🚨 Emergency cleanup of Session A driver")
                    driver.quit()
            except:
                pass
            return {'listing_names': [], 'comparison_url': None, 'vendor_offers': []}
        finally:
            # Restore original driver
            self.driver = original_driver
    
    def _run_session_p1_p2(self, driver, product: ProductInput) -> dict:
        """Run P1→P2 session: type product name, select from dropdown, then proceed."""
        try:
            # Temporarily switch to this driver
            original_driver = self.driver
            self.driver = driver
            
            # Navigate to ZAP
            self._navigate_to_zap()
            
            # Search for product
            self._search_product(product.name)
            
            # Select from dropdown (P2 phase)
            selected = self._select_from_dropdown(product.name)
            if not selected:
                logger.warning(f"No dropdown selection for {product.name} in Session B")
            
            # Wait for results page
            self._wait_for_page_ready()
            
            # Extract listing names from results page
            listing_names = self._extract_listing_names_from_results()
            
            # Click comparison button to get to vendor list
            comparison_url = self._click_comparison_button()
            
            result = {
                'listing_names': listing_names,
                'comparison_url': comparison_url,
                'vendor_offers': []
            }
            
            if comparison_url:
                result['vendor_offers'] = self._process_comparison_page(comparison_url, product)
            
            return result
            
        except Exception as e:
            logger.error(f"Session B (P1→P2) failed: {e}")
            # Immediately try to close this driver if it's stuck
            try:
                if driver:
                    logger.warning("🚨 Emergency cleanup of Session B driver")
                    driver.quit()
            except:
                pass
            return {'listing_names': [], 'comparison_url': None, 'vendor_offers': []}
        finally:
            # Restore original driver
            self.driver = original_driver
    
    def _search_product_p1_only(self, product_name: str) -> None:
        """Search for product - P1 only (type and press Enter immediately)."""
        logger.info(f"🔍 P1-ONLY SEARCH: '{product_name}'")
        
        try:
            # Reuse existing search box finding logic
            search_box = None
            search_selectors = [
                "input[type='search']",
                "input[type='text']",
                "input[placeholder*='חיפוש']",
                "input[placeholder*='חפש']", 
                "input.search-input",
                "input#search"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not search_box:
                raise NoSuchElementException("Could not find search box")
            
            # Click to focus, clear, type, and immediately press Enter
            search_box.click()
            time.sleep(0.5)
            search_box.clear()
            search_box.send_keys(product_name)
            time.sleep(0.5)  # Brief pause
            search_box.send_keys(Keys.RETURN)  # Press Enter immediately
            
            logger.info(f"✅ P1-ONLY: Typed '{product_name}' and pressed Enter")
            
        except Exception as e:
            logger.error(f"Error in P1-only search: {e}")
            raise
    
    def _extract_listing_names_from_results(self) -> List[str]:
        """Extract product listing names from ZAP results page."""
        try:
            time.sleep(3)  # Wait for page to load
            
            # Look for product listing elements
            listing_selectors = [
                "[class*='product-title']",
                "[class*='product-name']", 
                "[class*='item-title']",
                "h3", "h4",
                "a[href*='/product/']",
                ".product-link"
            ]
            
            listing_names = []
            
            for selector in listing_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        if text and 5 < len(text) < 100 and text not in listing_names:
                            listing_names.append(text)
                            if len(listing_names) >= 10:  # Limit to top 10
                                break
                    except:
                        continue
                
                if len(listing_names) >= 10:
                    break
            
            logger.info(f"📝 Extracted {len(listing_names)} listing names")
            return listing_names[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error extracting listing names: {e}")
            return []
    
    def _compare_session_results(self, original_product: str, session_a: dict, session_b: dict) -> dict:
        """Compare results from both sessions and choose the best one."""
        logger.info("🏁 COMPARING SESSION RESULTS")
        
        # Parse original product components
        original_components = self._parse_product_components(original_product)
        
        # Score Session A
        score_a = self._score_session_results(original_components, session_a['listing_names'])
        logger.info(f"🅰️ Session A score: {score_a:.2f}")
        
        # Score Session B  
        score_b = self._score_session_results(original_components, session_b['listing_names'])
        logger.info(f"🅱️ Session B score: {score_b:.2f}")
        
        # Choose winner
        if score_a >= score_b:
            winner = {
                'session': 'A (P1-only)',
                'score': score_a,
                'result': ProductScrapingResult(
                    input_product=ProductInput(name=original_product, original_price=0, row_number=1),
                    vendor_offers=session_a['vendor_offers'],
                    status="success" if session_a['vendor_offers'] else "no_results"
                )
            }
        else:
            winner = {
                'session': 'B (P1→P2)',
                'score': score_b,
                'result': ProductScrapingResult(
                    input_product=ProductInput(name=original_product, original_price=0, row_number=1),
                    vendor_offers=session_b['vendor_offers'],
                    status="success" if session_b['vendor_offers'] else "no_results"
                )
            }
        
        return winner
    
    def _score_session_results(self, original_components: dict, listing_names: List[str]) -> float:
        """Score how well listing names match the original product components."""
        if not listing_names:
            return 0.0
        
        total_score = 0.0
        manufacturer = original_components.get('manufacturer', '').lower()
        series = original_components.get('series', '').lower()
        model = original_components.get('model', '').lower()
        
        for listing in listing_names:
            listing_lower = listing.lower()
            listing_score = 0.0
            
            # Score manufacturer match
            if manufacturer and manufacturer in listing_lower:
                listing_score += 0.4
            
            # Score series match  
            if series and series in listing_lower:
                listing_score += 0.3
            
            # Score model match
            if model and model in listing_lower:
                listing_score += 0.3
            
            total_score += listing_score
        
        # Average score across all listings
        return total_score / len(listing_names) if listing_names else 0.0

    # ==========================================
    # HYBRID SEARCH STRATEGY METHODS
    # ==========================================
    
    def _extract_model_id_from_name(self, product_name: str) -> Optional[str]:
        """Extract model ID if the product name contains a direct ZAP model reference."""
        # Check if product name contains a model ID pattern
        model_id_patterns = [
            r'modelid[=:](\d+)',
            r'model[=:](\d+)', 
            r'id[=:](\d+)',
            r'^(\d{7})$',  # 7-digit model ID
            r'zap\.co\.il/model\.aspx\?modelid=(\d+)'
        ]
        
        for pattern in model_id_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                model_id = match.group(1)
                logger.info(f"📋 Extracted model ID: {model_id} from '{product_name}'")
                return model_id
        
        return None

    def _scrape_direct_model(self, product: ProductInput, model_id: str) -> ProductScrapingResult:
        """Scrape product using direct model ID access."""
        logger.info(f"🎯 DIRECT MODEL ACCESS: modelid={model_id}")
        
        try:
            # Navigate directly to model page
            model_url = f"https://www.zap.co.il/model.aspx?modelid={model_id}"
            logger.info(f"Navigating to: {model_url}")
            self.driver.get(model_url)
            
            # Wait for page to load
            self._wait_for_page_ready()
            
            # Check if page loaded successfully
            if "404" in self.driver.title or "שגיאה" in self.driver.page_source:
                logger.warning(f"❌ Model ID {model_id} not found (404)")
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="no_results"
                )
            
            # Extract vendor offers directly from model page
            vendor_offers = self._extract_vendors_from_model_page(product)
            
            logger.info(f"✅ Direct model access found {len(vendor_offers)} vendors")
            
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=vendor_offers,
                status="success" if vendor_offers else "no_results"
            )
            
        except Exception as e:
            logger.error(f"❌ Direct model access failed: {e}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )

    def _scrape_smart_search(self, product: ProductInput) -> ProductScrapingResult:
        """Smart search with variant detection and selection."""
        logger.info(f"🔍 SMART SEARCH: {product.name}")
        
        try:
            # Navigate to search page
            search_url = f"https://www.zap.co.il/models.aspx?sog=e-airconditioner&keyword={product.name.replace(' ', '%20')}"
            logger.info(f"Smart search URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for results
            self._wait_for_page_ready()
            
            # Detect product variants
            variants = self._detect_product_variants(product.name)
            
            if not variants:
                logger.warning(f"❌ No variants found for: {product.name}")
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="no_results"
                )
            
            logger.info(f"🔍 Found {len(variants)} product variants")
            
            # Select best matching variant
            best_variant = self._select_best_variant(product.name, variants)
            
            if not best_variant:
                logger.warning(f"❌ No suitable variant found")
                return ProductScrapingResult(
                    input_product=product,
                    vendor_offers=[],
                    status="no_results"
                )
            
            logger.info(f"🎯 Selected variant: {best_variant['name']} ({best_variant['vendors']} vendors)")
            
            # Navigate to selected variant and extract vendors
            vendor_offers = self._extract_vendors_from_variant(product, best_variant)
            
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=vendor_offers,
                status="success" if vendor_offers else "no_results"
            )
            
        except Exception as e:
            logger.error(f"❌ Smart search failed: {e}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )

    def _detect_product_variants(self, product_name: str) -> List[Dict[str, Any]]:
        """Detect product variants on search results page."""
        variants = []
        
        try:
            # FIXED selectors based on manual verification (2025)
            variant_selectors = [
                # CORRECT ZAP interface structure (verified manually)
                ".ItemsFound.RegularView .ModelRow",  # Actual product cards (32 found)
                ".ModelRow",  # Individual product rows
                ".ItemsFound .ModelRow",  # Products in results container
                # Fallback selectors
                ".MainDiv .Martef .MartefItem",  # Old structure
                ".MartefItemInfo",  # Product info sections
                "div[class*='model-item']",
                "div[class*='product-item']", 
                ".model-box"
            ]
            
            variant_elements = []
            for selector in variant_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        variant_elements = elements
                        logger.info(f"Found variants with selector: {selector}")
                        break
                except:
                    continue
            
            if not variant_elements:
                # Fallback: look for any clickable product links
                try:
                    variant_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='model.aspx']")
                    logger.info(f"Fallback: Found {len(variant_elements)} model links")
                except:
                    pass
            
            # Extract variant information
            for element in variant_elements[:10]:  # Limit to first 10 variants
                try:
                    # Extract variant name - FIXED for ModelRow structure
                    name_selectors = [
                        # CORRECT selectors for .ModelRow elements (verified)
                        ".ModelRow",  # The element itself contains product text
                        "a",  # Links within ModelRow
                        "img[alt]",  # Product image alt text
                        ".title",  # Product title
                        # Fallback selectors
                        ".MartefItemInfo",  # Old structure
                        ".MoreDetailsLink a",  # Old structure
                        "h3", "h4", "[class*='name']"
                    ]
                    variant_name = None
                    
                    # First try: Get text directly from ModelRow element
                    variant_name = element.text.strip()
                    
                    # If direct text is too short or empty, try child elements
                    if not variant_name or len(variant_name) < 10:
                        for sel in name_selectors:
                            try:
                                name_elem = element.find_element(By.CSS_SELECTOR, sel)
                                # Try alt text first, then text content
                                candidate_name = name_elem.get_attribute('alt') or name_elem.text.strip()
                                if candidate_name and len(candidate_name) > 3:  # Valid product name
                                    variant_name = candidate_name
                                    break
                            except:
                                continue
                    
                    if not variant_name:
                        continue
                    
                    # Extract vendor count
                    vendor_count = 0
                    vendor_patterns = [r'(\d+)\s*(?:חנויות|ספקים|vendors)', r'(\d+)\s*stores']
                    element_text = element.text
                    
                    for pattern in vendor_patterns:
                        match = re.search(pattern, element_text, re.IGNORECASE)
                        if match:
                            vendor_count = int(match.group(1))
                            break
                    
                    # Extract model URL/ID - updated for current ZAP interface
                    model_url = None
                    model_link_selectors = [
                        # Updated for 2025 ZAP interface - fs.aspx links
                        ".MartefItem a[href*='fs.aspx']",  # Product card links  
                        "a[href*='fs.aspx']",  # Any fs.aspx link
                        "a[href*='fs/mp']",  # Marketplace links
                        # Legacy model.aspx links
                        ".MoreDetailsLink a[href*='model.aspx']",  # ZAP detail links
                        ".MartefItem a[href*='model.aspx']",  # Product card links
                        "a[href*='model.aspx']",  # Any model link
                        "a[href*='models.aspx']"  # Search result links
                    ]
                    
                    for sel in model_link_selectors:
                        try:
                            link_elem = element.find_element(By.CSS_SELECTOR, sel)
                            model_url = link_elem.get_attribute('href')
                            if model_url:
                                break
                        except:
                            continue
                    
                    # Calculate similarity to search term
                    similarity = self._calculate_similarity(product_name, variant_name)
                    
                    variant = {
                        'name': variant_name,
                        'vendors': vendor_count,
                        'url': model_url,
                        'element': element,
                        'similarity': similarity
                    }
                    
                    variants.append(variant)
                    
                except Exception as e:
                    logger.debug(f"Error extracting variant info: {e}")
                    continue
            
            # Sort by similarity and vendor count
            variants.sort(key=lambda x: (x['similarity'], x['vendors']), reverse=True)
            
            logger.info(f"🔍 Detected {len(variants)} variants:")
            for i, variant in enumerate(variants[:5], 1):
                logger.info(f"   {i}. {variant['name']} ({variant['vendors']} vendors, {variant['similarity']:.2f} similarity)")
            
            return variants
            
        except Exception as e:
            logger.error(f"Error detecting variants: {e}")
            return []

    def _select_best_variant(self, search_term: str, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best matching variant based on similarity and vendor count."""
        if not variants:
            return None
        
        # Filter variants with reasonable similarity (>0.3) and vendors (>0)
        good_variants = [v for v in variants if v['similarity'] > 0.3 and v['vendors'] > 0]
        
        if not good_variants:
            # Fallback to any variant with vendors
            good_variants = [v for v in variants if v['vendors'] > 0]
        
        if not good_variants:
            return None
        
        # Return highest scoring variant (already sorted by similarity and vendor count)
        best = good_variants[0]
        logger.info(f"🎯 Best variant: '{best['name']}' (similarity: {best['similarity']:.2f}, vendors: {best['vendors']})")
        
        return best

    def _calculate_similarity(self, search_term: str, variant_name: str) -> float:
        """Calculate similarity between search term and variant name."""
        search_lower = search_term.lower()
        variant_lower = variant_name.lower()
        
        # Exact match
        if search_lower == variant_lower:
            return 1.0
        
        # Contains match
        if search_lower in variant_lower or variant_lower in search_lower:
            return 0.8
        
        # Word overlap scoring
        search_words = set(search_lower.split())
        variant_words = set(variant_lower.split())
        
        if not search_words or not variant_words:
            return 0.0
        
        common_words = search_words.intersection(variant_words)
        similarity = len(common_words) / len(search_words.union(variant_words))
        
        return similarity

    def _extract_vendors_from_model_page(self, product: ProductInput) -> List[VendorOffer]:
        """Extract vendor offers from a direct model page."""
        vendor_offers = []
        
        try:
            # Wait for vendor content to load
            time.sleep(5)
            
            # Try modern card-based extraction first
            vendor_offers = self._extract_vendors_card_layout(product)
            if vendor_offers:
                return vendor_offers
            
            # Fallback to traditional table-based extraction
            logger.info("🔄 Falling back to traditional vendor extraction")
            
            # Updated selectors for current ZAP interface (2025)
            vendor_selectors = [
                # New ZAP interface structure
                ".MainDiv .MainContent .site_logo",  # Vendor cards
                ".MainDiv .MainContent div[class*='vendor']",  # Vendor divs
                ".MainDiv .MainContent a[href*='/fs.aspx']",  # Vendor links
                "div[class*='newssite-']",  # Vendor site containers
                # Fallback to older selectors
                "tr[class*='vendor']",
                "tr[class*='store']", 
                "tbody tr",
                ".vendor-row",
                "[data-vendor]"
            ]
            
            vendor_rows = []
            for selector in vendor_selectors:
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if rows:
                        vendor_rows = rows
                        logger.info(f"Found vendor rows with selector: {selector}")
                        break
                except:
                    continue
            
            if not vendor_rows:
                logger.warning("❌ No vendor rows found on model page")
                return []
            
            logger.info(f"📊 Processing {len(vendor_rows)} vendor rows")
            
            for row in vendor_rows:
                try:
                    # Extract vendor name - updated for current ZAP interface
                    name_selectors = [
                        # New ZAP interface selectors
                        "img[alt]",  # Site logo images with alt text
                        ".site_logo img[alt]",  # Vendor logo with alt
                        "a[title]",  # Links with vendor title
                        # Fallback selectors
                        ".vendor-name", 
                        ".store-name", 
                        "td:first-child", 
                        "a"
                    ]
                    vendor_name = None
                    
                    for sel in name_selectors:
                        try:
                            name_elem = row.find_element(By.CSS_SELECTOR, sel)
                            # Try to get alt text first (for images), then text content
                            vendor_name = name_elem.get_attribute('alt') or name_elem.get_attribute('title') or name_elem.text.strip()
                            if vendor_name and len(vendor_name) > 1:  # Valid vendor name
                                break
                        except:
                            continue
                    
                    if not vendor_name:
                        continue
                    
                    # Extract price - updated for current ZAP interface
                    price_selectors = [
                        # New ZAP interface selectors for price
                        "a[href*='/fs.aspx']",  # Vendor links containing prices
                        ".MainContent a",  # Any link in main content
                        "[class*='price']",  # Price classes
                        ".price",  # Standard price class
                        "td:last-child"  # Table fallback
                    ]
                    price = 0.0
                    
                    for sel in price_selectors:
                        try:
                            price_elem = row.find_element(By.CSS_SELECTOR, sel)
                            price_text = price_elem.text.strip()
                            # Look for Hebrew shekel symbol and numbers
                            price_match = re.search(r'([\d,]+(?:\.\d+)?)\s*₪', price_text) or re.search(r'₪\s*([\d,]+(?:\.\d+)?)', price_text) or re.search(r'([\d,]+)', price_text)
                            if price_match:
                                price = float(price_match.group(1).replace(',', ''))
                                if price > 0:  # Valid price found
                                    break
                        except:
                            continue
                    
                    # Extract URL
                    vendor_url = ""
                    try:
                        link_elem = row.find_element(By.CSS_SELECTOR, "a")
                        vendor_url = link_elem.get_attribute('href') or ""
                    except:
                        pass
                    
                    if vendor_name and price > 0:
                        offer = VendorOffer(
                            vendor_name=vendor_name,
                            product_name=f"{product.name} - {vendor_name}",
                            price=price,
                            url=vendor_url
                        )
                        vendor_offers.append(offer)
                        
                except Exception as e:
                    logger.debug(f"Error processing vendor row: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(vendor_offers)} vendor offers from model page")
            return vendor_offers
            
        except Exception as e:
            logger.error(f"Error extracting vendors from model page: {e}")
            return []

    def _extract_vendors_from_variant(self, product: ProductInput, variant: Dict[str, Any]) -> List[VendorOffer]:
        """Extract vendor offers from selected variant."""
        try:
            # If variant has direct URL, navigate to it
            if variant.get('url'):
                logger.info(f"🔗 Navigating to variant URL: {variant['url']}")
                self.driver.get(variant['url'])
                self._wait_for_page_ready()
                return self._extract_vendors_from_model_page(product)
            
            # Otherwise, click on the variant element
            elif variant.get('element'):
                logger.info(f"🖱️ Clicking on variant element")
                variant['element'].click()
                self._wait_for_page_ready()
                return self._extract_vendors_from_model_page(product)
            
            else:
                logger.warning("❌ No way to access variant")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting vendors from variant: {e}")
            return []

    def _extract_vendors_card_layout(self, product: ProductInput) -> List[VendorOffer]:
        """Extract vendors from modern ZAP card-based layout."""
        vendor_offers = []
        
        try:
            logger.info("🎯 Attempting modern card-based vendor extraction")
            
            # Scroll down to load all vendor cards (lazy loading)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Look for vendor links containing prices - updated for 2025 interface
            vendor_link_selectors = [
                "a[href*='/fs.aspx']",  # Primary fs.aspx links
                "a[href*='fs/mp']",     # Marketplace links
                ".MainContent a"        # Any link in main content
            ]
            
            vendor_links = []
            for selector in vendor_link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        vendor_links = links
                        logger.info(f"Found vendor links with selector: {selector}")
                        break
                except:
                    continue
            
            if not vendor_links:
                logger.info("🔍 No vendor links found, trying price-based detection")
                # Alternative: look for any links with prices
                all_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
                vendor_links = [link for link in all_links if '₪' in link.text]
            
            logger.info(f"📊 Found {len(vendor_links)} potential vendor links")
            
            processed_vendors = set()  # Avoid duplicates
            
            for link in vendor_links:
                try:
                    # Extract price from link text
                    link_text = link.text.strip()
                    price_match = re.search(r'([\d,]+(?:\.\d+)?)\s*₪', link_text)
                    
                    if not price_match:
                        continue
                    
                    price = float(price_match.group(1).replace(',', ''))
                    if price <= 0:
                        continue
                    
                    # Extract vendor name from nearby elements
                    vendor_name = self._extract_vendor_name_from_context(link)
                    
                    if not vendor_name or vendor_name in processed_vendors:
                        continue
                    
                    # Get vendor URL
                    vendor_url = link.get_attribute('href') or ""
                    
                    # Create vendor offer
                    offer = VendorOffer(
                        vendor_name=vendor_name,
                        product_name=f"{product.name} - {vendor_name}",
                        price=price,
                        url=vendor_url
                    )
                    
                    vendor_offers.append(offer)
                    processed_vendors.add(vendor_name)
                    
                    logger.debug(f"✅ Added vendor: {vendor_name} - ₪{price:,.0f}")
                    
                except Exception as e:
                    logger.debug(f"Error processing vendor link: {e}")
                    continue
            
            logger.info(f"✅ Card-based extraction found {len(vendor_offers)} vendors")
            return vendor_offers
            
        except Exception as e:
            logger.error(f"Error in card-based extraction: {e}")
            return []

    def _extract_vendor_name_from_context(self, link_element) -> Optional[str]:
        """Extract vendor name from context around a price link."""
        try:
            # Strategy 1: Look for nearby img with alt text (vendor logo)
            try:
                parent = link_element.find_element(By.XPATH, "..")
                img = parent.find_element(By.CSS_SELECTOR, "img[alt]")
                vendor_name = img.get_attribute('alt').strip()
                if vendor_name and len(vendor_name) > 1:
                    return vendor_name
            except:
                pass
            
            # Strategy 2: Look for vendor name in link's own attributes
            try:
                title = link_element.get_attribute('title')
                if title and 'מחיר' not in title and len(title) > 1:
                    return title.strip()
            except:
                pass
            
            # Strategy 3: Extract from URL
            try:
                url = link_element.get_attribute('href')
                if url:
                    # Look for site parameter in URL
                    site_match = re.search(r'site=([^&]+)', url)
                    if site_match:
                        return site_match.group(1).replace('%20', ' ')
            except:
                pass
            
            # Strategy 4: Look in parent container for text
            try:
                parent = link_element.find_element(By.XPATH, "..")
                parent_text = parent.text.strip()
                # Extract first line or meaningful text
                lines = [line.strip() for line in parent_text.split('\n') if line.strip()]
                for line in lines:
                    if '₪' not in line and len(line) > 1 and len(line) < 50:
                        return line
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting vendor name from context: {e}")
            return None
    
    # ==========================================
    # SIMPLIFIED BUTTON-TYPE ARCHITECTURE
    # ==========================================
    
    def scrape_product_button_type(self, product: ProductInput) -> ProductScrapingResult:
        """
        Simplified button-type scraping architecture.
        Uses simple search + Enter, then processes by button types (T.1, T.2, T.3).
        """
        logger.info(f"🎯 BUTTON-TYPE SCRAPING: {product.name}")
        
        try:
            # Step 1: Navigate to ZAP
            self._navigate_to_zap()
            
            # Step 2: NEW - Dropdown search with component matching
            self._dropdown_search_and_select(product)
            
            # Step 3: Wait for filtered results
            self._wait_for_filtered_results()
            
            # Step 4: Scroll to footer to load all listings
            self._scroll_to_load_all_listings()
            
            # Step 5: Find and validate listings using 2-artifact rule
            validated_listings = self._find_validated_listings()
            
            # Step 6: Process each listing by button type
            all_vendor_offers = []
            for listing in validated_listings:
                offers = self._process_listing_by_button_type(listing, product)
                all_vendor_offers.extend(offers)
            
            logger.info(f"✅ Button-type scraping found {len(all_vendor_offers)} total vendors")
            
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=all_vendor_offers,
                status="success" if all_vendor_offers else "no_results"
            )
            
        except Exception as e:
            logger.error(f"❌ Button-type scraping failed: {e}")
            return ProductScrapingResult(
                input_product=product,
                vendor_offers=[],
                status="error",
                error_message=str(e)
            )
    
    def _dropdown_search_and_select(self, product: ProductInput) -> None:
        """
        NEW: Dropdown-based search with component matching.
        Types search term, waits for dropdown, scores options, selects best match.
        """
        search_term = product.search_term
        components = product.search_components
        
        logger.info(f"🔍 Dropdown search for: {search_term}")
        logger.info(f"🧩 Target components: {components}")
        
        try:
            # Navigate to ZAP main page first
            self.driver.get("https://www.zap.co.il")
            time.sleep(2)
            
            # Find search field
            search_field = None
            search_selectors = [
                "input[type='search']",
                "input[placeholder*='חיפוש']",
                "input[placeholder*='חפש']",
                "input.search-input",
                "input#search",
                "input[name='search']",
                "input[type='text']"
            ]
            
            for selector in search_selectors:
                try:
                    search_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found search field with selector: {selector}")
                    break
                except:
                    continue
            
            if not search_field:
                raise Exception("Could not find search field")
            
            # STEP 1: Click to focus and clear field
            search_field.click()
            time.sleep(0.5)
            search_field.clear()
            
            # STEP 2: Type search term character by character to trigger dropdown
            logger.info(f"📝 Typing search term: {search_term}")
            for i, char in enumerate(search_term):
                search_field.send_keys(char)
                # Small delay between characters to allow dropdown to update
                time.sleep(0.05)
                
                # After typing enough characters, pause to let dropdown populate
                if i == 10:  # After "Electra Tit"
                    logger.info("⏳ Pausing to let dropdown populate...")
                    time.sleep(1.5)
            
            logger.info(f"✅ Typed full search term: {search_term}")
            
            # STEP 2: Wait for dropdown to appear with retries
            logger.info("⏳ Waiting for dropdown to appear...")
            dropdown_appeared = False
            
            for attempt in range(3):  # Try 3 times
                time.sleep(1.5)  # Wait a bit
                
                # Quick check if dropdown appeared
                try:
                    dropdown_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "div.autoCompleteResults, .autoCompleteResults a, .autocomplete-suggestions, .ui-autocomplete, [class*='suggestion'], [class*='autocomplete']")
                    if dropdown_elements:
                        logger.info(f"✅ Dropdown detected on attempt {attempt + 1}")
                        dropdown_appeared = True
                        break
                except:
                    pass
                    
                # If dropdown not appeared, try clicking search field again to trigger it
                if attempt > 0:
                    logger.info("🔄 Re-clicking search field to trigger dropdown...")
                    search_field.click()
                    time.sleep(0.5)
                    
                logger.info(f"⏳ Dropdown attempt {attempt + 1}/3...")
            
            if not dropdown_appeared:
                logger.warning("⚠️ Dropdown not detected, but proceeding with search...")
                # Log page structure for debugging
                try:
                    page_source_sample = self.driver.page_source[:2000]
                    logger.debug(f"Page source sample: {page_source_sample}")
                    
                    # Check for any div elements that might be the dropdown
                    all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                    logger.info(f"Total div elements on page: {len(all_divs)}")
                    
                    # Check for elements with 'auto' or 'suggest' in class name
                    auto_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='auto'], [class*='suggest']")
                    logger.info(f"Elements with 'auto'/'suggest' in class: {len(auto_elements)}")
                    
                except Exception as e:
                    logger.debug(f"Debug logging failed: {e}")
            
            # STEP 3: Find dropdown options and score them
            best_option = self._find_best_dropdown_option(components)
            
            if best_option:
                # STEP 3.5: Prefer keyboard-driven selection (ArrowDown + Enter)
                try:
                    logger.info("Trying keyboard selection (ArrowDown + Enter) before click fallback...")
                    # Build a list of currently visible dropdown options
                    option_selectors = (
                        "div.autoCompleteResults a, .autoCompleteResults .autoCompleteResult, "
                        ".autocomplete-suggestions .autocomplete-suggestion, "
                        "ul.ui-autocomplete li, [role='listbox'] [role='option']"
                    )
                    visible_options = [el for el in self.driver.find_elements(By.CSS_SELECTOR, option_selectors)
                                       if el.is_displayed() and el.text.strip()]
                    option_texts = [el.text.strip() for el in visible_options]

                    # Locate index of the option text we decided is best
                    target_index = -1
                    for idx, text in enumerate(option_texts):
                        if text.strip() == best_option['text'].strip():
                            target_index = idx
                            break

                    if target_index >= 0:
                        # Ensure the search field has focus
                        try:
                            active = self.driver.switch_to.active_element
                            # If focus is not on an input, re-focus search field
                            if active.tag_name.lower() not in ['input', 'textarea']:
                                raise Exception("Active element is not input")
                        except Exception:
                            # Re-find the search field
                            for sel in [
                                "input[type='search']", "input[placeholder*='חיפוש']", "input[placeholder*='חפש']",
                                "input.search-input", "input#search", "input[name='search']", "input[type='text']"
                            ]:
                                try:
                                    search_field = WebDriverWait(self.driver, 2).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
                                    )
                                    search_field.click()
                                    break
                                except Exception:
                                    continue

                        # Send ArrowDown target_index+1 times to highlight the intended option
                        for _ in range(target_index + 1):
                            search_field.send_keys(Keys.ARROW_DOWN)
                            time.sleep(0.1)
                        # Confirm selection
                        search_field.send_keys(Keys.ENTER)
                        logger.info("Confirmed dropdown selection with Enter")
                        time.sleep(2.5)
                        current_url = self.driver.current_url
                        logger.info(f"URL after Enter: {current_url}")
                        if "model.aspx?modelid=" in current_url or "compmodels.aspx?modelid=" in current_url:
                            return True
                    else:
                        logger.info("Best option not found in currently visible list; using click fallback")
                except Exception as e:
                    logger.debug(f"Keyboard selection attempt failed: {e}")

                # STEP 4: Click best option with ENHANCED click interception handling
                logger.info(f"🎯 Selecting best option: {best_option['text'][:100]}...")
                
                # FIRST: Always remove ALL potential blocking masks/overlays
                logger.info("🔧 Removing all blocking overlays...")
                self.driver.execute_script("""
                    // Remove ALL autocomplete masks and overlays
                    var masks = document.querySelectorAll('.autoCompleteMask, .overlay, .modal-backdrop, [class*="mask"]');
                    masks.forEach(function(mask) {
                        mask.style.display = 'none';
                        mask.style.visibility = 'hidden';
                        mask.style.pointerEvents = 'none';
                        mask.remove();
                    });
                    
                    // Force all autocomplete/suggestion containers to be clickable
                    var containers = document.querySelectorAll('[class*="autocomplete"], [class*="suggestion"]');
                    containers.forEach(function(container) {
                        container.style.pointerEvents = 'auto';
                        container.style.zIndex = '99999';
                    });
                """)
                time.sleep(0.5)
                
                # Now try multiple click methods
                click_successful = False
                
                try:
                    # Method 1: Try normal click first (prefer actual links)
                    elem = best_option['element']
                    
                    # If element is not a link, try to find the actual link
                    if elem.tag_name.lower() != 'a':
                        # Look for link child
                        links = elem.find_elements(By.TAG_NAME, 'a')
                        if links:
                            elem = links[0]
                            logger.info("Found link child to click instead of text element")
                    
                    elem.click()
                    logger.info("✅ Selected dropdown option with normal click")
                    click_successful = True
                except Exception as e:
                    logger.warning(f"Normal click failed: {e}")
                    
                    try:
                        # Method 2: JavaScript click with href extraction
                        logger.info("🔧 Trying enhanced JavaScript click...")
                        result = self.driver.execute_script("""
                            var element = arguments[0];
                            
                            // If element has href, navigate directly
                            if (element.href) {
                                window.location.href = element.href;
                                return 'navigated';
                            }
                            
                            // Try to find parent with href
                            var parent = element.closest('a[href]');
                            if (parent && parent.href) {
                                window.location.href = parent.href;
                                return 'navigated-parent';
                            }
                            
                            // Otherwise, simulate click event
                            var event = new MouseEvent('click', {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            element.dispatchEvent(event);
                            
                            // Also try native click
                            element.click();
                            return 'clicked';
                        """, best_option['element'])
                        
                        logger.info(f"✅ JavaScript click result: {result}")
                        click_successful = True
                    except Exception as e2:
                        logger.warning(f"JavaScript click failed: {e2}")
                        
                        try:
                            # Method 3: Extract text and use keyboard navigation
                            logger.info("🔧 Trying keyboard navigation method...")
                            option_text = best_option['text']
                            
                            # Type the exact text in search field to narrow down
                            search_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
                            search_field.clear()
                            search_field.send_keys(option_text)
                            time.sleep(1)
                            
                            # Press Enter to select
                            search_field.send_keys(Keys.ENTER)
                            logger.info("✅ Selected via keyboard navigation")
                            click_successful = True
                        except Exception as e3:
                            logger.error(f"Keyboard navigation failed: {e3}")
                
                if not click_successful:
                    logger.error("All click methods failed!")
                    logger.info("⚠️ Falling back to Enter key with original search...")
                    # Restore original search and press Enter
                    search_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
                    search_field.clear()
                    search_field.send_keys(search_term)  # Use search_term from beginning of method
                    time.sleep(0.5)
                    search_field.send_keys(Keys.ENTER)
                
                time.sleep(3)
            else:
                # Fallback: Press Enter for basic search
                logger.warning("⚠️ No good dropdown options found, using Enter fallback")
                search_field.send_keys(Keys.ENTER)
                time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Error in dropdown search: {e}")
            raise
    
    def _find_best_dropdown_option(self, target_components: List[str]) -> Optional[Dict[str, Any]]:
        """
        STEP 3: Find and score dropdown options by component matching.
        Returns best matching option or None.
        """
        logger.info("🔍 Scanning dropdown options...")
        
        try:
            # FIRST: Remove the blocking mask
            self.driver.execute_script("""
                var mask = document.querySelector('.autoCompleteMask');
                if (mask) {
                    mask.remove();
                    console.log('Removed autoCompleteMask');
                }
            """)
            
            # Look for dropdown/autocomplete elements - ZAP specific + generic
            dropdown_selectors = [
                # Look for actual links first (these navigate to product pages)
                "a[href*='model.aspx']",      # Direct product links
                "div.autoCompleteResults a",  # Primary ZAP dropdown links
                "a.autoCompleteResult",        # Individual result links
                ".autoCompleteResults a",      # Any links in autocomplete
                
                # Then check other elements
                ".autoCompleteResults .autoCompleteResult",
                "div.autoCompleteResults div",
                ".autocomplete-suggestions .autocomplete-suggestion",
                ".autocomplete-suggestions div",
                ".ui-autocomplete .ui-menu-item",
                ".ui-menu-item",
                ".autocomplete-suggestion",
                ".suggestion",
                "[class*='suggestion']",
                "[class*='autocomplete'] div",
                "[class*='search-result']",
                # Generic selectors  
                ".autocomplete-item",
                ".dropdown-item", 
                ".suggestion-item",
                ".search-result",
                "[role='option']",
                "li[data-value]",
                "div[class*='suggest']",
                "div[class*='auto']",
                ".search-suggestion"
            ]
            
            all_options = []
            
            # Try each selector
            for selector in dropdown_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"✅ Found {len(elements)} elements with selector: {selector}")
                        valid_options = 0
                        for element in elements:
                            option_text = element.text.strip()
                            logger.debug(f"   Element text: '{option_text}' (visible: {element.is_displayed()})")
                            if option_text and len(option_text) > 3 and element.is_displayed():  # Valid option
                                all_options.append({
                                    'element': element,
                                    'text': option_text,
                                    'selector': selector
                                })
                                valid_options += 1
                        logger.info(f"   -> {valid_options} valid options found")
                        if valid_options > 0:
                            break  # Use first working selector with valid options
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not all_options:
                logger.warning("No dropdown options found with standard selectors")
                
                # FALLBACK: Look for ANY clickable elements with relevant text
                logger.info("🔍 Trying fallback: scanning for any clickable elements with product text...")
                try:
                    # Find all clickable elements
                    clickable_selectors = ["a", "div[onclick]", "[role='button']", "button", "li", "span[onclick]"]
                    
                    for selector in clickable_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        logger.debug(f"Checking {len(elements)} {selector} elements...")
                        
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    element_text = element.text.strip()
                                    # Check if element contains any of our target components
                                    if (element_text and len(element_text) > 5 and 
                                        any(component.lower() in element_text.lower() for component in target_components)):
                                        logger.info(f"📋 Found potential option: '{element_text[:100]}...'")
                                        all_options.append({
                                            'element': element,
                                            'text': element_text,
                                            'selector': f"fallback-{selector}"
                                        })
                            except:
                                continue
                        
                        if all_options:
                            logger.info(f"✅ Found {len(all_options)} options via fallback method")
                            break
                except Exception as e:
                    logger.debug(f"Fallback search failed: {e}")
                
                if not all_options:
                    logger.warning("No dropdown options found even with fallback")
                    return None
            
            logger.info(f"Found {len(all_options)} total dropdown options")
            
            # Score each option
            scored_options = []
            for option in all_options:
                score = self._score_dropdown_option(option['text'], target_components)
                scored_options.append({
                    **option,
                    'score': score
                })
                logger.debug(f"Option: '{option['text'][:50]}...' → Score: {score}")
            
            # Sort by score (highest first)
            scored_options.sort(key=lambda x: x['score'], reverse=True)
            
            # Return best option ONLY if it has ALL mandatory components
            best_option = scored_options[0]
            total_components = len(target_components)
            
            # MANDATORY: Must have ALL components (score > 0 means all found due to new scoring)
            if best_option['score'] > 0:
                logger.info(f"🎯 PERFECT MATCH - All {total_components} mandatory components found!")
                logger.info(f"Selected: {best_option['text'][:100]}")
                return best_option
            else:
                logger.error(f"❌ NO VALID OPTIONS - All options missing mandatory components!")
                logger.info("Cannot proceed without all mandatory components (Manufacturer + Product + Type + Model Number)")
                return None
                
        except Exception as e:
            logger.error(f"Error finding dropdown options: {e}")
            return None
    
    def _score_dropdown_option(self, option_text: str, target_components: List[str]) -> int:
        """
        MANDATORY AND logic - ALL components MUST be present.
        
        Components and their MANDATORY status:
        - Manufacturer (e.g., "Electra") → MANDATORY
        - Product Name (e.g., "Titanium") → MANDATORY  
        - Type (e.g., "INV" = "Inverter") → MANDATORY
        - Model Number (e.g., "140") → MANDATORY
        
        ALL components must match or score = 0 (REJECT)
        """
        option_lower = option_text.lower()
        components_found = 0
        components_detail = []
        missing_mandatory = False
        
        # Check each MANDATORY component
        for i, component in enumerate(target_components):
            component_lower = component.lower().strip()
            found = False
            
            # Special handling for INV/Inverter equivalence
            if component_lower == "inv":
                # Accept either "inv" or "inverter" 
                if "inv" in option_lower or "inverter" in option_lower:
                    found = True
                    components_detail.append(f"✓{component}(or Inverter)")
            elif component_lower == "inverter":
                # Accept either "inverter" or "inv"
                if "inverter" in option_lower or "inv" in option_lower:
                    found = True
                    components_detail.append(f"✓{component}(or INV)")
            else:
                # Standard exact match required
                if component_lower and component_lower in option_lower:
                    found = True
                    components_detail.append(f"✓{component}")
            
            if found:
                components_found += 1
            else:
                components_detail.append(f"✗{component} [MANDATORY!]")
                missing_mandatory = True
        
        # Log the match details
        if missing_mandatory:
            logger.warning(f"  ❌ REJECTED: '{option_text[:50]}...' - Missing mandatory components")
            logger.debug(f"    Components: {' '.join(components_detail)}")
            return 0  # ANY missing mandatory = instant rejection
        else:
            logger.info(f"  ✅ ACCEPTED: '{option_text[:50]}...' - All {components_found} mandatory components found")
            logger.debug(f"    Components: {' '.join(components_detail)}")
            return components_found
    
    def _wait_for_filtered_results(self) -> None:
        """Wait for the page to be filtered with search results."""
        logger.info("Waiting for filtered results...")
        
        try:
            # Wait for URL to change or results to load
            time.sleep(3)
            
            # Check for results container
            results_selectors = [
                ".ItemsFound",
                ".ModelRow",
                ".search-results",
                ".products-list",
                "#results"
            ]
            
            for selector in results_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Results loaded with selector: {selector}")
                    break
                except:
                    continue
            
        except Exception as e:
            logger.warning(f"Warning waiting for results: {e}")
    
    def _scroll_to_load_all_listings(self) -> None:
        """Scroll to page footer to ensure all listings are loaded."""
        logger.info("Scrolling to load all listings...")
        
        try:
            # Scroll to bottom progressively
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Scroll back up slightly to ensure all elements are accessible
            self.driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(1)
            
            logger.info("Finished scrolling - all listings should be loaded")
            
        except Exception as e:
            logger.warning(f"Warning during scrolling: {e}")
    
    def _find_validated_listings(self) -> List[Dict[str, Any]]:
        """
        Find and validate listings using 2-artifact rule:
        1. Button (קנו עכשיו / לפרטים נוספים / השוואת מחירים)
        2. Price with ₪ symbol
        """
        logger.info("Finding validated listings with 2-artifact rule...")
        validated_listings = []
        
        try:
            # Log current URL for debugging
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Find all potential listing containers
            listing_selectors = [
                # Primary selectors for ZAP model pages
                ".PriceRow",  # Price rows on model pages
                ".StoresLines",  # Store/vendor lines
                ".LineBar",  # Individual vendor lines
                "tr.PriceRow",  # Table row format
                # Alternative selectors
                ".ModelRow",
                ".ItemsFound .ModelRow",
                ".product-item",
                ".vendor-item",
                "div[class*='offer']",
                # Additional selectors
                ".product-card",
                ".offer-card",
                ".vendor-offer",
                "div[class*='product']",
                "div[class*='vendor']"
            ]
            
            listing_elements = []
            for selector in listing_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        listing_elements = elements
                        logger.info(f"Found {len(elements)} potential listings with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not listing_elements:
                logger.warning("No listing elements found with any selector!")
                # Try to get page source for debugging
                page_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
                logger.debug(f"Page text sample: {page_text}")
            
            # Validate each listing
            for element in listing_elements:
                try:
                    # Check for button artifact
                    button = None
                    button_type = None
                    
                    button_patterns = [
                        ("השוואת מחירים", "T.3"),  # Check T.3 FIRST - highest priority
                        ("קנו עכשיו", "T.1"),
                        ("לפרטים נוספים", "T.2"),
                        # Also look for "לחנות" which is common on ZAP
                        ("לחנות", "T.2"),
                        ("מעבר לחנות", "T.2"),
                        ("כניסה לחנות", "T.2")
                    ]
                    
                    for pattern, b_type in button_patterns:
                        try:
                            # Try to find button/link with text
                            button_xpath = f".//a[contains(text(), '{pattern}')] | .//button[contains(text(), '{pattern}')] | .//span[contains(text(), '{pattern}')]/parent::a"
                            button = element.find_element(By.XPATH, button_xpath)
                            button_type = b_type
                            break
                        except:
                            continue
                    
                    # If no button found with text, look for any clickable link in the element
                    if not button:
                        try:
                            # Look for any link that might be a vendor link
                            links = element.find_elements(By.TAG_NAME, "a")
                            for link in links:
                                href = link.get_attribute("href") or ""
                                # Check if it's a vendor redirect link
                                if "redirect" in href.lower() or "site=" in href or "url=" in href:
                                    button = link
                                    button_type = "T.2"  # Assume external vendor
                                    break
                        except:
                            pass
                    
                    if not button:
                        continue
                    
                    # Check for price artifact (₪ symbol)
                    price_text = element.text
                    if "₪" not in price_text:
                        continue
                    
                    # Extract price value
                    price_match = re.search(r'([\d,]+(?:\.\d+)?)\s*₪', price_text)
                    if not price_match:
                        continue
                    
                    price = float(price_match.group(1).replace(',', ''))
                    
                    # Extract product name from listing
                    product_name = self._extract_product_name_from_listing(element)
                    
                    # Valid listing found
                    listing = {
                        'element': element,
                        'button': button,
                        'button_type': button_type,
                        'price': price,
                        'product_name': product_name
                    }
                    
                    validated_listings.append(listing)
                    logger.debug(f"✅ Validated listing: {button_type} - ₪{price:,.0f}")
                    
                except Exception as e:
                    logger.debug(f"Error validating listing: {e}")
                    continue
            
            logger.info(f"✅ Found {len(validated_listings)} validated listings")
            return validated_listings
            
        except Exception as e:
            logger.error(f"Error finding validated listings: {e}")
            return []
    
    def _extract_product_name_from_listing(self, element) -> str:
        """Extract product name from a listing element with enhanced extraction."""
        try:
            # Try multiple selectors for product name with priority order
            name_selectors = [
                ("img[alt]", "alt"),  # Image alt text often has clean product names
                ("a[href*='model'] img", "alt"),  # Model links with images
                ("h3", "text"), ("h4", "text"), ("h5", "text"),
                (".product-name", "text"), (".title", "text"), (".ModelName", "text"),
                ("a[href*='model']", "text"),  # Model links
                (".product-title", "text"), ("span[title]", "title")
            ]
            
            for selector, attr_type in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if attr_type == "alt":
                        name = name_elem.get_attribute('alt')
                    elif attr_type == "title":
                        name = name_elem.get_attribute('title')
                    else:
                        name = name_elem.text.strip()
                    
                    if name and len(name) > 5:
                        # Clean up the product name and check if valid
                        cleaned_name = self._clean_product_name(name)
                        if cleaned_name != "Unknown Product":
                            logger.debug(f"Extracted product name: '{cleaned_name}' from selector: {selector}")
                            return cleaned_name
                except:
                    continue
            
            # Enhanced fallback: look for meaningful text in element
            element_text = element.text.strip()
            text_lines = element_text.split('\n')
            
            for line in text_lines:
                line = line.strip()
                # Skip price lines, short lines, and button text
                if (line and '₪' not in line and len(line) > 8 and 
                    not any(btn in line for btn in ['לפרטים נוספים', 'קנו עכשיו', 'השוואת מחירים']) and
                    any(keyword in line.lower() for keyword in ['מזגן', 'inv', 'inverter', 'electra', 'tornado', 'tadiran'])):
                    
                    cleaned_name = self._clean_product_name(line)
                    if cleaned_name != "Unknown Product":
                        logger.debug(f"Extracted product name from fallback: '{cleaned_name}'")
                        return cleaned_name
            
            # Final fallback: use the input product name if extraction fails
            logger.warning(f"Could not extract product name from listing, using fallback")
            return "Product Name Not Available"
            
        except Exception as e:
            logger.debug(f"Error extracting product name: {e}")
            return "Product Name Not Available"
    
    def _clean_product_name(self, name: str) -> str:
        """Clean and standardize product name, filter out button text patterns."""
        try:
            # Remove extra whitespace and normalize
            name = ' '.join(name.split())
            
            # FILTER OUT button text patterns (user reported issue)
            button_patterns = [
                'לפרטים נוספים', 'קנו עכשיו', 'השוואת מחירים',
                'מזגנים - לפרטים נוספים', 'מזגנים - קנו עכשיו',
                'מזגנים - השוואת מחירים'
            ]
            
            # Check if this is ONLY a button text pattern
            for pattern in button_patterns:
                if name == pattern or name.endswith(pattern):
                    logger.debug(f"Filtered out button text pattern: '{name}'")
                    return "Unknown Product"  # Skip this entry
            
            # Remove button text from the end of product names if present
            for pattern in button_patterns:
                if pattern in name:
                    name = name.replace(pattern, '').strip()
                    name = name.rstrip(' -').strip()  # Remove trailing dashes
            
            # Additional cleanup
            name = name.replace('מזגנים -', '').strip()  # Remove generic prefix
            
            # Validate that we have a meaningful product name
            if len(name) < 5 or name.lower() in ['unknown', 'n/a', '']:
                return "Unknown Product"
            
            return name
        except:
            return name
    
    def _process_listing_by_button_type(self, listing: Dict[str, Any], product: ProductInput) -> List[VendorOffer]:
        """Process a listing based on its button type (T.1, T.2, or T.3)."""
        button_type = listing['button_type']
        logger.info(f"Processing {button_type} listing...")
        
        try:
            if button_type == "T.1":
                return self._process_t1_button(listing, product)
            elif button_type == "T.2":
                return self._process_t2_button(listing, product)
            elif button_type == "T.3":
                return self._process_t3_button(listing, product)
            else:
                logger.warning(f"Unknown button type: {button_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error processing {button_type} listing: {e}")
            return []
    
    def _process_t1_button(self, listing: Dict[str, Any], product: ProductInput) -> List[VendorOffer]:
        """
        Process T.1 button: "קנו עכשיו" - Always zap.co.il vendor.
        Extract: price, product name from listing; URL and vendor name (zap.co.il) from drilled page.
        """
        logger.info("Processing T.1 button (קנו עכשיו - zap.co.il)")
        
        try:
            # Get data from listing
            price = listing['price']
            product_name = listing['product_name']
            button = listing['button']
            button_text = button.text.strip() if button else "קנו עכשיו"  # Get actual button text
            
            # Click button to get URL
            original_url = self.driver.current_url
            
            try:
                # Open in new tab to preserve main listing
                button.send_keys(Keys.CONTROL + Keys.RETURN)
                time.sleep(2)
                
                # Switch to new tab
                self.driver.switch_to.window(self.driver.window_handles[-1])
                vendor_url = self.driver.current_url
                
                # Close tab and switch back
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
            except:
                # Fallback: get href attribute
                vendor_url = button.get_attribute('href') or original_url
            
            # Create vendor offer
            offer = VendorOffer(
                vendor_name="zap.co.il",
                product_name=product_name,
                price=price,
                url=vendor_url,
                button_text=button_text  # Actual button text that was pressed
            )
            
            logger.info(f"✅ T.1 offer: zap.co.il - ₪{price:,.0f}")
            return [offer]
            
        except Exception as e:
            logger.error(f"Error processing T.1 button: {e}")
            return []
    
    def _process_t2_button(self, listing: Dict[str, Any], product: ProductInput) -> List[VendorOffer]:
        """
        Process T.2 button: "לפרטים נוספים" - External vendor.
        Extract: price, product name from listing; URL and vendor name from drilled page header.
        """
        logger.info("Processing T.2 button (לפרטים נוספים - external vendor)")
        
        try:
            # Get data from listing
            price = listing['price']
            product_name = listing['product_name']
            button = listing['button']
            button_text = button.text.strip() if button else "לפרטים נוספים"  # Get actual button text
            
            # Click button to get vendor page
            original_url = self.driver.current_url
            vendor_name = "Unknown Vendor"
            vendor_url = ""
            
            try:
                # Open in new tab
                button.send_keys(Keys.CONTROL + Keys.RETURN)
                time.sleep(3)
                
                # Switch to new tab
                self.driver.switch_to.window(self.driver.window_handles[-1])
                vendor_url = self.driver.current_url
                
                # Extract vendor name from header/logo
                vendor_name = self._extract_vendor_from_header()
                
                # Close tab and switch back
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
            except:
                # Fallback: try to extract from URL or button context
                vendor_url = button.get_attribute('href') or original_url
                vendor_name = self._extract_vendor_name_from_context(button) or "Unknown Vendor"
                
                # Special case: if it's a ZAP comparison page, give it a proper name
                if "zap.co.il" in vendor_url and "comp" in vendor_url.lower():
                    vendor_name = "ZAP השוואת מחירים"
            
            # Create vendor offer
            offer = VendorOffer(
                vendor_name=vendor_name,
                product_name=product_name,
                price=price,
                url=vendor_url,
                button_text=button_text  # Actual button text that was pressed
            )
            
            logger.info(f"✅ T.2 offer: {vendor_name} - ₪{price:,.0f}")
            return [offer]
            
        except Exception as e:
            logger.error(f"Error processing T.2 button: {e}")
            return []
    
    def _extract_vendor_from_header(self) -> str:
        """Extract vendor name from page header (logo, title, etc.)."""
        try:
            current_url = self.driver.current_url
            logger.debug(f"Extracting vendor from URL: {current_url}")
            
            # Strategy 1: Check if it's a ZAP comparison/model page
            try:
                if "zap.co.il" in current_url.lower():
                    if "compmodels.aspx" in current_url or "models.aspx" in current_url:
                        return "ZAP השוואת מחירים"
                    elif "shop.zap.co.il" in current_url:
                        return "zap.co.il"
            except Exception as e:
                logger.debug(f"ZAP URL check failed: {e}")
            
            # Strategy 2: Extract from URL domain (for non-ZAP sites)
            try:
                domain = urlparse(current_url).netloc
                if domain and "zap" not in domain.lower():
                    # Clean domain name to get vendor name
                    vendor = domain.replace('www.', '').replace('shop.', '').split('.')[0]
                    vendor = vendor.replace('-', ' ').replace('_', ' ').title()
                    logger.debug(f"Extracted from domain: {vendor}")
                    if len(vendor) > 1 and vendor.lower() != "unknown":
                        return vendor
            except Exception as e:
                logger.debug(f"Domain extraction failed: {e}")
            
            # Strategy 3: Look for vendor name in page title (clean it)
            try:
                title = self.driver.title.strip()
                if title and "zap" not in title.lower():
                    # Remove common suffixes and prefixes
                    title = title.split('-')[0].split('|')[0].split('–')[0]
                    title = title.replace('מזגן', '').replace('עילי', '').strip()
                    # If it's not a product description, use it
                    if (len(title) < 30 and 
                        not any(word in title.lower() for word in ['inv', 'wifi', 'btuh', 'כ"ס', 'טון']) and
                        len(title) > 2):
                        logger.debug(f"Extracted from title: {title}")
                        return title
            except Exception as e:
                logger.debug(f"Title extraction failed: {e}")
            
            # Strategy 4: Look for logo with alt text
            logo_selectors = [
                "header img[alt]",
                ".logo img[alt]", 
                "#logo img[alt]",
                "img.logo[alt]",
                "[class*='logo'] img[alt]"
            ]
            
            for selector in logo_selectors:
                try:
                    logo = self.driver.find_element(By.CSS_SELECTOR, selector)
                    alt_text = logo.get_attribute('alt').strip()
                    # Filter out generic alt text
                    if (alt_text and len(alt_text) > 1 and len(alt_text) < 30 and
                        not any(word in alt_text.lower() for word in ['logo', 'image', 'pic', 'מזגן', 'inv'])):
                        logger.debug(f"Extracted from logo alt: {alt_text}")
                        return alt_text
                except:
                    continue
            
            # Strategy 5: Look in header/navigation for vendor name
            header_selectors = ["header", ".header", "#header", "nav", ".nav", ".navbar"]
            for selector in header_selectors:
                try:
                    header = self.driver.find_element(By.CSS_SELECTOR, selector)
                    header_text = header.text.strip()
                    if header_text:
                        lines = header_text.split('\n')
                        for line in lines[:5]:  # Check first 5 lines
                            line = line.strip()
                            # Look for short, non-product-like text
                            if (line and 3 < len(line) < 25 and 
                                not any(word in line.lower() for word in ['מזגן', 'inv', 'wifi', 'btuh', 'כ"ס', 'home', 'עמוד', 'חיפוש'])):
                                logger.debug(f"Extracted from header text: {line}")
                                return line
                except:
                    continue
            
            # Strategy 6: Fallback - use domain but cleaned up
            try:
                domain = urlparse(current_url).netloc
                if domain and "zap" not in domain.lower():
                    vendor = domain.replace('www.', '').split('.')[0]
                    vendor = vendor.replace('-', '').replace('_', '').capitalize()
                    logger.debug(f"Fallback domain vendor: {vendor}")
                    return vendor
            except:
                pass
            
            logger.warning("Could not extract vendor name, using Unknown Vendor")
            return "Unknown Vendor"
            
        except Exception as e:
            logger.error(f"Error extracting vendor from header: {e}")
            return "Unknown Vendor"
    
    def _process_t3_button(self, listing: Dict[str, Any], product: ProductInput) -> List[VendorOffer]:
        """
        Process T.3 button: "השוואת מחירים" - Recursive listing page.
        Opens another listing page with T.1 and T.2 buttons only.
        CRITICAL: T.3 button itself is NEVER added to results - only the vendors from the comparison page.
        """
        button = listing['button']
        button_text = button.text.strip() if button else "השוואת מחירים"
        
        logger.info(f"🔄 Processing T.3 button: '{button_text}' - Starting recursive navigation")
        
        try:
            # Click button to open sub-listing page
            original_url = self.driver.current_url
            logger.info(f"Original URL: {original_url}")
            
            try:
                # Open in new tab
                button.send_keys(Keys.CONTROL + Keys.RETURN)
                time.sleep(3)
                
                # Switch to new tab
                self.driver.switch_to.window(self.driver.window_handles[-1])
                comparison_url = self.driver.current_url
                logger.info(f"Comparison page URL: {comparison_url}")
                
                # Verify we're on a comparison page
                if "compmodels.aspx" not in comparison_url and "models.aspx" not in comparison_url:
                    logger.warning(f"T.3 navigation may have failed - unexpected URL: {comparison_url}")
                
                # Process the sub-listing page (will have T.1 and T.2 only)
                self._scroll_to_load_all_listings()
                
                # Find validated listings (T.1 and T.2 only)
                sub_listings = self._find_validated_listings()
                logger.info(f"Found {len(sub_listings)} sub-listings on comparison page")
                
                # Process each sub-listing - NEVER include T.3 types
                vendor_offers = []
                for sub_listing in sub_listings:
                    if sub_listing['button_type'] != "T.3":  # Skip any T.3 in sub-pages
                        logger.info(f"Processing sub-listing: {sub_listing['button_type']}")
                        offers = self._process_listing_by_button_type(sub_listing, product)
                        vendor_offers.extend(offers)
                    else:
                        logger.warning(f"Skipping T.3 button on comparison page (would create infinite recursion)")
                
                # Close tab and switch back
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                logger.info(f"✅ T.3 recursive processing complete: {len(vendor_offers)} vendors found")
                logger.info(f"🚨 IMPORTANT: T.3 button itself is NOT added to results - only found vendors")
                return vendor_offers
                
            except Exception as e:
                logger.error(f"Error in T.3 recursive processing: {e}")
                # Try to return to original tab
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                return []
                
        except Exception as e:
            logger.error(f"Error processing T.3 button: {e}")
            return [] 