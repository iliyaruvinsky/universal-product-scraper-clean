"""
Configuration management for Universal Product Scraper.

Handles loading configuration from JSON files and environment variables.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from src.utils.logger import get_logger


# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration from file or environment.
        
        Args:
            config_file: Path to JSON configuration file
        """
        self._config = {}
        
        # Load default configuration
        default_config_path = Path(__file__).parent.parent.parent / "config" / "default_config.json"
        if default_config_path.exists():
            self._load_json_config(str(default_config_path))
            logger.info(f"Loaded default configuration from {default_config_path}")
        
        # Load custom configuration if provided
        if config_file and os.path.exists(config_file):
            custom_config = self._load_json_config(config_file)
            self._merge_config(custom_config)
            logger.info(f"Loaded custom configuration from {config_file}")
        
        # Override with environment variables
        self._load_env_config()
    
    def _load_json_config(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {e}")
            return {}
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Recursively merge new configuration into existing."""
        def merge_dict(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
            return base
        
        merge_dict(self._config, new_config)
    
    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        # Scraper settings
        if os.getenv('HEADLESS_MODE'):
            self.set('scraper.headless', os.getenv('HEADLESS_MODE').lower() == 'true')
        if os.getenv('SCRAPER_TIMEOUT'):
            self.set('scraper.timeout', int(os.getenv('SCRAPER_TIMEOUT')))
        if os.getenv('MIN_DELAY'):
            self.set('scraper.min_delay', int(os.getenv('MIN_DELAY')))
        if os.getenv('MAX_DELAY'):
            self.set('scraper.max_delay', int(os.getenv('MAX_DELAY')))
        
        # Excel settings
        if os.getenv('EXCEL_START_ROW'):
            self.set('excel.start_row', int(os.getenv('EXCEL_START_ROW')))
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.set('logging.level', os.getenv('LOG_LEVEL'))
        if os.getenv('LOG_FILE'):
            self.set('logging.file', os.getenv('LOG_FILE'))
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Dot-separated key path (e.g., 'scraper.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_scraper_config(self) -> Dict[str, Any]:
        """Get scraper-specific configuration."""
        return self.get('scraper', {})
    
    def get_excel_config(self) -> Dict[str, Any]:
        """Get Excel-specific configuration."""
        return self.get('excel', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging-specific configuration."""
        return self.get('logging', {})
    
    def get_hebrew_config(self) -> Dict[str, Any]:
        """Get Hebrew processing configuration."""
        return self.get('hebrew', {}) 