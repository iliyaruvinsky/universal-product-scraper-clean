"""
Custom exception classes for Universal Product Scraper.

Provides specific exceptions for different error scenarios.
"""


class ScraperException(Exception):
    """Base exception for all scraper errors."""
    pass


class WebDriverException(ScraperException):
    """WebDriver initialization or operation errors."""
    pass


class ExcelException(ScraperException):
    """Excel file reading/writing errors."""
    pass


class ProductNotFoundException(ScraperException):
    """Product not found on ZAP website."""
    pass


class RateLimitException(ScraperException):
    """Rate limiting or bot detection."""
    pass


class ConfigurationException(ScraperException):
    """Configuration related errors."""
    pass


class HebrewProcessingException(ScraperException):
    """Hebrew text processing errors."""
    pass


class ValidationException(ScraperException):
    """Data validation errors."""
    pass 