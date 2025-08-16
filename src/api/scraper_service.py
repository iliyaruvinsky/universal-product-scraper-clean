"""
Scraper Service - API interface for core scraping operations

This service provides a clean API interface to the main scraping functionality,
separating CLI concerns from business logic.
"""

import sys
import os
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from excel.source_reader import SourceExcelReader
from models.data_models import ProductInput


class ScraperService:
    """Service class for scraping operations."""
    
    def __init__(self):
        """Initialize scraper service."""
        self.project_root = Path(__file__).parent.parent.parent
        self.production_scraper_path = self.project_root / "production_scraper.py"
        
    def get_source_products(self, source_file: str = "data/SOURCE.xlsx") -> List[ProductInput]:
        """
        Get products from source Excel file.
        
        Args:
            source_file: Path to source Excel file
            
        Returns:
            List of ProductInput objects
        """
        try:
            reader = SourceExcelReader()
            source_path = self.project_root / source_file
            products = reader.read_products(str(source_path))
            return products
        except Exception as e:
            raise Exception(f"Failed to read source products: {e}")
    
    def validate_row_numbers(self, row_numbers: List[int], source_file: str = "data/SOURCE.xlsx") -> Tuple[bool, List[int], str]:
        """
        Validate that requested row numbers exist in source file.
        
        Args:
            row_numbers: List of row numbers to validate
            source_file: Path to source Excel file
            
        Returns:
            Tuple of (success, valid_rows, error_message)
        """
        try:
            products = self.get_source_products(source_file)
            available_rows = [p.row_number for p in products]
            
            valid_rows = []
            invalid_rows = []
            
            for row in row_numbers:
                if row in available_rows:
                    valid_rows.append(row)
                else:
                    invalid_rows.append(row)
            
            if invalid_rows:
                return False, valid_rows, f"Invalid rows: {invalid_rows}. Available rows: {min(available_rows)}-{max(available_rows)}"
            
            return True, valid_rows, ""
            
        except Exception as e:
            return False, [], f"Failed to validate rows: {e}"
    
    def get_product_info(self, row_numbers: List[int], source_file: str = "data/SOURCE.xlsx") -> List[Dict[str, Any]]:
        """
        Get product information for specific row numbers.
        
        Args:
            row_numbers: List of row numbers to get info for
            source_file: Path to source Excel file
            
        Returns:
            List of product info dictionaries
        """
        try:
            products = self.get_source_products(source_file)
            product_dict = {p.row_number: p for p in products}
            
            result = []
            for row in row_numbers:
                if row in product_dict:
                    product = product_dict[row]
                    result.append({
                        'row_number': product.row_number,
                        'name': product.name,
                        'manufacturer': product.manufacturer,
                        'model_series': product.model_series,
                        'model_number': product.model_number,
                        'price': getattr(product, 'original_price', None)
                    })
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to get product info: {e}")
    
    def run_scraping(self, row_numbers: List[int], headless: bool = True, 
                    source_file: str = "data/SOURCE.xlsx") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run scraping operation for specified row numbers.
        
        Args:
            row_numbers: List of row numbers to scrape
            headless: Whether to run in headless mode
            source_file: Path to source Excel file
            
        Returns:
            Tuple of (success, message, result_info)
        """
        try:
            # Validate rows first
            valid, validated_rows, error_msg = self.validate_row_numbers(row_numbers, source_file)
            if not valid:
                return False, error_msg, {}
            
            # Build command
            cmd = [sys.executable, str(self.production_scraper_path)]
            
            if headless:
                cmd.append("--headless")
            
            # Add rows parameter
            cmd.append("--rows")
            if len(validated_rows) == 1:
                cmd.append(str(validated_rows[0]))
            else:
                cmd.append("-".join([str(validated_rows[0]), str(validated_rows[-1])]))
            
            # Run scraping
            start_time = datetime.now()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                # Parse output for Excel file info
                output_lines = result.stdout.split('\n')
                excel_file = self._extract_excel_filename(output_lines)
                
                result_info = {
                    'processing_time': processing_time,
                    'excel_file': excel_file,
                    'rows_processed': validated_rows,
                    'mode': 'headless' if headless else 'explicit',
                    'timestamp': start_time.isoformat()
                }
                
                return True, "Scraping completed successfully", result_info
            else:
                error_msg = result.stderr or result.stdout
                return False, f"Scraping failed: {error_msg}", {'processing_time': processing_time}
                
        except Exception as e:
            return False, f"Scraping service error: {e}", {}
    
    def _extract_excel_filename(self, output_lines: List[str]) -> Optional[str]:
        """Extract Excel filename from scraper output."""
        for line in output_lines:
            if "Lines_" in line and "_Report_" in line and ".xlsx" in line:
                # Extract filename from line
                if "output/" in line:
                    start = line.find("output/")
                    end = line.find(".xlsx") + 5
                    if start != -1 and end != -1:
                        return line[start:end]
                elif ".xlsx" in line:
                    # Look for pattern like "Lines_126_Report_20250816_123456.xlsx"
                    import re
                    match = re.search(r'Lines_\d+.*?\.xlsx', line)
                    if match:
                        return f"output/{match.group()}"
        return None
    
    def get_available_rows(self, source_file: str = "data/SOURCE.xlsx") -> Tuple[int, int, int]:
        """
        Get available row range from source file.
        
        Args:
            source_file: Path to source Excel file
            
        Returns:
            Tuple of (min_row, max_row, total_count)
        """
        try:
            products = self.get_source_products(source_file)
            if not products:
                return 0, 0, 0
            
            rows = [p.row_number for p in products]
            return min(rows), max(rows), len(rows)
            
        except Exception as e:
            raise Exception(f"Failed to get available rows: {e}")
    
    def parse_row_input(self, row_input: str) -> List[int]:
        """
        Parse row input string into list of row numbers.
        
        Args:
            row_input: Input string like "126", "126-127", "2,5,10"
            
        Returns:
            List of row numbers
        """
        try:
            row_numbers = []
            
            # Handle comma-separated values
            parts = row_input.split(',')
            
            for part in parts:
                part = part.strip()
                
                # Handle range (e.g., "126-127")
                if '-' in part:
                    start, end = part.split('-', 1)
                    start_row = int(start.strip())
                    end_row = int(end.strip())
                    row_numbers.extend(range(start_row, end_row + 1))
                else:
                    # Single number
                    row_numbers.append(int(part))
            
            return sorted(list(set(row_numbers)))  # Remove duplicates and sort
            
        except ValueError as e:
            raise ValueError(f"Invalid row input format: {row_input}. Use formats like '126', '126-127', or '2,5,10'")