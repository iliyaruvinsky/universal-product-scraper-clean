"""
API Interface Layer for Universal Product Scraper

This module provides a clean API interface between the CLI and core scraping engine,
enabling modular architecture and multiple interface possibilities.
"""

from .scraper_service import ScraperService
from .validation_service import ValidationService  
from .results_service import ResultsService
from .status_service import StatusService
from .summary_service import SummaryService

__all__ = [
    'ScraperService',
    'ValidationService', 
    'ResultsService',
    'StatusService',
    'SummaryService'
]