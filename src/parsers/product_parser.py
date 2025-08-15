"""
Product name parser for Universal Product Scraper.

Parses product names into structured components: Importer, Series, Model.
"""

import re
from typing import Dict, Optional

from src.utils.logger import get_logger


logger = get_logger(__name__)


class ProductParser:
    """Parse product names into structured components."""
    
    def __init__(self):
        """Initialize product parser with known patterns."""
        # Known importers/manufacturers
        self.known_importers = {
            'ELECTRA', 'TADIRAN', 'ELCO', 'TORNADO', 'RELAX', 
            'SUPREME', 'TITANIUM', 'אלקטרה', 'תדיראן', 'טורנדו'
        }
        
        # Common series patterns
        self.series_patterns = [
            r'AI\s+INV',
            r'SLIM\s+A\s+SQ\s+INV',
            r'TOP\s+PRO\s+INV',
            r'EMD\s+A\s+SQ',
            r'INV',
            r'INVERTER',
            r'אינוורטר'
        ]
        
        # Model number patterns
        self.model_patterns = [
            r'\d+[A-Z]?$',  # 150, 120A
            r'\d+/\d+[A-Z]*$',  # 40/1P
            r'\d+\.\d+',  # 2.5
            r'\d+\s*X\s*WIFI',  # 12 X WIFI
        ]
    
    def parse_product_components(self, product_name: str) -> Dict[str, str]:
        """
        Parse product name into components.
        
        Args:
            product_name: Full product name
            
        Returns:
            Dictionary with keys: importer, series, model
            
        Examples:
            "Electra AI INV 150" -> {
                "importer": "Electra",
                "series": "AI INV",
                "model": "150"
            }
        """
        if not product_name:
            return {"importer": "", "series": "", "model": ""}
        
        # Normalize the product name
        normalized = self._normalize_product_name(product_name)
        
        # Extract components
        importer = self.extract_importer(normalized)
        model = self.extract_model(normalized)
        series = self.extract_series(normalized, importer, model)
        
        result = {
            "importer": importer,
            "series": series,
            "model": model
        }
        
        logger.debug(f"Parsed '{product_name}' -> {result}")
        
        return result
    
    def _normalize_product_name(self, name: str) -> str:
        """Normalize product name for parsing."""
        # Basic normalization
        normalized = name.strip()
        
        # Replace multiple spaces with single space
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def extract_importer(self, product_name: str) -> str:
        """
        Extract importer/manufacturer name.
        
        Args:
            product_name: Product name
            
        Returns:
            Importer name or empty string
        """
        if not product_name:
            return ""
        
        # Check for known importers (case-insensitive)
        upper_name = product_name.upper()
        for importer in self.known_importers:
            if upper_name.startswith(importer.upper()):
                # Extract the original case version
                return product_name[:len(importer)]
        
        # If no known importer, try to extract first word
        parts = product_name.split()
        if parts:
            first_word = parts[0]
            # Check if it's likely an importer name (not a number or common word)
            if not first_word.isdigit() and len(first_word) > 2:
                return first_word
        
        return ""
    
    def extract_model(self, product_name: str) -> str:
        """
        Extract model number/identifier.
        
        Args:
            product_name: Product name
            
        Returns:
            Model number or empty string
        """
        if not product_name:
            return ""
        
        # Try each model pattern
        for pattern in self.model_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        # Fallback: look for any number at the end
        parts = product_name.split()
        if parts:
            last_part = parts[-1]
            if any(char.isdigit() for char in last_part):
                return last_part
        
        return ""
    
    def extract_series(self, product_name: str, importer: str = "", model: str = "") -> str:
        """
        Extract product series/line.
        
        Args:
            product_name: Product name
            importer: Already extracted importer (to exclude from series)
            model: Already extracted model (to exclude from series)
            
        Returns:
            Series name or empty string
        """
        if not product_name:
            return ""
        
        # Try known series patterns first
        upper_name = product_name.upper()
        for pattern in self.series_patterns:
            match = re.search(pattern, upper_name, re.IGNORECASE)
            if match:
                # Get the original case version
                start = match.start()
                end = match.end()
                return product_name[start:end].strip()
        
        # Fallback: extract middle part between importer and model
        if importer and model:
            # Remove importer from start
            remaining = product_name
            if remaining.upper().startswith(importer.upper()):
                remaining = remaining[len(importer):].strip()
            
            # Remove model from end
            if remaining.upper().endswith(model.upper()):
                remaining = remaining[:-len(model)].strip()
            
            # What's left should be the series
            if remaining and remaining != product_name:
                return remaining
        
        # Another fallback: look for INV or INVERTER
        if 'INV' in upper_name:
            # Find the word containing INV
            for word in product_name.split():
                if 'INV' in word.upper():
                    return word
        
        return ""
    
    def format_product_name(self, components: Dict[str, str]) -> str:
        """
        Format components back into a product name.
        
        Args:
            components: Dictionary with importer, series, model
            
        Returns:
            Formatted product name
        """
        parts = []
        
        if components.get("importer"):
            parts.append(components["importer"])
        
        if components.get("series"):
            parts.append(components["series"])
        
        if components.get("model"):
            parts.append(components["model"])
        
        return " ".join(parts) 