"""
API Configuration file for DataProvider.

This file contains configuration settings for various data providers.
Copy this file to config/api_config_local.py and fill in your actual API keys.
"""

import os
from pathlib import Path

# =========================
# API Configuration
# =========================

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Interactive Brokers Configuration
IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
IB_PORT = int(os.getenv('IB_PORT', '7497'))  # 7497 for TWS, 7496 for IB Gateway
IB_CLIENT_ID = int(os.getenv('IB_CLIENT_ID', '1'))

# Alpha Vantage API (for additional market data)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')

# Polygon.io API (for US market data)
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')

# =========================
# Data Storage Configuration
# =========================

# Base data directory
DATA_BASE_PATH = Path("data")

# Raw data directory
RAW_DATA_PATH = DATA_BASE_PATH / "raw"

# Clean data directory
CLEAN_DATA_PATH = DATA_BASE_PATH / "clean"

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24

# =========================
# Data Quality Settings
# =========================

# Maximum allowed data gaps (in periods)
MAX_DATA_GAPS = 5

# Minimum required data points for validation
MIN_DATA_POINTS = 100

# Price validation thresholds
MAX_PRICE_CHANGE_PCT = 50.0  # 50% max change in one period
MIN_PRICE = 0.01  # Minimum valid price

# =========================
# Provider-Specific Settings
# =========================

# Binance settings
BINANCE_RATE_LIMIT_DELAY = 0.1  # seconds between API calls
BINANCE_MAX_RETRIES = 3

# Yahoo Finance settings
YAHOO_RATE_LIMIT_DELAY = 0.5  # seconds between API calls
YAHOO_MAX_RETRIES = 3

# Interactive Brokers settings
IB_CONNECTION_TIMEOUT = 30  # seconds
IB_REQUEST_TIMEOUT = 60  # seconds

# =========================
# Data Processing Settings
# =========================

# Default data intervals
DEFAULT_INTERVALS = {
    'crypto': '1h',
    'equities': '1d',
    'fx': '1h',
    'commodities': '1d'
}

# Data resampling options
RESAMPLE_OPTIONS = ['1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M']

# =========================
# Logging Configuration
# =========================

# Log level
LOG_LEVEL = 'INFO'

# Log file path
LOG_FILE = DATA_BASE_PATH / "logs" / "data_provider.log"

# Maximum log file size (MB)
MAX_LOG_SIZE = 10

# Number of log files to keep
LOG_BACKUP_COUNT = 5

# =========================
# Error Handling
# =========================

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds
CONNECTION_TIMEOUT = 10  # seconds

# =========================
# Validation Functions
# =========================

def validate_config():
    """Validate the configuration settings."""
    errors = []
    
    # Check required directories
    if not DATA_BASE_PATH.exists():
        errors.append(f"Data base path does not exist: {DATA_BASE_PATH}")
    
    # Check API keys (optional warnings)
    if not BINANCE_API_KEY:
        print("Warning: BINANCE_API_KEY not set. Some features may be limited.")
    
    if not ALPHA_VANTAGE_API_KEY:
        print("Warning: ALPHA_VANTAGE_API_KEY not set. Alpha Vantage features disabled.")
    
    if not POLYGON_API_KEY:
        print("Warning: POLYGON_API_KEY not set. Polygon.io features disabled.")
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
    
    return True

def get_provider_config(provider: str) -> dict:
    """
    Get configuration for a specific provider.
    
    Args:
        provider: Provider name ('binance', 'ib', 'yahoo', etc.)
        
    Returns:
        Dictionary with provider-specific configuration
    """
    configs = {
        'binance': {
            'api_key': BINANCE_API_KEY,
            'api_secret': BINANCE_API_SECRET,
            'rate_limit_delay': BINANCE_RATE_LIMIT_DELAY,
            'max_retries': BINANCE_MAX_RETRIES
        },
        'ib': {
            'host': IB_HOST,
            'port': IB_PORT,
            'client_id': IB_CLIENT_ID,
            'connection_timeout': IB_CONNECTION_TIMEOUT,
            'request_timeout': IB_REQUEST_TIMEOUT
        },
        'yahoo': {
            'rate_limit_delay': YAHOO_RATE_LIMIT_DELAY,
            'max_retries': YAHOO_MAX_RETRIES
        }
    }
    
    return configs.get(provider, {})

# =========================
# Environment Setup
# =========================

def setup_environment():
    """Setup the environment for data providers."""
    # Create necessary directories
    DATA_BASE_PATH.mkdir(exist_ok=True)
    RAW_DATA_PATH.mkdir(exist_ok=True)
    CLEAN_DATA_PATH.mkdir(exist_ok=True)
    (DATA_BASE_PATH / "logs").mkdir(exist_ok=True)
    
    # Create asset type subdirectories
    asset_types = ['Crypto', 'Equities', 'FX', 'Commodities', 'FixedIncome']
    for asset_type in asset_types:
        (RAW_DATA_PATH / asset_type).mkdir(exist_ok=True)
        (CLEAN_DATA_PATH / asset_type).mkdir(exist_ok=True)
    
    # Validate configuration
    validate_config()
    
    print("✅ Environment setup completed successfully!")

if __name__ == "__main__":
    setup_environment()
