"""
Natural Language CLI Interface for Universal Product Scraper
Provides user-friendly, conversational interaction with 1,2,3 or A,B,C choices
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.api.scraper_service import ScraperService
from src.api.validation_service import ValidationService
from src.api.results_service import ResultsService
from src.api.status_service import StatusService
from src.api.summary_service import SummaryService

logger = get_logger(__name__)

# Detect if running from PyInstaller executable
RUNNING_FROM_EXECUTABLE = getattr(sys, 'frozen', False)


class NaturalLanguageCLI:
    """Natural language interface for the Universal Product Scraper."""
    
    def __init__(self):
        """Initialize the Natural Language CLI."""
        self.current_config = {
            'source_file': None,
            'target_file': None,
            'row_range': None,
            'mode': None,
            'products_to_process': 0
        }
        self.auth_manager = None
        
        # Initialize API services
        self.scraper_service = ScraperService()
        self.validation_service = ValidationService()
        self.results_service = ResultsService()
        self.status_service = StatusService()
        self.summary_service = SummaryService()
        
    def start_interactive_session(self, auth_manager=None):
        """Start the main interactive session."""
        self.auth_manager = auth_manager
        self.print_welcome()
        
        while True:
            try:
                # Main menu
                choice = self.show_main_menu()
                
                if choice == '1':
                    self.configure_scraping_session()
                elif choice == '2':
                    self.quick_scraping_wizard()
                elif choice == '3':
                    self.view_recent_results()
                elif choice == '4':
                    self.system_status_check()
                elif choice == '5':
                    self.show_help_and_examples()
                elif choice == '6':
                    # Logout
                    if self.auth_manager:
                        self.auth_manager.logout()
                        print("🔐 You have been logged out.")
                        break
                    else:
                        print("❌ No active session to logout from")
                elif choice == '7':
                    print("\n👋 Thank you for using Universal Product Scraper!")
                    if self.auth_manager:
                        self.auth_manager.logout()
                    break
                else:
                    print("❌ Please enter a number between 1-7")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"\n❌ An error occurred: {e}")
                input("\nPress Enter to continue...")
    
    def print_welcome(self):
        """Print welcome message and system overview."""
        print("\n" + "="*70)
        print("🚀 UNIVERSAL PRODUCT SCRAPER - Natural Language Interface")
        print("="*70)
        print("Welcome! I'll help you scrape product prices from ZAP.co.il")
        print("using simple, conversational prompts.")
        print(f"\n📅 Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show authentication info if available
        if self.auth_manager:
            current_user = self.auth_manager.get_current_user()
            session_info = self.auth_manager.session_manager.get_session_info()
            if current_user and session_info:
                print(f"👤 Logged in as: {current_user}")
                print(f"🕐 Session expires in: {session_info['time_left_hours']} hours")
        
        print("-"*70)
    
    def show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        print("\n🔧 What would you like to do today?")
        print("\n1. 📊 Configure a custom scraping session")
        print("2. ⚡ Quick scraping wizard (guided setup)")
        print("3. 📈 View recent scraping results")
        print("4. 🔍 Check system status and performance")
        print("5. ❓ Help and examples")
        print("6. 🔐 Logout")
        print("7. 🚪 Exit")
        
        choice = input("\n👉 Please enter your choice (1-7): ").strip()
        return choice
    
    def configure_scraping_session(self):
        """Configure a custom scraping session step by step."""
        print("\n" + "="*50)
        print("📊 CUSTOM SCRAPING SESSION CONFIGURATION")
        print("="*50)
        
        # Step 1: Choose source file
        source_file = self.choose_source_file()
        if not source_file:
            return
            
        # Step 2: Analyze source file
        products_info = self.analyze_source_file(source_file)
        if not products_info:
            return
            
        # Step 3: Choose what to scrape
        row_selection = self.choose_products_to_scrape(products_info)
        if not row_selection:
            return
            
        # Step 4: Choose scraping mode
        mode = self.choose_scraping_mode(row_selection['product_count'])
        if not mode:
            return
            
        # Step 5: Choose output location
        target_file = self.choose_output_location()
        if not target_file:
            return
            
        # Step 6: Review and confirm
        if self.review_and_confirm_config(source_file, target_file, row_selection, mode):
            self.execute_scraping_session(source_file, target_file, row_selection, mode)
    
    def quick_scraping_wizard(self):
        """Quick wizard for common scraping tasks."""
        print("\n" + "="*50)
        print("⚡ QUICK SCRAPING WIZARD")
        print("="*50)
        
        print("I'll help you set up scraping quickly with smart defaults!")
        print("\nWhat type of scraping do you want to do?")
        print("\nA. 🧪 Quick test (2 products, ~10 minutes, visible browser)")
        print("B. 📊 Small batch (6-10 products, your choice of mode)")  
        print("C. 🚀 Large batch (11+ products, headless mode)")
        print("D. 🔍 Single product validation")
        
        choice = input("\n👉 Choose your scraping type (A/B/C/D): ").strip().upper()
        
        if choice == 'A':
            self.quick_test_scraping()
        elif choice == 'B':
            self.quick_small_batch()
        elif choice == 'C':
            self.quick_large_batch()
        elif choice == 'D':
            self.quick_single_product()
        else:
            print("❌ Please choose A, B, C, or D")
    
    def choose_source_file(self) -> Optional[str]:
        """Let user choose source Excel file."""
        print("\n📁 Let's find your product list (Excel file)")
        
        # Check for default SOURCE.xlsx
        default_source = "data/SOURCE.xlsx"
        if os.path.exists(default_source):
            print(f"\n✅ Found default source file: {default_source}")
            choice = input("👉 Use this file? (Y/n): ").strip().lower()
            if choice in ['', 'y', 'yes']:
                return default_source
        
        # Manual file selection
        print("\n📂 Available options:")
        print("1. Enter custom file path")
        print("2. Browse data/ directory")
        print("3. Cancel")
        print("\n💡 TIP: You can paste a full file path directly (no need to choose option 1 first)")
        print("   Example: C:\\Users\\USER\\Google Drive\\SW_PLATFORM\\...\\SOURCE.xlsx")
        
        choice = input("\n👉 Enter choice (1-3) OR paste full file path: ").strip()
        
        # Smart input detection: Check if input looks like a file path
        if self._is_file_path(choice):
            # User entered a file path directly
            print(f"📁 Detected file path: {choice}")
            
            # Handle different path formats for external computers
            normalized_path = self._normalize_file_path(choice)
            
            if os.path.exists(normalized_path):
                print(f"✅ File found and verified!")
                return normalized_path
            elif os.path.exists(choice):
                print(f"✅ File found and verified!")
                return choice
            else:
                print(f"❌ File not found: {choice}")
                # Suggest potential fixes for common path issues
                suggestions = self._suggest_path_fixes(choice)
                if suggestions:
                    print("💡 Possible fixes:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
                return None
        
        # Traditional menu option handling
        elif choice == '1':
            file_path = input("📁 Enter full path to your Excel file: ").strip()
            normalized_path = self._normalize_file_path(file_path)
            
            if os.path.exists(normalized_path):
                return normalized_path
            elif os.path.exists(file_path):
                return file_path
            else:
                print(f"❌ File not found: {file_path}")
                suggestions = self._suggest_path_fixes(file_path)
                if suggestions:
                    print("💡 Possible fixes:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
                return None
                
        elif choice == '2':
            return self.browse_data_directory()
            
        elif choice == '3':
            return None
            
        else:
            # Check if it might be a path that we failed to detect
            if len(choice) > 10 and ('\\' in choice or '/' in choice):
                print(f"🤔 Input looks like it might be a file path: '{choice[:50]}...'")
                try_anyway = input("👉 Try to use it as a file path anyway? (y/N): ").strip().lower()
                if try_anyway in ['y', 'yes']:
                    # Process as if it were detected as a file path
                    normalized_path = self._normalize_file_path(choice)
                    
                    if os.path.exists(normalized_path):
                        print(f"✅ File found and verified!")
                        return normalized_path
                    elif os.path.exists(choice):
                        print(f"✅ File found and verified!")
                        return choice
                    else:
                        print(f"❌ File not found: {choice}")
                        suggestions = self._suggest_path_fixes(choice)
                        if suggestions:
                            print("💡 Possible fixes:")
                            for suggestion in suggestions:
                                print(f"   • {suggestion}")
                        return None
            
            print(f"❌ Invalid input: '{choice}'")
            print("💡 Please enter either:")
            print("   • A number (1, 2, or 3)")
            print("   • A full file path (like: C:\\Users\\USER\\Google Drive\\...\\file.xlsx)")
            print("   • Try option 1 to enter the path step-by-step")
            return None
    
    def browse_data_directory(self) -> Optional[str]:
        """Browse data directory for Excel files."""
        data_dir = "data"
        if not os.path.exists(data_dir):
            print(f"❌ Data directory not found: {data_dir}")
            return None
            
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            print(f"❌ No Excel files found in {data_dir}/")
            return None
            
        print(f"\n📂 Excel files in {data_dir}/:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
            
        try:
            choice = int(input(f"\n👉 Choose file (1-{len(excel_files)}): ").strip())
            if 1 <= choice <= len(excel_files):
                return os.path.join(data_dir, excel_files[choice-1])
            else:
                print("❌ Invalid choice")
                return None
        except ValueError:
            print("❌ Please enter a number")
            return None
    
    def analyze_source_file(self, source_file: str) -> Optional[Dict[str, Any]]:
        """Analyze source file and show product information."""
        print(f"\n🔍 Analyzing source file: {source_file}")
        
        try:
            products = self.scraper_service.get_source_products(source_file)
            
            if not products:
                print("❌ No valid products found in the file")
                return None
                
            # Show summary
            total_products = len(products)
            print(f"\n✅ Found {total_products} valid products")
            
            # Show first few products as examples
            print("\n📋 First few products:")
            for i, product in enumerate(products[:5]):
                print(f"   Row {product.row_number}: {product.name} (₪{product.original_price})")
                
            if total_products > 5:
                print(f"   ... and {total_products - 5} more products")
                
            return {
                'total_products': total_products,
                'products': products,
                'first_row': products[0].row_number,
                'last_row': products[-1].row_number
            }
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def choose_products_to_scrape(self, products_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Let user choose which products to scrape."""
        total = products_info['total_products']
        first_row = products_info['first_row']
        last_row = products_info['last_row']
        
        print(f"\n🎯 Which products would you like to scrape?")
        print(f"   (Available: {total} products, rows {first_row}-{last_row})")
        
        print("\n📊 Common choices:")
        print("1. 🧪 Quick test with 2 products (~10 minutes)")
        print("2. 📋 Small batch: first 10 products")
        print("3. 🎯 Custom range (you specify start and end)")
        print("4. 🚀 All products (full processing)")
        
        choice = input("\n👉 Choose option (1-4): ").strip()
        
        if choice == '1':
            # Quick test with 2 products - let user choose which ones
            return self._handle_quick_test_selection(products_info)
            
        elif choice == '2':
            # First 10 products
            return {
                'type': 'first_n', 
                'count': 10,
                'product_count': min(10, total),
                'description': 'First 10 products'
            }
            
        elif choice == '3':
            # Custom range
            return self.get_custom_range(products_info)
            
        elif choice == '4':
            # All products
            print(f"\n⚠️  Processing all {total} products will take significant time!")
            print(f"   Estimated time: {self.estimate_processing_time(total)}")
            
            confirm = input("👉 Are you sure? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                return {
                    'type': 'all',
                    'product_count': total,
                    'description': f'All {total} products'
                }
            else:
                return None
                
        else:
            print("❌ Invalid choice")
            return None
    
    def _handle_quick_test_selection(self, products_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle quick test selection - 2 products with user choice."""
        available_rows = [p.row_number for p in products_info['products']]
        min_row = min(available_rows)
        max_row = max(available_rows)
        
        print(f"\n🧪 QUICK TEST SETUP")
        print(f"   Available rows: {min_row} to {max_row}")
        
        print(f"\n💡 Which product would you like to test?")
        print(f"A. 🎯 Optimal test product (WD 150 3PH - minimal vendors, ~5 min)")
        print(f"B. 🔍 I'll choose 2 specific rows for testing")
        
        choice = input(f"\n👉 Choose option (A/B): ").strip().upper()
        
        if choice == 'A':
            # Find "wd 150 3ph" for optimal quick testing (only 2 vendors)
            target_product = self._find_optimal_test_product(products_info)
            if target_product:
                return target_product
            else:
                # Fallback to first 2 products if optimal product not found
                return {
                    'type': 'first_n',
                    'count': 2,
                    'product_count': min(2, len(available_rows)),
                    'description': 'First 2 products (quick test - fallback)'
                }
            
        elif choice == 'B':
            # User chooses 2 specific rows
            return self._get_specific_test_rows(products_info)
            
        else:
            print("❌ Please choose A or B")
            return None
    
    def _find_optimal_test_product(self, products_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find optimal test product (WD 150 3PH) that has minimal vendors for quick testing."""
        products = products_info['products']
        
        # Search for "wd 150 3ph" (case-insensitive, flexible matching)
        target_keywords = ['wd', '150', '3ph']
        
        for product in products:
            product_name_lower = product.name.lower()
            # Check if all keywords are present in the product name
            if all(keyword in product_name_lower for keyword in target_keywords):
                print(f"\n✅ Found optimal test product: {product.name} (Row {product.row_number})")
                print(f"   This product has minimal vendors (~2) for fast testing")
                
                return {
                    'type': 'custom_range',
                    'start_row': product.row_number,
                    'end_row': product.row_number,
                    'product_count': 1,
                    'description': f'Row {product.row_number}: {product.name} (optimal for testing)'
                }
        
        # If not found, look for similar patterns
        for product in products:
            product_name_lower = product.name.lower()
            if 'wd' in product_name_lower and ('150' in product_name_lower or '3ph' in product_name_lower):
                print(f"\n⚡ Found similar test product: {product.name} (Row {product.row_number})")
                print(f"   Using this as alternative test product")
                
                return {
                    'type': 'custom_range',
                    'start_row': product.row_number,
                    'end_row': product.row_number,
                    'product_count': 1,
                    'description': f'Row {product.row_number}: {product.name} (alternative test product)'
                }
        
        print(f"\n⚠️  Could not find 'WD 150 3PH' product in the list")
        print(f"   Will use fallback method (first 2 products)")
        return None
    
    def _get_specific_test_rows(self, products_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Let user choose 2 specific rows for testing."""
        available_rows = [p.row_number for p in products_info['products']]
        min_row = min(available_rows)
        max_row = max(available_rows)
        
        print(f"\n🔍 CHOOSE 2 SPECIFIC ROWS")
        print(f"   Available rows: {min_row} to {max_row}")
        
        # Show first few products as examples
        print(f"\n📋 Examples from your product list:")
        for i, product in enumerate(products_info['products'][:8]):
            print(f"   Row {product.row_number}: {product.name} (₪{product.original_price})")
        
        if len(products_info['products']) > 8:
            remaining = len(products_info['products']) - 8
            print(f"   ... and {remaining} more products")
        
        try:
            print(f"\n👉 Enter 2 row numbers to test:")
            row1 = int(input(f"   First row ({min_row}-{max_row}): ").strip())
            row2 = int(input(f"   Second row ({min_row}-{max_row}): ").strip())
            
            # Validate rows
            if row1 not in available_rows or row2 not in available_rows:
                print("❌ One or both row numbers are not available")
                return None
                
            if row1 == row2:
                print("❌ Please choose 2 different rows")
                return None
            
            # Sort rows for consistent naming
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            
            return {
                'type': 'custom_range',
                'start_row': start_row,
                'end_row': end_row,
                'product_count': 2,
                'description': f'Rows {row1}, {row2} (user-selected test)'
            }
            
        except ValueError:
            print("❌ Please enter valid numbers")
            return None
    
    def get_custom_range(self, products_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get custom row range from user."""
        total = products_info['total_products']
        available_rows = [p.row_number for p in products_info['products']]
        min_row = min(available_rows)
        max_row = max(available_rows)
        
        print(f"\n🎯 Custom Range Selection")
        print(f"   Available rows: {min_row} to {max_row} ({total} products)")
        
        try:
            start = input(f"👉 Start row (minimum {min_row}): ").strip()
            end = input(f"👉 End row (maximum {max_row}): ").strip()
            
            start_row = int(start)
            end_row = int(end)
            
            if start_row < min_row or end_row > max_row or start_row > end_row:
                print("❌ Invalid range")
                return None
                
            # Count products in range
            products_in_range = [p for p in products_info['products'] 
                               if start_row <= p.row_number <= end_row]
            
            return {
                'type': 'custom_range',
                'start_row': start_row,
                'end_row': end_row,
                'product_count': len(products_in_range),
                'description': f'Rows {start_row}-{end_row} ({len(products_in_range)} products)'
            }
            
        except ValueError:
            print("❌ Please enter valid numbers")
            return None
    
    def estimate_processing_time(self, product_count: int) -> str:
        """Estimate processing time based on product count."""
        # Based on heavy testing: ~5 minutes per product average
        minutes = product_count * 5
        
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hours"
            else:
                return f"{hours}h {remaining_minutes}m"
    
    def choose_scraping_mode(self, product_count: int) -> Optional[str]:
        """Let user choose scraping mode with smart recommendations."""
        print(f"\n🖥️  SCRAPING MODE SELECTION")
        print(f"   You're processing {product_count} product(s)")
        
        # Apply bulk processing restrictions
        if product_count > 10:
            print(f"\n⚠️  BULK PROCESSING RESTRICTION:")
            print(f"   Processing {product_count} products (>10) requires headless mode.")
            print(f"   This ensures stability and optimal performance.")
            
            confirm = input("\n👉 Continue with headless mode? (Y/n): ").strip().lower()
            if confirm in ['', 'y', 'yes']:
                return 'headless'
            else:
                return None
        
        # For ≤10 products, offer choices
        print(f"\n🎛️  Available modes for {product_count} products:")
        print("1. 👀 Explicit mode - Shows browser window (good for debugging)")
        print("2. 🚀 Headless mode - No browser window (faster, uses less resources)")
        print("3. 📱 Minimal mode - Browser window minimized")
        
        # Add recommendations
        if product_count <= 3:
            print("\n💡 Recommendation: Explicit mode (best for testing/debugging)")
        elif product_count <= 6:
            print("\n💡 Recommendation: Headless mode (good balance of speed/resources)")
        else:
            print("\n💡 Recommendation: Headless mode (optimal for this batch size)")
        
        choice = input("\n👉 Choose mode (1-3): ").strip()
        
        mode_map = {
            '1': 'explicit',
            '2': 'headless', 
            '3': 'minimal'
        }
        
        return mode_map.get(choice)
    
    def choose_output_location(self) -> Optional[str]:
        """Let user choose output file location."""
        print(f"\n💾 Where should I save the results?")
        
        # Suggest default name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"scraping_results_{timestamp}.xlsx"
        # Use absolute path for clear display
        output_dir = Path.cwd() / "output"
        default_path = str(output_dir / default_name)
        
        # Ensure absolute path is displayed
        abs_display_path = str(Path(default_path).resolve())
        print(f"\n📁 Suggested location: {abs_display_path}")
        
        print("\n📂 Options:")
        print("1. ✅ Use suggested location")
        print("2. 🎯 Custom filename in output/ directory")
        print("3. 📁 Custom full path")
        
        choice = input("\n👉 Choose option (1-3): ").strip()
        
        if choice == '1':
            return default_path
            
        elif choice == '2':
            filename = input("📝 Enter filename (without .xlsx): ").strip()
            if filename:
                # Use absolute path for custom filename
                output_dir = Path.cwd() / "output"
                return str(output_dir / f"{filename}.xlsx")
            else:
                return default_path
                
        elif choice == '3':
            full_path = input("📁 Enter full path: ").strip()
            if full_path:
                return full_path
            else:
                return default_path
                
        else:
            print("❌ Invalid choice, using default")
            return default_path
    
    def review_and_confirm_config(self, source_file: str, target_file: str, 
                                 row_selection: Dict[str, Any], mode: str) -> bool:
        """Review configuration and get final confirmation."""
        print(f"\n" + "="*50)
        print("📋 CONFIGURATION REVIEW")
        print("="*50)
        
        print(f"📁 Source file: {source_file}")
        print(f"🎯 Products: {row_selection['description']}")
        print(f"🖥️  Mode: {mode}")
        print(f"💾 Output: {target_file}")
        print(f"⏱️  Estimated time: {self.estimate_processing_time(row_selection['product_count'])}")
        
        print(f"\n" + "-"*50)
        
        confirm = input("👉 Everything looks good? Start scraping? (Y/n): ").strip().lower()
        return confirm in ['', 'y', 'yes']
    
    def direct_scraping_execution(self, source_file: str, target_file: str,
                                 row_selection: Dict[str, Any], mode: str) -> int:
        """Execute scraping directly without subprocess when running from executable."""
        try:
            # Import required modules for direct execution
            import production_scraper  # Use WORKING production scraper directly
            from src.excel.target_writer import TargetExcelWriter
            from src.utils.config import Config
            from src.utils.logger import setup_logger
            from src.models.data_models import ProductScrapingResult
            
            print(f"✅ Running direct scraping (executable mode)")
            print(f"📁 Source: {source_file}")
            print(f"📁 Target: {target_file}")
            print(f"🎯 Mode: {mode}")
            
            # Setup configuration
            config = Config("config/default_config.json" if os.path.exists("config/default_config.json") else None)
            
            # Setup logging
            log_level = config.get("logging.level", "INFO")
            log_file = config.get("logging.file", "logs/scraper.log")
            logger = setup_logger("main", log_level, log_file)
            
            # Apply mode to config
            if mode == "headless":
                config.set("scraper.headless", True)
                config.set("scraper.minimize", False)
            elif mode == "minimal":
                config.set("scraper.headless", False)
                config.set("scraper.minimize", True)
            else:  # explicit
                config.set("scraper.headless", False)
                config.set("scraper.minimize", False)
            
            # Read products from source
            print("📖 Reading products from source Excel...")
            products = self.scraper_service.get_source_products(source_file)
            print(f"✅ Found {len(products)} products")
            
            # Apply row range filter if specified
            if row_selection['type'] == 'custom_range':
                start_row = row_selection['start_row']
                end_row = row_selection['end_row']
                filtered_products = [p for p in products if start_row <= p.row_number <= end_row]
                products = filtered_products
                print(f"🎯 Filtered to rows {start_row}-{end_row}: {len(products)} products")
            elif row_selection['type'] == 'first_n':
                count = row_selection['count']
                products = products[:count]
                print(f"🎯 Limited to first {len(products)} products")
            
            # Initialize working production scraper
            print("🚀 Initializing WORKING production scraper...")
            
            # Set headless mode in production scraper
            if mode == "headless":
                production_scraper.HEADLESS_MODE = True
            else:
                production_scraper.HEADLESS_MODE = False
            
            # Process products with progress tracking using WORKING production scraper
            print(f"⏳ Processing {len(products)} products in {mode} mode...")
            results = []
            start_time = time.time()
            
            # Process products one by one with progress display
            for i, product in enumerate(products):
                try:
                    # Display progress
                    percent = (i / len(products)) * 100
                    print(f"\r[{i+1}/{len(products)}] ({percent:.1f}%) Processing: {product.name[:40]:<40}", end="", flush=True)
                    
                    # Create fresh driver for each product (WORKING pattern from production_scraper)
                    driver = production_scraper.create_driver()
                    
                    try:
                        # Use EXACT working production scraper method
                        search_method, model_id, final_url = production_scraper.search_product_breakthrough(driver, product.name)
                        
                        if search_method != "failed":
                            # Extract vendors using working method
                            vendor_results = production_scraper.extract_vendors_complete(driver)
                            
                            # Convert to expected format using correct production scraper keys
                            from src.models.data_models import VendorOffer
                            vendor_offers = []
                            for vendor in vendor_results:
                                offer = VendorOffer(
                                    vendor_name=vendor['vendor_name'],
                                    product_name=vendor.get('vendor_product', ''),
                                    price=vendor['vendor_price'],
                                    url=vendor.get('vendor_url', ''),
                                    button_text=vendor.get('button_text', '')
                                )
                                vendor_offers.append(offer)
                            
                            # Create successful result
                            result = ProductScrapingResult(
                                input_product=product,
                                vendor_offers=vendor_offers,
                                status="success",
                                error_message=""
                            )
                        else:
                            # Create no results result
                            result = ProductScrapingResult(
                                input_product=product,
                                vendor_offers=[],
                                status="no_results",
                                error_message="Search failed"
                            )
                    finally:
                        driver.quit()
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Failed to scrape product {product.name}: {e}")
                    # Create error result
                    results.append(ProductScrapingResult(
                        input_product=product,
                        vendor_offers=[],
                        status="error",
                        error_message=str(e)
                    ))
            
            # Final progress update
            total_time = time.time() - start_time
            print(f"\n✅ Completed in {int(total_time/60)}m {int(total_time%60)}s")
            
            # Write results
            print("💾 Writing results to Excel...")
            writer = TargetExcelWriter()
            success = writer.write_results(results, target_file)
            
            if success:
                # Print summary
                total_products = len(results)
                successful = sum(1 for r in results if r.status == "success")
                failed = sum(1 for r in results if r.status == "error")
                no_results = sum(1 for r in results if r.status == "no_results")
                
                print("\n" + "="*50)
                print("SCRAPING SUMMARY:")
                print(f"Total products: {total_products}")
                if total_products > 0:
                    print(f"✅ Successful: {successful} ({successful/total_products*100:.1f}%)")
                    print(f"⚠️  No results: {no_results}")
                    print(f"❌ Failed: {failed}")
                print("="*50)
                return 0
            else:
                print("❌ Failed to write results")
                return 1
                
        except KeyboardInterrupt:
            print("\n⚠️  Scraping interrupted by user")
            return 2
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            logger.error(f"Fatal error in direct scraping: {e}", exc_info=True)
            return 1
    
    def execute_scraping_session(self, source_file: str, target_file: str,
                                row_selection: Dict[str, Any], mode: str):
        """Execute the scraping session with the configured parameters."""
        print(f"\n" + "="*50)
        print("🚀 STARTING SCRAPING SESSION")
        print("="*50)
        
        print(f"⏳ Processing {row_selection['product_count']} products...")
        print(f"\n💡 You can press Ctrl+C to interrupt if needed")
        print("-"*50)
        
        # Choose execution method based on environment
        if RUNNING_FROM_EXECUTABLE:
            # Use direct function call when running from executable
            try:
                result_code = self.direct_scraping_execution(source_file, target_file, row_selection, mode)
                
                if result_code == 0:
                    print(f"\n✅ Scraping completed successfully!")
                    print(f"📁 Results saved to: {target_file}")
                    
                    # Generate and display post-processing summary
                    self._display_post_processing_summary(target_file, row_selection)
                else:
                    print(f"\n❌ Scraping failed with exit code {result_code}")
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Scraping interrupted by user")
            except Exception as e:
                print(f"\n❌ Error executing direct scraping: {e}")
        else:
            # Use subprocess when running from development environment
            cmd_parts = [
                "python", "src/main.py",
                "--source", source_file,
                "--target", target_file,
                "--mode", mode
            ]
            
            # Add selection parameters based on type
            if row_selection['type'] == 'first_n':
                cmd_parts.extend(["--limit", str(row_selection['count'])])
            elif row_selection['type'] == 'custom_range':
                rows_param = f"{row_selection['start_row']}-{row_selection['end_row']}"
                cmd_parts.extend(["--rows", rows_param])
            elif row_selection['type'] == 'all':
                pass  # No additional parameters needed
            else:
                cmd_parts.extend(["--limit", "5"])  # Fallback
            
            cmd_str = " ".join(cmd_parts)
            print(f"📋 Executing: {cmd_str}")
            
            import subprocess
            try:
                result = subprocess.run(cmd_parts, cwd=".", capture_output=False)
                
                if result.returncode == 0:
                    print(f"\n✅ Scraping completed successfully!")
                    # Convert to absolute path for clear logging
                    abs_target_file = str(Path(target_file).resolve())
                    print(f"📁 Results saved to: {abs_target_file}")
                    
                    # Generate and display post-processing summary
                    self._display_post_processing_summary(abs_target_file, row_selection)
                else:
                    print(f"\n❌ Scraping failed with exit code {result.returncode}")
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Scraping interrupted by user")
            except Exception as e:
                print(f"\n❌ Error executing scraping: {e}")
            
        input("\nPress Enter to continue...")
    
    def quick_test_scraping(self):
        """Quick test scraping setup."""
        print(f"\n🧪 QUICK TEST SCRAPING")
        print("Perfect for fast validation and debugging!")
        
        # Use defaults with minimal configuration
        source_file = "data/SOURCE.xlsx"
        if not os.path.exists(source_file):
            print(f"❌ Default source file not found: {source_file}")
            return
            
        # Analyze source to find optimal test product
        try:
            products_info = self.analyze_source_file(source_file)
            if not products_info:
                print(f"❌ Could not analyze source file")
                return
        except Exception as e:
            print(f"❌ Error analyzing source: {e}")
            return
            
        timestamp = datetime.now().strftime('%H%M%S')
        # Use absolute path for clear logging
        output_dir = Path.cwd() / "output"
        target_file = str(output_dir / f"quick_test_{timestamp}.xlsx")
        
        # Find optimal test product (WD 150 3PH)
        row_selection = self._find_optimal_test_product(products_info)
        
        if not row_selection:
            # Fallback to first product only
            row_selection = {
                'type': 'first_n',
                'count': 1,
                'product_count': 1,
                'description': 'First product (quick test fallback)'
            }
        
        print(f"\n⚡ Quick setup:")
        print(f"   📁 Source: {source_file}")
        print(f"   🎯 Product: {row_selection['description']}")
        print(f"   🖥️  Mode: Explicit (visible browser)")
        print(f"   💾 Output: {target_file}")
        print(f"   ⏱️  Estimated time: ~5 minutes (optimal test product)")
        
        confirm = input("\n👉 Start quick test? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.execute_scraping_session(source_file, target_file, row_selection, 'explicit')
    
    def quick_small_batch(self):
        """Small batch scraping setup (6-10 products)."""
        print(f"\n📊 SMALL BATCH SCRAPING")
        print("Ideal for focused analysis with your choice of mode!")
        
        # Get source file
        source_file = self.choose_source_file()
        if not source_file:
            return
            
        # Analyze source file
        try:
            products_info = self.analyze_source_file(source_file)
            if not products_info:
                print(f"❌ Could not analyze source file")
                return
        except Exception as e:
            print(f"❌ Error analyzing source: {e}")
            return
            
        # Suggest optimal small batch size
        total_products = products_info['total_products']
        if total_products < 6:
            suggested_count = total_products
            print(f"ℹ️  Source has {total_products} products - processing all")
        else:
            suggested_count = min(8, total_products)  # Default to 8 for small batch
            
        # Let user choose count
        print(f"\n🎯 How many products? (6-10 recommended for small batch)")
        print(f"📊 Source file has {total_products} products total")
        
        while True:
            try:
                user_input = input(f"👉 Enter count (default {suggested_count}): ").strip()
                if not user_input:
                    count = suggested_count
                    break
                count = int(user_input)
                if 1 <= count <= total_products:
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {total_products}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Choose processing mode
        mode = self.choose_scraping_mode(count)
        if not mode:
            return
            
        # Setup output file
        timestamp = datetime.now().strftime('%H%M%S')
        output_dir = Path.cwd() / "output"
        target_file = str(output_dir / f"small_batch_{count}products_{timestamp}.xlsx")
        
        # Create row selection
        row_selection = {
            'type': 'first_n',
            'count': count,
            'product_count': count,
            'description': f'First {count} products (small batch)'
        }
        
        # Show summary and confirm
        est_minutes = count * 2.5  # Rough estimate
        print(f"\n⚡ Small batch setup:")
        print(f"   📁 Source: {source_file}")
        print(f"   🎯 Products: {count} (small batch)")
        print(f"   🖥️  Mode: {mode.title()}")
        print(f"   💾 Output: {target_file}")
        print(f"   ⏱️  Estimated time: ~{est_minutes:.0f} minutes")
        
        confirm = input("\n👉 Start small batch scraping? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.execute_scraping_session(source_file, target_file, row_selection, mode)
    
    def quick_large_batch(self):
        """Large batch scraping setup (11+ products, headless mode)."""
        print(f"\n🚀 LARGE BATCH SCRAPING")
        print("Optimized for processing many products efficiently in headless mode!")
        
        # Get source file
        source_file = self.choose_source_file()
        if not source_file:
            return
            
        # Analyze source file
        try:
            products_info = self.analyze_source_file(source_file)
            if not products_info:
                print(f"❌ Could not analyze source file")
                return
        except Exception as e:
            print(f"❌ Error analyzing source: {e}")
            return
            
        total_products = products_info['total_products']
        
        if total_products < 11:
            print(f"ℹ️  Note: Source has only {total_products} products")
            print("💡 Consider using Small Batch (Option B) for better optimization")
            
        # Choose processing scope
        print(f"\n🎯 Processing scope:")
        print(f"📊 Source file has {total_products} products total")
        print(f"A. Process all {total_products} products")
        print(f"B. Process first N products")
        print(f"C. Process custom row range")
        
        scope_choice = input("\n👉 Choose scope (A/B/C): ").strip().upper()
        
        if scope_choice == 'A':
            row_selection = {
                'type': 'all',
                'product_count': total_products,
                'description': f'All {total_products} products'
            }
            count = total_products
        elif scope_choice == 'B':
            while True:
                try:
                    count = int(input(f"👉 How many products to process? (max {total_products}): "))
                    if 1 <= count <= total_products:
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {total_products}")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            row_selection = {
                'type': 'first_n',
                'count': count,
                'product_count': count,
                'description': f'First {count} products'
            }
        elif scope_choice == 'C':
            row_selection = self.get_custom_range(products_info)
            if not row_selection:
                return
            count = row_selection['product_count']
        else:
            print("❌ Invalid choice")
            return
            
        # Setup output file
        timestamp = datetime.now().strftime('%H%M%S')
        output_dir = Path.cwd() / "output"
        target_file = str(output_dir / f"large_batch_{count}products_{timestamp}.xlsx")
        
        # Large batch always uses headless mode for efficiency
        mode = 'headless'
        
        # Show summary and confirm
        est_minutes = count * 2  # Faster estimate for headless mode
        print(f"\n⚡ Large batch setup:")
        print(f"   📁 Source: {source_file}")
        print(f"   🎯 Products: {row_selection['description']}")
        print(f"   🖥️  Mode: Headless (optimized for large batches)")
        print(f"   💾 Output: {target_file}")
        print(f"   ⏱️  Estimated time: ~{est_minutes:.0f} minutes")
        print(f"   🔥 This will run in background - you can use your computer normally")
        
        confirm = input("\n👉 Start large batch scraping? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.execute_scraping_session(source_file, target_file, row_selection, mode)
    
    def quick_single_product(self):
        """Single product validation setup."""
        print(f"\n🔍 SINGLE PRODUCT VALIDATION")
        print("Perfect for testing specific products or troubleshooting!")
        
        # Get source file
        source_file = self.choose_source_file()
        if not source_file:
            return
            
        # Analyze source file
        try:
            products_info = self.analyze_source_file(source_file)
            if not products_info:
                print(f"❌ Could not analyze source file")
                return
        except Exception as e:
            print(f"❌ Error analyzing source: {e}")
            return
            
        total_products = products_info['total_products']
        
        # Let user choose which product
        print(f"\n🎯 Which product to validate?")
        print(f"📊 Source file has products in rows 4-{total_products + 3}")
        print(f"A. 🧪 Use optimal test product (if available)")
        print(f"B. 📍 Choose specific row number")
        print(f"C. 🔀 Use first product")
        
        choice = input("\n👉 Choose option (A/B/C): ").strip().upper()
        
        if choice == 'A':
            # Try to find optimal test product
            row_selection = self._find_optimal_test_product(products_info)
            if not row_selection:
                print("ℹ️  No optimal test product found, using first product")
                row_selection = {
                    'type': 'first_n',
                    'count': 1,
                    'product_count': 1,
                    'description': 'First product'
                }
        elif choice == 'B':
            while True:
                try:
                    row_num = int(input(f"👉 Enter row number (4-{total_products + 3}): "))
                    if 4 <= row_num <= total_products + 3:
                        product_index = row_num - 4  # Convert to 0-based index
                        row_selection = {
                            'type': 'custom_range',
                            'start_row': row_num,
                            'end_row': row_num,
                            'product_count': 1,
                            'description': f'Row {row_num} (single product)'
                        }
                        break
                    else:
                        print(f"❌ Please enter a row number between 4 and {total_products + 3}")
                except ValueError:
                    print("❌ Please enter a valid row number")
        elif choice == 'C':
            row_selection = {
                'type': 'first_n',
                'count': 1,
                'product_count': 1,
                'description': 'First product'
            }
        else:
            print("❌ Invalid choice")
            return
            
        # Choose processing mode
        mode = self.choose_scraping_mode(1)
        if not mode:
            return
            
        # Setup output file
        timestamp = datetime.now().strftime('%H%M%S')
        output_dir = Path.cwd() / "output"
        target_file = str(output_dir / f"single_product_{timestamp}.xlsx")
        
        # Show summary and confirm
        print(f"\n⚡ Single product setup:")
        print(f"   📁 Source: {source_file}")
        print(f"   🎯 Product: {row_selection['description']}")
        print(f"   🖥️  Mode: {mode.title()}")
        print(f"   💾 Output: {target_file}")
        print(f"   ⏱️  Estimated time: ~3-5 minutes")
        
        confirm = input("\n👉 Start single product validation? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            self.execute_scraping_session(source_file, target_file, row_selection, mode)
    
    def view_recent_results(self):
        """Show recent scraping results."""
        print(f"\n📈 RECENT SCRAPING RESULTS")
        print("="*50)
        
        try:
            results = self.results_service.get_recent_results(limit=10)
            
            if not results:
                print("📂 No result files found")
                return
            
            print(f"📊 Found {len(results)} recent result files:")
            
            for i, result in enumerate(results, 1):
                filename = result['filename']
                created_time = result.get('created_time', 'Unknown')
                file_size = result.get('file_size', 0) // 1024  # KB
                rows_processed = result.get('rows_processed', 'Unknown')
                
                if isinstance(created_time, datetime):
                    time_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = str(created_time)
                
                print(f"{i:2d}. 📄 {filename}")
                print(f"     🎯 Rows: {rows_processed} | 🕒 {time_str} | 💾 {file_size} KB")
                
                if 'total_vendors' in result:
                    print(f"     📊 Vendors: {result['total_vendors']}")
                if 'min_price' in result and 'max_price' in result:
                    print(f"     💰 Price range: ₪{result['min_price']:,.0f} - ₪{result['max_price']:,.0f}")
            
            # Additional options
            print("\n🔧 Available actions:")
            print("1. View detailed statistics")
            print("2. Open a specific file")
            print("3. Search results")
            print("4. Return to main menu")
            
            choice = input("\n👉 Enter choice (1-4): ").strip()
            
            if choice == '1':
                self._show_detailed_statistics()
            elif choice == '2':
                self._open_specific_file(results)
            elif choice == '3':
                self._search_results()
            
        except Exception as e:
            logger.error(f"Error in view_recent_results: {e}")
            print(f"❌ Error loading results: {e}")
            
        input("\nPress Enter to continue...")
    
    def system_status_check(self):
        """Check system status and performance."""
        print(f"\n🔍 SYSTEM STATUS CHECK")
        print("="*50)
        
        try:
            # Get comprehensive system status
            status = self.status_service.get_system_status()
            
            # System health
            print("🧾 System Health:")
            health = status.get('system_health', {})
            print(f"   🖥️  CPU Usage: {health.get('cpu_usage', 'Unknown')}%")
            print(f"   💾 Memory Usage: {health.get('memory_usage', 'Unknown')}%")
            print(f"   💽 Disk Usage: {health.get('disk_usage', 'Unknown')}%")
            print(f"   🐍 Python: {health.get('python_version', 'Unknown')}")
            
            # Scraper status
            print(f"\n🔧 Scraper Components:")
            scraper_status = status.get('scraper_status', {})
            components = [
                ("Production Scraper", scraper_status.get('production_scraper_exists', False)),
                ("Excel Validator", scraper_status.get('excel_validator_exists', False)),
                ("Source File", scraper_status.get('source_file_exists', False)),
                ("Chrome Browser", scraper_status.get('chrome_available', False))
            ]
            
            for name, available in components:
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {name}")
            
            overall_ready = scraper_status.get('scraper_ready', False)
            print(f"\n🎯 Overall Status: {'✅ READY' if overall_ready else '❌ NOT READY'}")
            
            # Recent activity
            print(f"\n📈 Recent Activity:")
            activity = status.get('recent_activity', {})
            print(f"   📊 Last 24 hours: {activity.get('last_24_hours', 0)} files")
            print(f"   📅 Last week: {activity.get('last_week', 0)} files")
            print(f"   📆 Last month: {activity.get('last_month', 0)} files")
            
            if activity.get('latest_file'):
                print(f"   📄 Latest file: {activity['latest_file']}")
            
            # File system status
            print(f"\n📂 File System:")
            fs_status = status.get('file_system_status', {})
            print(f"   📁 Output files: {fs_status.get('recent_output_files', 0)}")
            total_size = fs_status.get('total_output_size', 0) // 1024 // 1024  # MB
            print(f"   💾 Total output size: {total_size} MB")
            
            # Health check option
            print(f"\n🔧 Additional Options:")
            print("1. Run comprehensive health check")
            print("2. View performance metrics")
            print("3. Return to main menu")
            
            choice = input("\n👉 Enter choice (1-3): ").strip()
            
            if choice == '1':
                self._run_comprehensive_health_check()
            elif choice == '2':
                self._show_performance_metrics()
                
        except Exception as e:
            logger.error(f"Error in system_status_check: {e}")
            print(f"❌ Error checking system status: {e}")
            
        input("\nPress Enter to continue...")
    
    def show_help_and_examples(self):
        """Show help and usage examples."""
        print(f"\n❓ HELP AND EXAMPLES")
        print("="*70)
        
        print("🚀 UNIVERSAL PRODUCT SCRAPER GUIDE")
        print("-" * 40)
        
        print("\n📋 What this tool does:")
        print("   • Scrapes product prices from ZAP.co.il")
        print("   • Compares prices across multiple vendors")
        print("   • Exports results to Excel with price analysis")
        
        print("\n🎯 Quick start recommendations:")
        print("   1. 🧪 Start with 'Quick Wizard' → 'Quick test' (2 products)")
        print("   2. 📊 Use small batches (6-10 products) once comfortable")
        print("   3. 🚀 Scale up to larger batches for production use")
        
        print("\n⚡ Processing modes explained:")
        print("   • Explicit: Shows browser (good for debugging)")
        print("   • Headless: No browser window (faster)")
        print("   • Minimal: Browser minimized (balanced)")
        
        print("\n📏 Batch size guidelines:")
        print("   • 2 products: Quick test (10 min)")
        print("   • 6-10 products: Small batch (30-50 min)")
        print("   • 11+ products: Large batch (1+ hours, auto headless)")
        
        print("\n💡 Pro tips:")
        print("   • Always test with small batches first")
        print("   • Headless mode is best for large batches")
        print("   • Check 'View recent results' to see past scraping")
        print("   • Use 'System status' if something seems wrong")
        
        input("\nPress Enter to continue...")
    
    def _is_file_path(self, input_str: str) -> bool:
        """Check if input string looks like a file path rather than a menu option."""
        # Clean the input string - remove quotes and extra whitespace
        cleaned_input = input_str.strip().strip('"').strip("'")
        
        # If it's just a single digit, it's likely a menu option
        if cleaned_input in ['1', '2', '3', '4', '5', '6']:
            return False
            
        # If it contains path separators or drive letters, it's likely a path
        path_indicators = [
            '\\',           # Windows backslash
            '/',            # Forward slash
            ':',            # Drive letter colon (C:)
            '.xlsx',        # Excel file extension
            '.xls',         # Old Excel extension
            'data/',        # Data directory reference
            'Google Drive', # Google Drive folder name
            'My Drive',     # Google Drive mount name
            'SW_PLATFORM',  # Project directory name
            'Skywind_Uni_Prod_Scrap_Protected'  # Project folder name
        ]
        
        # Check if any path indicator is present (case-insensitive for folder names)
        for indicator in path_indicators:
            if indicator.lower() in cleaned_input.lower():
                logger.debug(f"Path indicator '{indicator}' found in input: {cleaned_input}")
                return True
        
        # Additional heuristics: if it's longer than 10 characters and contains specific patterns
        if len(cleaned_input) > 10:
            # Check for drive letter pattern (C:\, D:\, etc.)
            if len(cleaned_input) >= 3 and cleaned_input[1:3] == ':\\':
                logger.debug(f"Drive letter pattern found in input: {cleaned_input}")
                return True
            
            # Check for UNC path pattern (\\server\share)
            if cleaned_input.startswith('\\\\'):
                logger.debug(f"UNC path pattern found in input: {cleaned_input}")
                return True
        
        logger.debug(f"Input '{cleaned_input}' not recognized as file path")
        return False
    
    def _normalize_file_path(self, file_path: str) -> str:
        """Normalize file path to handle different Google Drive path formats between computers."""
        # Clean the input path
        cleaned_path = file_path.strip().strip('"').strip("'")
        
        logger.debug(f"Normalizing path: {cleaned_path}")
        
        # Handle external computer Google Drive format to main computer format
        # Pattern: C:\Users\USER\Google Drive\... → G:\My Drive\...
        google_drive_patterns = [
            ("Google Drive\\", "\\"),
            ("Google Drive/", "/"),
            ("google drive\\", "\\"),  # Case insensitive
            ("google drive/", "/")
        ]
        
        for pattern, separator in google_drive_patterns:
            if pattern.lower() in cleaned_path.lower():
                # Find the pattern case-insensitively
                lower_path = cleaned_path.lower()
                pattern_index = lower_path.find(pattern.lower())
                
                if pattern_index != -1:
                    # Extract everything after "Google Drive"
                    after_google_drive = cleaned_path[pattern_index + len(pattern):]
                    # Normalize separators to backslashes
                    relative_path = after_google_drive.replace('/', '\\')
                    normalized = f"G:\\My Drive\\{relative_path}"
                    logger.debug(f"Converted external format to main: {normalized}")
                    return normalized
        
        # Handle main computer format to external computer format (if needed)
        my_drive_patterns = ["G:\\My Drive\\", "G:/My Drive/"]
        
        for pattern in my_drive_patterns:
            if pattern in cleaned_path and not os.path.exists(cleaned_path):
                # Only convert if main computer path doesn't exist
                relative_path = cleaned_path.replace(pattern, "").replace('/', '\\')
                external_format = f"C:\\Users\\USER\\Google Drive\\{relative_path}"
                logger.debug(f"Converted main format to external: {external_format}")
                return external_format
        
        # Handle case where we're already on the external computer
        # Try to detect the current environment and adjust accordingly
        if "C:\\Users\\USER\\Google Drive\\" in cleaned_path:
            logger.debug(f"Already in external computer format: {cleaned_path}")
            return cleaned_path
            
        logger.debug(f"No normalization needed: {cleaned_path}")
        return cleaned_path
    
    def _suggest_path_fixes(self, file_path: str) -> List[str]:
        """Suggest potential fixes for common path issues."""
        suggestions = []
        
        # Check if it's a Google Drive path issue
        if "Google Drive" in file_path or "My Drive" in file_path:
            # Try different Google Drive formats
            if "Google Drive\\" in file_path:
                # Try main computer format
                parts = file_path.split("Google Drive\\")
                if len(parts) > 1:
                    main_format = f"G:\\My Drive\\{parts[1]}"
                    suggestions.append(f"Try main computer format: {main_format}")
            
            if "My Drive\\" in file_path:
                # Try external computer format
                parts = file_path.split("My Drive\\")
                if len(parts) > 1:
                    external_format = f"C:\\Users\\USER\\Google Drive\\{parts[1]}"
                    suggestions.append(f"Try external computer format: {external_format}")
        
        # Check if file exists with different extension
        if file_path.endswith('.xlsx'):
            xls_path = file_path.replace('.xlsx', '.xls')
            if os.path.exists(xls_path):
                suggestions.append(f"File exists with .xls extension: {xls_path}")
        elif file_path.endswith('.xls'):
            xlsx_path = file_path.replace('.xls', '.xlsx')
            if os.path.exists(xlsx_path):
                suggestions.append(f"File exists with .xlsx extension: {xlsx_path}")
        
        # Check if relative path works
        if os.path.isabs(file_path):
            filename = os.path.basename(file_path)
            relative_candidates = [
                f"data/{filename}",
                f"./{filename}",
                filename
            ]
            for candidate in relative_candidates:
                if os.path.exists(candidate):
                    suggestions.append(f"File found using relative path: {candidate}")
                    break
        
        # Check common data directory locations
        if not file_path.startswith("data/"):
            filename = os.path.basename(file_path)
            data_path = f"data/{filename}"
            if os.path.exists(data_path):
                suggestions.append(f"File found in data directory: {data_path}")
        
        return suggestions

    # Helper methods for enhanced CLI functionality
    def _show_detailed_statistics(self):
        """Show detailed statistics about scraping results."""
        try:
            stats = self.results_service.get_statistics()
            
            print(f"\n📊 DETAILED STATISTICS")
            print("="*50)
            
            print(f"📁 Total Files: {stats.get('total_files', 0)}")
            
            if 'date_range' in stats:
                earliest = stats['date_range'].get('earliest')
                latest = stats['date_range'].get('latest')
                if earliest and latest:
                    print(f"📅 Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
            
            print(f"🏪 Total Vendors Processed: {stats.get('total_vendors_processed', 0)}")
            print(f"📊 Average Vendors per File: {stats.get('average_vendors_per_file', 0):.1f}")
            
            if 'price_range' in stats:
                price_range = stats['price_range']
                print(f"💰 Price Range: ₪{price_range.get('lowest', 0):,.0f} - ₪{price_range.get('highest', 0):,.0f}")
                print(f"💰 Average Price: ₪{price_range.get('average', 0):,.0f}")
            
            total_size_mb = stats.get('total_file_size', 0) // 1024 // 1024
            print(f"💾 Total Storage Used: {total_size_mb} MB")
            
        except Exception as e:
            print(f"❌ Error loading detailed statistics: {e}")
    
    def _open_specific_file(self, results):
        """Allow user to open a specific Excel file."""
        try:
            print(f"\n📂 Select file to open:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['filename']}")
            
            choice = input(f"\n👉 Enter file number (1-{len(results)}): ").strip()
            
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(results):
                    file_path = results[file_index]['file_path']
                    if self.results_service.open_excel_file(file_path):
                        print(f"✅ Opened {results[file_index]['filename']}")
                    else:
                        print(f"❌ Failed to open file")
                else:
                    print("❌ Invalid file number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        except Exception as e:
            print(f"❌ Error opening file: {e}")
    
    def _search_results(self):
        """Search through results."""
        try:
            search_term = input("\n🔍 Enter search term (row number, product name, etc.): ").strip()
            
            if not search_term:
                print("❌ Search term cannot be empty")
                return
            
            results = self.results_service.search_results(search_term)
            
            if not results:
                print(f"❌ No results found for '{search_term}'")
                return
            
            print(f"\n🎯 Found {len(results)} matches for '{search_term}':")
            
            for i, result in enumerate(results, 1):
                filename = result['filename']
                rows_processed = result.get('rows_processed', 'Unknown')
                created_time = result.get('created_time', 'Unknown')
                
                if isinstance(created_time, datetime):
                    time_str = created_time.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = str(created_time)
                
                print(f"{i}. 📄 {filename}")
                print(f"   🎯 Rows: {rows_processed} | 🕒 {time_str}")
                
        except Exception as e:
            print(f"❌ Error searching results: {e}")
    
    def _run_comprehensive_health_check(self):
        """Run comprehensive health check."""
        try:
            print(f"\n🔍 Running comprehensive health check...")
            
            health_check = self.status_service.run_health_check()
            
            overall_status = health_check.get('overall_status', 'UNKNOWN')
            print(f"\n🎯 Overall Status: {overall_status}")
            
            # Show individual checks
            checks = health_check.get('checks', {})
            for check_name, check_result in checks.items():
                status = check_result.get('status', 'UNKNOWN')
                status_icon = {"OK": "✅", "WARNING": "⚠️", "CRITICAL": "❌", "ERROR": "🔴"}.get(status, "❓")
                print(f"   {status_icon} {check_name.replace('_', ' ').title()}: {status}")
            
            # Show recommendations
            recommendations = health_check.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
            
            # Show critical issues
            critical_issues = health_check.get('critical_issues', [])
            if critical_issues:
                print(f"\n🚨 Critical Issues:")
                for issue in critical_issues:
                    print(f"   • {issue}")
                    
        except Exception as e:
            print(f"❌ Error running health check: {e}")
    
    def _show_performance_metrics(self):
        """Show performance metrics."""
        try:
            print(f"\n📈 PERFORMANCE METRICS")
            print("="*50)
            
            # Get system status for performance data
            status = self.status_service.get_system_status()
            
            # Performance metrics from status
            performance = status.get('performance_metrics', {})
            
            print(f"⏱️  Average Processing Time: {performance.get('average_processing_time', 'Not available')}")
            print(f"🏪 Average Vendors per Product: {performance.get('average_vendors_per_product', 'Not available')}")
            print(f"✅ Success Rate: {performance.get('success_rate', 'Not available')}")
            print(f"📈 Performance Trend: {performance.get('performance_trend', 'Not available')}")
            
            # Current system metrics
            health = status.get('system_health', {})
            print(f"\n💻 Current System Performance:")
            print(f"   🖥️  CPU: {health.get('cpu_usage', 'Unknown')}% ({health.get('cpu_status', 'Unknown')})")
            print(f"   💾 Memory: {health.get('memory_usage', 'Unknown')}% ({health.get('memory_status', 'Unknown')})")
            
            if performance.get('note'):
                print(f"\nℹ️  Note: {performance['note']}")
                
        except Exception as e:
            print(f"❌ Error loading performance metrics: {e}")
    
    def _display_post_processing_summary(self, excel_file_path: str, row_selection: Dict[str, Any]):
        """Display comprehensive post-processing summary."""
        try:
            # Determine operation type based on row selection
            operation_type = self._determine_operation_type(row_selection)
            
            # Generate summary using SummaryService
            summary = self.summary_service.generate_post_processing_summary(excel_file_path, operation_type)
            
            if "error" in summary:
                print(f"\n⚠️  Could not generate detailed summary: {summary['error']}")
                return
            
            # Display the formatted summary
            formatted_display = summary.get("formatted_display", "")
            if formatted_display:
                print(formatted_display)
            else:
                print("\n⚠️  Summary generated but no display content available")
                
        except Exception as e:
            logger.error(f"Error displaying post-processing summary: {e}")
            print(f"\n⚠️  Could not generate post-processing summary: {e}")
    
    def _determine_operation_type(self, row_selection: Dict[str, Any]) -> str:
        """Determine the operation type based on row selection parameters."""
        try:
            product_count = row_selection.get('product_count', 1)
            selection_type = row_selection.get('type', 'single')
            
            if product_count == 1:
                return "single"
            elif product_count <= 5:
                return "batch"
            elif product_count > 20 or selection_type == 'stress':
                return "stress"
            else:
                return "range"
                
        except Exception:
            return "batch"  # Default fallback


def main():
    """Main entry point for Natural Language CLI."""
    try:
        cli = NaturalLanguageCLI()
        cli.start_interactive_session()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Fatal error in Natural Language CLI: {e}")


if __name__ == "__main__":
    main() 