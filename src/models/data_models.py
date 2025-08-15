"""
Data Models for Universal Product Scraper

All data structures used throughout the scraping system.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ProductInput:
    """Product information from SOURCE Excel file with component-based structure."""
    row_number: int
    manufacturer: str  # יצרן / יבואן
    model_series: str  # דגם  
    model_number: str  # מספר
    original_price: float  # מחיר
    
    @property
    def name(self) -> str:
        """Combined product name from components."""
        return f"{self.manufacturer} {self.model_series} {self.model_number}".strip()
    
    @property
    def search_components(self) -> List[str]:
        """List of search components for dropdown matching."""
        return [
            self.manufacturer.strip(),
            self.model_series.strip(), 
            str(self.model_number).strip()
        ]
    
    @property
    def search_term(self) -> str:
        """Combined search term for initial ZAP search - returns ORIGINAL name without transformation."""
        # CRITICAL FIX: Return the original product name for scraper compatibility
        # The scraper handles hyphenation and dropdown selection internally
        # Transforming INV to inverter here breaks the hyphenation logic
        return self.name.strip()  # Return original name as-is
    
    @property
    def components(self) -> List[str]:
        """List of key components for AND rule validation."""
        parts = []
        if self.manufacturer: 
            parts.extend(self.manufacturer.split())
        if self.model_series: 
            parts.extend(self.model_series.split())
        if self.model_number: 
            parts.extend(str(self.model_number).split())
        return [p.strip() for p in parts if p.strip()]
    
    def __str__(self):
        return f"Product({self.row_number}: {self.name} @ ₪{self.original_price:,.2f})"


@dataclass
class VendorOffer:
    """Single vendor offer from ZAP website."""
    vendor_name: str
    product_name: str  # As shown on vendor site
    price: float
    url: str  # Final vendor URL (not ZAP redirect)
    button_text: str = ""  # Text of the button that was pressed (קנו עכשיו, לפרטים נוספים, השוואת מחירים)
    
    def __str__(self):
        return f"VendorOffer({self.vendor_name}: ₪{self.price:,.2f} - {self.url})"


@dataclass
class ProductScrapingResult:
    """Complete scraping result for a product with all vendor offers - Extended for URL construction method."""
    input_product: ProductInput
    vendor_offers: List[VendorOffer]
    status: str  # 'success', 'no_results', 'error'
    error_message: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    # New fields for URL construction method
    model_id: Optional[str] = None              # ZAP Model ID
    listing_count: Optional[int] = None         # Number of listings found
    constructed_url: Optional[str] = None       # Constructed ZAP URL
    
    def __str__(self):
        return (f"ScrapingResult({self.input_product.name}: "
                f"{len(self.vendor_offers)} vendors, status={self.status})")
    
    @property
    def is_successful(self) -> bool:
        """Check if scraping was successful."""
        return self.status == "success" and len(self.vendor_offers) > 0
    
    @property
    def has_error(self) -> bool:
        """Check if scraping had an error."""
        return self.status == "error"


@dataclass
class ProductSummary:
    """Statistical summary for a product (used in worksheet 2) - UNIFIED 17-column format."""
    product_name: str              # Column A - שם מוצר
    model_id: str                  # Column B - Model ID
    listings_found: int            # Column C - רשומות שנמצאו - Total found after filtering
    listings_processed: int        # Column D - רשומות שנגרדו - Actually scraped
    status: str                    # Column E - סטטוס
    minimum_price: float           # Column F - מחיר מינימלי
    maximum_price: float           # Column G - מחיר מקסימלי
    average_price: float           # Column H - מחיר ממוצע
    price_range: float             # Column I - טווח מחירים
    vendor_count: int              # Column J - מספר ספקים
    cheapest_vendor_name: str      # Column K - ספק הזול ביותר
    option1_url: str              # Column L - קישור ל Opt.1 (Model ID URL)
    standard_deviation: float      # Column M - סטיית תקן
    zap_reference_price: float     # Column N - מחיר מקורי (original price)
    percentage_diff_from_zap: float # Column O - % הפרש ממקור
    update_timestamp: str          # Column P - זמן עדכון
    
    def __str__(self):
        return (f"Summary({self.product_name}: "
                f"₪{self.minimum_price:,.2f}-₪{self.maximum_price:,.2f}, "
                f"{self.vendor_count} vendors)")
    
    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage from original price."""
        if self.zap_reference_price > 0:
            return ((self.zap_reference_price - self.minimum_price) / 
                    self.zap_reference_price * 100)
        return 0.0


@dataclass
class ScraperConfig:
    """Configuration for the web scraper."""
    headless: bool = False
    minimize: bool = False
    timeout: int = 30
    min_delay: int = 2
    max_delay: int = 5
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    window_size: str = "1920,1080"
    retry_attempts: int = 2
    retry_delay: int = 3
    vendor_timeout: int = 30
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ScraperConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})


@dataclass
class ExcelConfig:
    """Configuration for Excel operations."""
    start_row: int = 4
    encoding: str = "utf-8"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ExcelConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__}) 