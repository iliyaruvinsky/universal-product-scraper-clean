"""
Hebrew text processing utilities for Universal Product Scraper.

Handles Hebrew text normalization, encoding, and matching.
"""

import re
import unicodedata
from typing import Optional
from urllib.parse import quote

from src.utils.logger import get_logger


logger = get_logger(__name__)


class HebrewTextProcessor:
    """Process and normalize Hebrew text."""
    
    def __init__(self):
        """Initialize Hebrew text processor."""
        # Hebrew character range
        self.hebrew_range = (0x0590, 0x05FF)
        
        # Common Hebrew punctuation replacements
        self.hebrew_punctuation = {
            '״': '"',  # Gershayim
            '׳': "'",  # Geresh
            '־': '-',  # Maqaf
        }
    
    def normalize_hebrew(self, text: str) -> str:
        """
        Normalize Hebrew text for consistent processing.
        
        Args:
            text: Hebrew or mixed Hebrew-English text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Unicode normalization (NFC - Canonical Decomposition, followed by Canonical Composition)
        text = unicodedata.normalize('NFC', text)
        
        # Remove zero-width characters
        text = text.replace('\u200e', '')  # Left-to-right mark
        text = text.replace('\u200f', '')  # Right-to-left mark
        text = text.replace('\u202a', '')  # Left-to-right embedding
        text = text.replace('\u202b', '')  # Right-to-left embedding
        text = text.replace('\u202c', '')  # Pop directional formatting
        text = text.replace('\u202d', '')  # Left-to-right override
        text = text.replace('\u202e', '')  # Right-to-left override
        
        # Normalize Hebrew punctuation
        for hebrew_char, replacement in self.hebrew_punctuation.items():
            text = text.replace(hebrew_char, replacement)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def encode_for_url(self, text: str) -> str:
        """
        Encode Hebrew text for URL usage.
        
        Args:
            text: Hebrew text
            
        Returns:
            URL-encoded string
        """
        # Normalize first
        text = self.normalize_hebrew(text)
        
        # URL encode with UTF-8
        return quote(text, safe='')
    
    def calculate_match_score(self, search_term: str, result_text: str) -> float:
        """
        Calculate similarity score between texts.
        
        Args:
            search_term: Original search term
            result_text: Text to compare against
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Normalize both texts
        search_normalized = self.normalize_hebrew(search_term.lower())
        result_normalized = self.normalize_hebrew(result_text.lower())
        
        if not search_normalized or not result_normalized:
            return 0.0
        
        # Exact match
        if search_normalized == result_normalized:
            return 1.0
        
        # Contains match
        if search_normalized in result_normalized:
            # Calculate overlap percentage
            overlap = len(search_normalized) / len(result_normalized)
            return min(overlap * 1.5, 0.95)  # Boost score but cap below exact match
        
        # Word-level matching
        search_words = set(search_normalized.split())
        result_words = set(result_normalized.split())
        
        if not search_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = search_words.intersection(result_words)
        union = search_words.union(result_words)
        
        if not union:
            return 0.0
        
        jaccard_score = len(intersection) / len(union)
        
        # Also consider word order similarity
        common_words = len(intersection)
        total_words = len(search_words)
        word_coverage = common_words / total_words if total_words > 0 else 0
        
        # Combine scores (weighted average)
        final_score = (jaccard_score * 0.4) + (word_coverage * 0.6)
        
        return min(final_score, 0.9)  # Cap below contains match
    
    def extract_price_from_hebrew(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from Hebrew text.
        
        Args:
            price_text: Text containing price (e.g., "₪ 1,234", "מחיר: 1234 ש״ח")
            
        Returns:
            Float price or None if not found
        """
        if not price_text:
            return None
        
        # Normalize text
        text = self.normalize_hebrew(price_text)
        
        # Remove currency symbols and Hebrew price indicators
        text = text.replace('₪', '')
        text = text.replace('ש"ח', '')
        text = text.replace('שח', '')
        text = text.replace('מחיר:', '')
        text = text.replace('מחיר', '')
        
        # Find numeric pattern (supports comma as thousands separator)
        # Matches: 1234, 1,234, 1234.56, 1,234.56
        pattern = r'[\d,]+\.?\d*'
        match = re.search(pattern, text)
        
        if match:
            try:
                # Remove commas and convert to float
                price_str = match.group().replace(',', '')
                price = float(price_str)
                
                # Sanity check - prices should be reasonable
                if 0 < price < 1000000:  # Between 0 and 1 million shekels
                    return price
                else:
                    logger.warning(f"Extracted price {price} seems unreasonable")
                    return None
            except ValueError:
                logger.warning(f"Failed to convert '{match.group()}' to float")
                return None
        
        return None
    
    def is_hebrew(self, text: str) -> bool:
        """
        Check if text contains Hebrew characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Hebrew characters
        """
        if not text:
            return False
        
        for char in text:
            if self.hebrew_range[0] <= ord(char) <= self.hebrew_range[1]:
                return True
        
        return False
    
    def remove_hebrew(self, text: str) -> str:
        """
        Remove Hebrew characters from text.
        
        Args:
            text: Mixed language text
            
        Returns:
            Text with Hebrew characters removed
        """
        if not text:
            return ""
        
        result = []
        for char in text:
            if not (self.hebrew_range[0] <= ord(char) <= self.hebrew_range[1]):
                result.append(char)
        
        return ''.join(result).strip()
    
    def extract_english_from_mixed(self, text: str) -> str:
        """
        Extract English/Latin characters from mixed Hebrew-English text.
        
        Args:
            text: Mixed language text
            
        Returns:
            English text only
        """
        if not text:
            return ""
        
        # Keep only ASCII letters, numbers, and basic punctuation
        english_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        # Clean up extra spaces
        english_text = ' '.join(english_text.split())
        
        return english_text.strip() 