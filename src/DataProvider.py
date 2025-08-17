import os
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import json
import requests
from pathlib import Path
import yfinance as yf
from binance.client import Client
from binance.exceptions import BinanceAPIException
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# Base Data Provider Class
# =========================
class BaseDataProvider(ABC):
    """
    Abstract base class for all data providers.
    
    This class defines the interface that all data providers must implement.
    Subclasses should handle authentication, API calls, and data retrieval
    for specific service providers.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize the data provider.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self) -> None:
        """Setup the API client for the provider."""
        pass
    
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                   interval: str = '1d') -> pd.DataFrame:
        """
        Fetch historical data for a given symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            interval: Data interval (e.g., '1d', '1h', '1m')
            
        Returns:
            DataFrame with OHLCV data (Open, High, Low, Close, Volume columns)
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from the provider."""
        pass
    
    def validate_credentials(self) -> bool:
        """Validate API credentials."""
        try:
            # Test with a simple API call
            symbols = self.get_available_symbols()
            return len(symbols) > 0
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False

# =========================
# Binance Provider
# =========================
class BinanceProvider(BaseDataProvider):
    """
    Binance API integration for cryptocurrency data.
    
    Supports spot and futures markets with various timeframes.
    """
    
    def _setup_client(self) -> None:
        """Setup Binance client."""
        try:
            if self.api_key and self.api_secret:
                self.client = Client(self.api_key, self.api_secret)
            else:
                # Use public client for basic data
                self.client = Client()
            logger.info("Binance client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            self.client = None
    
    def fetch_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                   interval: str = '1d') -> pd.DataFrame:
        """
        Fetch historical data from Binance.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            start_date: Start date
            end_date: End date
            interval: Kline interval ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
            
        Returns:
            DataFrame with OHLCV data (Open, High, Low, Close, Volume columns)
        """
        if not self.client:
            raise RuntimeError("Binance client not initialized")
        
        try:
            # Convert interval to Binance format
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY,
                '1w': Client.KLINE_INTERVAL_1WEEK
            }
            
            binance_interval = interval_map.get(interval, Client.KLINE_INTERVAL_1DAY)
            
            # Fetch klines
            klines = self.client.get_historical_klines(
                symbol, binance_interval, start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Process data
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Convert to numeric
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Select only OHLCV columns and rename to standard format
            ohlcv_data = df[['open', 'high', 'low', 'close', 'volume']].copy()
            ohlcv_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            return ohlcv_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching Binance data: {e}")
            raise
    
    def get_available_symbols(self) -> List[str]:
        """Get available trading pairs from Binance."""
        try:
            if not self.client:
                return []
            
            exchange_info = self.client.get_exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING']
            return symbols
        except Exception as e:
            logger.error(f"Error getting Binance symbols: {e}")
            return []

# =========================
# Interactive Brokers Provider
# =========================
class InteractiveBrokersProvider(BaseDataProvider):
    """
    Interactive Brokers API integration for equities, ETFs, and other instruments.
    
    Note: This is a placeholder implementation. IB API requires additional setup
    and the ib_insync library for full functionality.
    """
    
    def _setup_client(self) -> None:
        """Setup Interactive Brokers client."""
        try:
            # Placeholder - would use ib_insync library
            logger.warning("Interactive Brokers provider not fully implemented")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize IB client: {e}")
            self.client = None
    
    def fetch_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                   interval: str = '1d') -> pd.DataFrame:
        """
        Fetch historical data from Interactive Brokers.
        
        This is a placeholder implementation.
        """
        raise NotImplementedError("Interactive Brokers provider not fully implemented")
    
    def get_available_symbols(self) -> List[str]:
        """Get available symbols from Interactive Brokers."""
        return []

# =========================
# Yahoo Finance Provider
# =========================
class YahooFinanceProvider(BaseDataProvider):
    """
    Yahoo Finance provider for equities, ETFs, and other instruments.
    
    Uses yfinance library for data retrieval.
    """
    
    def _setup_client(self) -> None:
        """Setup Yahoo Finance client."""
        self.client = None  # yfinance doesn't require a client object
    
    def fetch_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                   interval: str = '1d') -> pd.DataFrame:
        """
        Fetch historical data from Yahoo Finance.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'SPY')
            start_date: Start date
            end_date: End date
            interval: Data interval ('1d', '1wk', '1mo')
            
        Returns:
            DataFrame with OHLCV data (Open, High, Low, Close, Volume columns)
        """
        try:
            # Download data using yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Ensure columns are in the expected format
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Select only the required columns in the correct order
            df = df[expected_columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data: {e}")
            raise
    
    def get_available_symbols(self) -> List[str]:
        """Get available symbols from Yahoo Finance."""
        # Yahoo Finance doesn't provide a symbol list API
        # Return common symbols
        return ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'SPY', 'QQQ', 'IWM']

# =========================
# Data Processor
# =========================
class DataProcessor:
    """
    Handles data cleaning, validation, and formatting for backtesting.
    
    Converts raw data from various providers into a standardized format
    suitable for the Backtester class.
    """
    
    @staticmethod
    def clean_data(df: pd.DataFrame, asset_type: str) -> pd.DataFrame:
        """
        Clean and standardize data for backtesting.
        
        Args:
            df: Raw data DataFrame with OHLCV columns
            asset_type: Type of asset ('Crypto', 'Equities', 'FX', etc.)
            
        Returns:
            Cleaned DataFrame ready for backtesting
        """
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Make a copy to avoid modifying original
        clean_df = df.copy()
        
        # Remove any rows with all NaN values
        clean_df = clean_df.dropna(how='all')
        
        # Forward fill missing values for OHLC data
        for field in ['Open', 'High', 'Low', 'Close']:
            if field in clean_df.columns:
                clean_df[field] = clean_df[field].fillna(method='ffill')
        
        # Volume can be filled with 0
        if 'Volume' in clean_df.columns:
            clean_df['Volume'] = clean_df['Volume'].fillna(0)
        
        # Remove any remaining NaN values
        clean_df = clean_df.dropna()
        
        # Ensure index is sorted
        clean_df = clean_df.sort_index()
        
        # Validate data quality
        DataProcessor._validate_data(clean_df, asset_type)
        
        return clean_df
    
    @staticmethod
    def _validate_data(df: pd.DataFrame, asset_type: str) -> None:
        """
        Validate data quality and consistency.
        
        Args:
            df: DataFrame to validate
            asset_type: Type of asset for validation rules
        """
        # Check for negative prices
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in df.columns and (df[col] < 0).any():
                raise ValueError(f"Negative prices found in {asset_type} data column {col}")
        
        # Check for zero prices
        for col in price_columns:
            if col in df.columns and (df[col] == 0).any():
                logger.warning(f"Zero prices found in {asset_type} data column {col}")
        
        # Check for extreme price movements (>1000% in one period)
        if 'Close' in df.columns:
            returns = df['Close'].pct_change()
            extreme_moves = (returns.abs() > 10).any()
            if extreme_moves:
                logger.warning(f"Extreme price movements detected in {asset_type} data")
    
    @staticmethod
    def resample_data(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
        """
        Resample data to a different frequency.
        
        Args:
            df: Input DataFrame with OHLCV columns
            target_freq: Target frequency ('1D', '1H', '1W', etc.)
            
        Returns:
            Resampled DataFrame
        """
        resampled = {}
        
        # Resample each field appropriately
        if 'Volume' in df.columns:
            # Volume should be summed
            resampled['Volume'] = df['Volume'].resample(target_freq).sum()
        
        # OHLC should use appropriate aggregation
        if 'Open' in df.columns:
            resampled['Open'] = df['Open'].resample(target_freq).first()
        if 'High' in df.columns:
            resampled['High'] = df['High'].resample(target_freq).max()
        if 'Low' in df.columns:
            resampled['Low'] = df['Low'].resample(target_freq).min()
        if 'Close' in df.columns:
            resampled['Close'] = df['Close'].resample(target_freq).last()
        
        # Combine all fields
        result = pd.concat(resampled.values(), axis=1, keys=resampled.keys())
        
        return result.dropna()

# =========================
# Data Manager
# =========================
class DataManager:
    """
    Orchestrates the entire data pipeline from fetching to backtesting.
    
    Manages data storage, organization, and provides easy access to
    processed data for backtesting.
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize the data manager.
        
        Args:
            base_path: Base path for data storage
        """
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.clean_path = self.base_path / "clean"
        
        # Create directory structure
        self._create_directories()
        
        # Initialize providers
        self.providers = {
            'binance': BinanceProvider(),
            'yahoo': YahooFinanceProvider(),
            'ib': InteractiveBrokersProvider()
        }
        
        # Asset type mapping
        self.asset_type_map = {
            'binance': 'Crypto',
            'yahoo': 'Equities',
            'ib': 'Equities'
        }
    
    def _create_directories(self) -> None:
        """Create the necessary directory structure."""
        asset_types = ['Crypto', 'Equities', 'FX', 'Commodities', 'FixedIncome']
        
        for asset_type in asset_types:
            (self.raw_path / asset_type).mkdir(parents=True, exist_ok=True)
            (self.clean_path / asset_type).mkdir(parents=True, exist_ok=True)
    
    def _get_data_file_paths(self, provider: str, symbol: str, start_date: datetime, 
                             end_date: datetime, interval: str) -> tuple:
        """
        Get file paths for raw and clean data.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date for data (not used in filename)
            end_date: End date for data (not used in filename)
            interval: Data interval
            
        Returns:
            Tuple of (raw_file_path, clean_file_path)
        """
        asset_type = self.asset_type_map[provider]
        # Store data by asset name and interval only, not by date range
        filename = f"{symbol}_{interval}.parquet"
        raw_file = self.raw_path / asset_type / filename
        clean_file = self.clean_path / asset_type / filename
        return raw_file, clean_file
    
    def _check_data_completeness(self, df: pd.DataFrame, start_date: datetime, 
                                end_date: datetime, interval: str) -> dict:
        """
        Check if existing data covers the requested date range completely.
        
        Args:
            df: Existing DataFrame
            start_date: Requested start date
            end_date: Requested end date
            interval: Data interval
            
        Returns:
            Dictionary with completeness information
        """
        if df.empty:
            return {
                'is_complete': False,
                'missing_ranges': [(start_date, end_date)],
                'existing_range': None,
                'coverage_percentage': 0.0,
                'total_requested_days': (end_date - start_date).days,
                'existing_days': 0,
                'missing_days': (end_date - start_date).days
            }
        
        # Get the actual date range of existing data
        existing_start = df.index.min()
        existing_end = df.index.max()
        
        # Convert to datetime if needed
        if isinstance(existing_start, pd.Timestamp):
            existing_start = existing_start.to_pydatetime()
        if isinstance(existing_end, pd.Timestamp):
            existing_end = existing_end.to_pydatetime()
        
        # Check if requested range is fully covered
        if existing_start <= start_date and existing_end >= end_date:
            return {
                'is_complete': True,
                'missing_ranges': [],
                'existing_range': (existing_start, existing_end),
                'coverage_percentage': 100.0,
                'total_requested_days': (end_date - start_date).days,
                'existing_days': (end_date - start_date).days,
                'missing_days': 0
            }
        
        # Calculate coverage percentage
        total_requested_days = (end_date - start_date).days
        if total_requested_days == 0:
            coverage = 100.0 if existing_start <= start_date <= existing_end else 0.0
            existing_days = 1 if existing_start <= start_date <= existing_end else 0
        else:
            covered_days = 0
            if existing_start <= start_date <= existing_end:
                covered_days += (existing_end - start_date).days
            elif existing_start <= end_date <= existing_end:
                covered_days += (end_date - existing_start).days
            elif start_date <= existing_start <= end_date and start_date <= existing_end <= end_date:
                covered_days += (existing_end - existing_start).days
            
            coverage = (covered_days / total_requested_days) * 100
            existing_days = covered_days
        
        # Identify missing ranges
        missing_ranges = []
        
        if start_date < existing_start:
            missing_ranges.append((start_date, existing_start))
        
        if end_date > existing_end:
            missing_ranges.append((existing_end, end_date))
        
        missing_days = total_requested_days - existing_days
        
        return {
            'is_complete': False,
            'missing_ranges': missing_ranges,
            'existing_range': (existing_start, existing_end),
            'coverage_percentage': coverage,
            'total_requested_days': total_requested_days,
            'existing_days': existing_days,
            'missing_days': missing_days
        }
    
    def _fetch_missing_data(self, provider: str, symbol: str, missing_ranges: list, 
                           interval: str) -> pd.DataFrame:
        """
        Fetch data for missing date ranges.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            missing_ranges: List of (start_date, end_date) tuples for missing data
            interval: Data interval
            
        Returns:
            DataFrame with missing data
        """
        all_missing_data = []
        
        for start_date, end_date in missing_ranges:
            try:
                logger.info(f"Fetching missing data for {symbol} from {start_date} to {end_date}")
                missing_data = self.providers[provider].fetch_data(symbol, start_date, end_date, interval)
                all_missing_data.append(missing_data)
            except Exception as e:
                logger.error(f"Failed to fetch missing data for {symbol} from {start_date} to {end_date}: {e}")
                # Continue with other ranges
                continue
        
        if not all_missing_data:
            return pd.DataFrame()
        
        # Combine all missing data
        combined_missing = pd.concat(all_missing_data)
        return combined_missing.sort_index()
    
    def _merge_existing_and_new_data(self, existing_df: pd.DataFrame, new_df: pd.DataFrame, 
                                    start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Merge existing and new data, handling overlaps and gaps.
        
        Args:
            existing_df: Existing data DataFrame
            new_df: Newly fetched data DataFrame
            start_date: Requested start date
            end_date: Requested end date
            
        Returns:
            Merged DataFrame covering the full requested range
        """
        if existing_df.empty and new_df.empty:
            return pd.DataFrame()
        
        if existing_df.empty:
            return new_df
        
        if new_df.empty:
            return existing_df
        
        # Combine existing and new data
        combined = pd.concat([existing_df, new_df])
        
        # Remove duplicates (keep first occurrence)
        combined = combined[~combined.index.duplicated(keep='first')]
        
        # Sort by index
        combined = combined.sort_index()
        
        # Filter to requested date range
        combined = combined[(combined.index >= start_date) & (combined.index <= end_date)]
        
        return combined
    
    def fetch_data(self, provider: str, symbol: str, start_date: datetime, 
                   end_date: datetime, interval: str = '1d', 
                   force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch data from a provider and save to raw directory.
        
        This method now intelligently checks for existing data and only downloads
        what's missing, merging with existing data when possible.
        
        Args:
            provider: Data provider name ('binance', 'yahoo', 'ib')
            symbol: Trading symbol
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval
            force_refresh: Whether to force refresh existing data
            
        Returns:
            DataFrame with fetched data (OHLCV columns)
        """
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Get file paths
        raw_file, clean_file = self._get_data_file_paths(provider, symbol, start_date, end_date, interval)
        
        # If force refresh, delete existing files and fetch everything
        if force_refresh:
            if raw_file.exists():
                raw_file.unlink()
                logger.info(f"Deleted existing raw data for force refresh: {raw_file}")
            if clean_file.exists():
                clean_file.unlink()
                logger.info(f"Deleted existing clean data for force refresh: {clean_file}")
        
        # Check if we have existing data
        existing_data = pd.DataFrame()
        if raw_file.exists() and not force_refresh:
            try:
                existing_data = pd.read_parquet(raw_file)
                logger.info(f"Found existing raw data: {raw_file}")
            except Exception as e:
                logger.warning(f"Failed to read existing raw data: {e}")
                existing_data = pd.DataFrame()
        
        # Check data completeness
        completeness = self._check_data_completeness(existing_data, start_date, end_date, interval)
        
        if completeness['is_complete']:
            logger.info(f"Data for {symbol} is already complete (coverage: {completeness['coverage_percentage']:.1f}%)")
            return existing_data
        
        logger.info(f"Data for {symbol} is {completeness['coverage_percentage']:.1f}% complete")
        
        # Fetch missing data
        missing_data = self._fetch_missing_data(provider, symbol, completeness['missing_ranges'], interval)
        
        # Merge existing and new data
        final_data = self._merge_existing_and_new_data(existing_data, missing_data, start_date, end_date)
        
        if final_data.empty:
            raise RuntimeError(f"Failed to obtain any data for {symbol}")
        
        # Save the merged data
        final_data.to_parquet(raw_file)
        logger.info(f"Updated raw data saved to {raw_file}")
        
        return final_data
    
    def process_data(self, provider: str, symbol: str, start_date: datetime, 
                    end_date: datetime, interval: str = '1d') -> pd.DataFrame:
        """
        Process raw data and save to clean directory.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Cleaned DataFrame
        """
        asset_type = self.asset_type_map[provider]
        
        # Load raw data
        raw_file = self.raw_path / asset_type / f"{symbol}_{interval}.parquet"
        
        if not raw_file.exists():
            raise FileNotFoundError(f"Raw data file not found: {raw_file}")
        
        raw_data = pd.read_parquet(raw_file)
        
        # Clean data
        clean_data = DataProcessor.clean_data(raw_data, asset_type)
        
        # Save clean data
        clean_file = self.clean_path / asset_type / f"{symbol}_{interval}.parquet"
        clean_data.to_parquet(clean_file)
        
        logger.info(f"Clean data saved to {clean_file}")
        return clean_data
    
    def get_data(self, provider: str, symbols: Union[str, List[str]], 
                 start_date: datetime, end_date: datetime, 
                 interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        Get data ready for backtesting.
        
        This method handles both single and multiple assets, ensuring data is fetched 
        and processed, then returns the clean data suitable for the Backtester.
        
        Args:
            provider: Data provider name ('binance', 'yahoo', 'ib')
            symbols: Single symbol string or list of symbols
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval ('1d', '1h', etc.)
            
        Returns:
            Dictionary mapping symbol to DataFrame ready for backtesting
        """
        # Convert single symbol to list for uniform processing
        if isinstance(symbols, str):
            symbols = [symbols]
        
        if not isinstance(symbols, list) or len(symbols) == 0:
            raise ValueError("symbols must be a non-empty string or list of strings")
        
        data_dict = {}
        
        for symbol in symbols:
            try:
                asset_type = self.asset_type_map[provider]
                clean_file = self.clean_path / asset_type / f"{symbol}_{interval}.parquet"
                
                if not clean_file.exists():
                    # Fetch and process data if not available
                    self.fetch_data(provider, symbol, start_date, end_date, interval)
                    self.process_data(provider, symbol, start_date, end_date, interval)
                
                # Load the data
                data = pd.read_parquet(clean_file)
                
                # Ensure we have the expected OHLCV columns
                expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in expected_columns:
                    if col not in data.columns:
                        logger.warning(f"Missing expected column {col} for {symbol}")
                
                data_dict[symbol] = data
                logger.info(f"Successfully loaded data for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {e}")
                continue
        
        if not data_dict:
            raise RuntimeError("Failed to load data for any symbols")
        
        return data_dict
    
    def list_available_data(self, asset_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all available data files.
        
        Args:
            asset_type: Filter by asset type (None for all)
            
        Returns:
            Dictionary mapping asset types to available symbols
        """
        result = {}
        
        if asset_type:
            asset_types = [asset_type]
        else:
            asset_types = [d.name for d in self.clean_path.iterdir() if d.is_dir()]
        
        for at in asset_types:
            clean_dir = self.clean_path / at
            if clean_dir.exists():
                files = [f.stem for f in clean_dir.glob("*.parquet")]
                result[at] = files
        
        return result
    
    def list_assets_with_ranges(self, asset_type: Optional[str] = None, 
                               provider: Optional[str] = None, 
                               interval: str = '1d') -> Dict[str, List[dict]]:
        """
        List all available assets with their data ranges and details.
        
        Args:
            asset_type: Filter by asset type (None for all)
            provider: Filter by provider (None for all)
            interval: Data interval to check
            
        Returns:
            Dictionary mapping asset types to list of asset details
        """
        result = {}
        
        if asset_type:
            asset_types = [asset_type]
        else:
            asset_types = [d.name for d in self.clean_path.iterdir() if d.is_dir()]
        
        for at in asset_types:
            clean_dir = self.clean_path / at
            if clean_dir.exists():
                assets = []
                for file_path in clean_dir.glob("*.parquet"):
                    # Extract symbol and interval from filename
                    filename = file_path.stem
                    if '_' in filename:
                        parts = filename.split('_')
                        if len(parts) >= 2:
                            symbol = parts[0]
                            file_interval = parts[1]
                            
                            # Only include assets with matching interval
                            if file_interval == interval:
                                # Get data range for this asset
                                if provider:
                                    # Use specific provider
                                    asset_info = self.get_asset_data_range(provider, symbol, interval)
                                else:
                                    # Try to determine provider from asset type
                                    if at == 'Crypto':
                                        asset_info = self.get_asset_data_range('binance', symbol, interval)
                                    elif at == 'Equities':
                                        asset_info = self.get_asset_data_range('yahoo', symbol, interval)
                                    else:
                                        # Default to yahoo for other types
                                        asset_info = self.get_asset_data_range('yahoo', symbol, interval)
                                
                                assets.append(asset_info)
                
                if assets:
                    result[at] = assets
        
        return result
    
    def delete_data(self, provider: str, symbol: str, start_date: datetime, 
                   end_date: datetime, interval: str = '1d') -> None:
        """
        Delete data files for a specific symbol and period.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
        """
        asset_type = self.asset_type_map[provider]
        
        # Delete raw data
        raw_file = self.raw_path / asset_type / f"{symbol}_{interval}.parquet"
        if raw_file.exists():
            raw_file.unlink()
            logger.info(f"Deleted raw data: {raw_file}")
        
        # Delete clean data
        clean_file = self.clean_path / asset_type / f"{symbol}_{interval}.parquet"
        if clean_file.exists():
            clean_file.unlink()
            logger.info(f"Deleted clean data: {clean_file}")
    
    def get_data_info(self, provider: str, symbol: str, start_date: datetime, 
                     end_date: datetime, interval: str = '1d') -> dict:
        """
        Get information about data availability and completeness.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Dictionary with data information
        """
        raw_file, clean_file = self._get_data_file_paths(provider, symbol, start_date, end_date, interval)
        
        info = {
            'symbol': symbol,
            'provider': provider,
            'interval': interval,
            'requested_start': start_date,
            'requested_end': end_date,
            'raw_file_exists': raw_file.exists(),
            'clean_file_exists': clean_file.exists(),
            'raw_file_size': None,
            'clean_file_size': None,
            'data_completeness': None,
            'last_updated': None
        }
        
        # Get file sizes
        if raw_file.exists():
            info['raw_file_size'] = raw_file.stat().st_size
            info['last_updated'] = datetime.fromtimestamp(raw_file.stat().st_mtime)
        
        if clean_file.exists():
            info['clean_file_size'] = clean_file.stat().st_size
        
        # Check data completeness if raw file exists
        if raw_file.exists():
            try:
                existing_data = pd.read_parquet(raw_file)
                completeness = self._check_data_completeness(existing_data, start_date, end_date, interval)
                info['data_completeness'] = completeness
            except Exception as e:
                logger.warning(f"Failed to check data completeness: {e}")
                info['data_completeness'] = {'error': str(e)}
        
        return info
    
    def validate_data_integrity(self, provider: str, symbol: str, start_date: datetime, 
                               end_date: datetime, interval: str = '1d') -> dict:
        """
        Validate the integrity of stored data.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Dictionary with validation results
        """
        raw_file, clean_file = self._get_data_file_paths(provider, symbol, start_date, end_date, interval)
        
        validation = {
            'symbol': symbol,
            'provider': provider,
            'interval': interval,
            'raw_data_valid': False,
            'clean_data_valid': False,
            'raw_data_issues': [],
            'clean_data_issues': [],
            'data_continuity': False,
            'date_range_coverage': 0.0
        }
        
        # Validate raw data
        if raw_file.exists():
            try:
                raw_data = pd.read_parquet(raw_file)
                validation['raw_data_valid'] = True
                
                # Check for expected columns
                expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                missing_columns = [col for col in expected_columns if col not in raw_data.columns]
                if missing_columns:
                    validation['raw_data_issues'].append(f"Missing columns: {missing_columns}")
                
                # Check for data continuity
                if not raw_data.empty:
                    date_range = (raw_data.index.max() - raw_data.index.min()).days
                    requested_range = (end_date - start_date).days
                    validation['date_range_coverage'] = min(100.0, (date_range / requested_range) * 100)
                    
                    # Check for gaps in data (more than 2 days missing for daily data)
                    if interval == '1d':
                        expected_dates = pd.date_range(start=raw_data.index.min(), end=raw_data.index.max(), freq='D')
                        missing_dates = expected_dates.difference(raw_data.index)
                        if len(missing_dates) > 2:
                            validation['raw_data_issues'].append(f"Data gaps detected: {len(missing_dates)} missing dates")
                        else:
                            validation['data_continuity'] = True
                
            except Exception as e:
                validation['raw_data_issues'].append(f"Failed to read raw data: {e}")
        
        # Validate clean data
        if clean_file.exists():
            try:
                clean_data = pd.read_parquet(clean_file)
                validation['clean_data_valid'] = True
                
                # Check for data quality issues
                if not clean_data.empty:
                    # Check for negative prices
                    price_columns = ['Open', 'High', 'Low', 'Close']
                    for col in price_columns:
                        if col in clean_data.columns and (clean_data[col] < 0).any():
                            validation['clean_data_issues'].append(f"Negative prices in {col}")
                    
                    # Check for zero prices
                    for col in price_columns:
                        if col in clean_data.columns and (clean_data[col] == 0).any():
                            validation['clean_data_issues'].append(f"Zero prices in {col}")
                    
                    # Check for extreme price movements
                    if 'Close' in clean_data.columns:
                        returns = clean_data['Close'].pct_change()
                        extreme_moves = (returns.abs() > 10).sum()
                        if extreme_moves > 0:
                            validation['clean_data_issues'].append(f"Extreme price movements: {extreme_moves} instances")
                
            except Exception as e:
                validation['clean_data_issues'].append(f"Failed to read clean data: {e}")
        
        return validation
    
    def repair_data(self, provider: str, symbol: str, start_date: datetime, 
                   end_date: datetime, interval: str = '1d') -> bool:
        """
        Attempt to repair corrupted or incomplete data.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            True if repair was successful, False otherwise
        """
        try:
            logger.info(f"Attempting to repair data for {symbol}")
            
            # Force refresh to get clean data
            self.fetch_data(provider, symbol, start_date, end_date, interval, force_refresh=True)
            
            # Reprocess the data
            self.process_data(provider, symbol, start_date, end_date, interval)
            
            # Validate the repaired data
            validation = self.validate_data_integrity(provider, symbol, start_date, end_date, interval)
            
            if validation['raw_data_valid'] and validation['clean_data_valid']:
                logger.info(f"Successfully repaired data for {symbol}")
                return True
            else:
                logger.error(f"Data repair failed for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to repair data for {symbol}: {e}")
            return False
    
    def get_data_statistics(self, provider: str, symbol: str, start_date: datetime, 
                           end_date: datetime, interval: str = '1d') -> dict:
        """
        Get statistical information about the data.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Dictionary with statistical information
        """
        try:
            # Get the data
            data = self.get_data(provider, [symbol], start_date, end_date, interval)
            df = data[symbol]
            
            if df.empty:
                return {'error': 'No data available'}
            
            # Calculate basic statistics
            stats = {
                'symbol': symbol,
                'provider': provider,
                'interval': interval,
                'data_points': len(df),
                'date_range': {
                    'start': df.index.min().strftime('%Y-%m-%d'),
                    'end': df.index.max().strftime('%Y-%m-%d'),
                    'days': (df.index.max() - df.index.min()).days
                },
                'price_statistics': {},
                'volume_statistics': {},
                'returns_statistics': {}
            }
            
            # Price statistics
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df.columns:
                    stats['price_statistics'][col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'last': float(df[col].iloc[-1])
                    }
            
            # Volume statistics
            if 'Volume' in df.columns:
                stats['volume_statistics'] = {
                    'total': float(df['Volume'].sum()),
                    'mean': float(df['Volume'].mean()),
                    'max': float(df['Volume'].max()),
                    'min': float(df['Volume'].min())
                }
            
            # Returns statistics
            if 'Close' in df.columns:
                returns = df['Close'].pct_change().dropna()
                stats['returns_statistics'] = {
                    'mean_return': float(returns.mean()),
                    'volatility': float(returns.std()),
                    'min_return': float(returns.min()),
                    'max_return': float(returns.max()),
                    'positive_days': int((returns > 0).sum()),
                    'negative_days': int((returns < 0).sum())
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics for {symbol}: {e}")
            return {'error': str(e)}
    
    def get_asset_data_range(self, provider: str, symbol: str, interval: str = '1d') -> dict:
        """
        Get the full date range of data available for an asset.
        
        Args:
            provider: Data provider name
            symbol: Trading symbol
            interval: Data interval
            
        Returns:
            Dictionary with data range information
        """
        raw_file, _ = self._get_data_file_paths(provider, symbol, datetime.now(), datetime.now(), interval)
        
        if not raw_file.exists():
            return {
                'symbol': symbol,
                'provider': provider,
                'interval': interval,
                'has_data': False,
                'data_range': None,
                'data_points': 0,
                'file_size': None,
                'last_updated': None
            }
        
        try:
            # Load the data to get the actual range
            df = pd.read_parquet(raw_file)
            
            if df.empty:
                return {
                    'symbol': symbol,
                    'provider': provider,
                    'interval': interval,
                    'has_data': False,
                    'data_range': None,
                    'data_points': 0,
                    'file_size': raw_file.stat().st_size,
                    'last_updated': datetime.fromtimestamp(raw_file.stat().st_mtime)
                }
            
            # Get the actual date range
            actual_start = df.index.min()
            actual_end = df.index.max()
            
            # Convert to datetime if needed
            if isinstance(actual_start, pd.Timestamp):
                actual_start = actual_start.to_pydatetime()
            if isinstance(actual_end, pd.Timestamp):
                actual_end = actual_end.to_pydatetime()
            
            return {
                'symbol': symbol,
                'provider': provider,
                'interval': interval,
                'has_data': True,
                'data_range': {
                    'start': actual_start.strftime('%Y-%m-%d'),
                    'end': actual_end.strftime('%Y-%m-%d'),
                    'start_dt': actual_start,
                    'end_dt': actual_end,
                    'days': (actual_end - actual_start).days
                },
                'data_points': len(df),
                'file_size': raw_file.stat().st_size,
                'last_updated': datetime.fromtimestamp(raw_file.stat().st_mtime)
            }
            
        except Exception as e:
            logger.error(f"Failed to get data range for {symbol}: {e}")
            return {
                'symbol': symbol,
                'provider': provider,
                'interval': interval,
                'has_data': False,
                'data_range': None,
                'data_points': 0,
                'file_size': raw_file.stat().st_size if raw_file.exists() else None,
                'last_updated': datetime.fromtimestamp(raw_file.stat().st_mtime) if raw_file.exists() else None,
                'error': str(e)
            }

# =========================
# Utility Functions
# =========================
def get_data_manager(base_path: str = "data") -> DataManager:
    """
    Convenience function to get a DataManager instance.
    
    Args:
        base_path: Base path for data storage
        
    Returns:
        DataManager instance
    """
    return DataManager(base_path)

def quick_fetch(provider: str, symbols: Union[str, List[str]], days: int = 365, 
                interval: str = '1d', base_path: str = "data") -> Dict[str, pd.DataFrame]:
    """
    Quick function to fetch and process data.
    
    Args:
        provider: Data provider name
        symbols: Single symbol string or list of symbols
        days: Number of days to fetch
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary mapping symbol to DataFrame ready for backtesting
    """
    dm = get_data_manager(base_path)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return dm.get_data(provider, symbols, start_date, end_date, interval)

def check_data_availability(provider: str, symbols: Union[str, List[str]], 
                           start_date: datetime, end_date: datetime, 
                           interval: str = '1d', base_path: str = "data") -> dict:
    """
    Check data availability for multiple symbols.
    
    Args:
        provider: Data provider name
        symbols: Single symbol string or list of symbols
        start_date: Start date
        end_date: End date
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary with availability information for each symbol
    """
    dm = get_data_manager(base_path)
    
    if isinstance(symbols, str):
        symbols = [symbols]
    
    availability = {}
    for symbol in symbols:
        try:
            info = dm.get_data_info(provider, symbol, start_date, end_date, interval)
            availability[symbol] = info
        except Exception as e:
            availability[symbol] = {'error': str(e)}
    
    return availability

def validate_all_data(provider: str, symbols: Union[str, List[str]], 
                     start_date: datetime, end_date: datetime, 
                     interval: str = '1d', base_path: str = "data") -> dict:
    """
    Validate data integrity for multiple symbols.
    
    Args:
        provider: Data provider name
        symbols: Single symbol string or list of symbols
        start_date: Start date
        end_date: End date
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary with validation results for each symbol
    """
    dm = get_data_manager(base_path)
    
    if isinstance(symbols, str):
        symbols = [symbols]
    
    validation_results = {}
    for symbol in symbols:
        try:
            validation = dm.validate_data_integrity(provider, symbol, start_date, end_date, interval)
            validation_results[symbol] = validation
        except Exception as e:
            validation_results[symbol] = {'error': str(e)}
    
    return validation_results

def repair_all_data(provider: str, symbols: Union[str, List[str]], 
                   start_date: datetime, end_date: datetime, 
                   interval: str = '1d', base_path: str = "data") -> dict:
    """
    Attempt to repair data for multiple symbols.
    
    Args:
        provider: Data provider name
        symbols: Single symbol string or list of symbols
        start_date: Start date
        end_date: End date
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary with repair results for each symbol
    """
    dm = get_data_manager(base_path)
    
    if isinstance(symbols, str):
        symbols = [symbols]
    
    repair_results = {}
    for symbol in symbols:
        try:
            success = dm.repair_data(provider, symbol, start_date, end_date, interval)
            repair_results[symbol] = {'success': success}
        except Exception as e:
            repair_results[symbol] = {'success': False, 'error': str(e)}
    
    return repair_results

def get_all_asset_ranges(base_path: str = "data", asset_type: Optional[str] = None, 
                         provider: Optional[str] = None, interval: str = '1d') -> dict:
    """
    Get data ranges for all available assets.
    
    Args:
        base_path: Base path for data storage
        asset_type: Filter by asset type (None for all)
        provider: Filter by provider (None for all)
        interval: Data interval to check
        
    Returns:
        Dictionary with asset information organized by asset type
    """
    dm = get_data_manager(base_path)
    return dm.list_assets_with_ranges(asset_type, provider, interval)

def check_asset_data_needs(symbol: str, start_date: datetime, end_date: datetime, 
                          provider: str, interval: str = '1d', base_path: str = "data") -> dict:
    """
    Check what data is needed for a specific asset and date range.
    
    Args:
        symbol: Trading symbol
        start_date: Start date needed
        end_date: End date needed
        provider: Data provider name
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary with data needs analysis
    """
    dm = get_data_manager(base_path)
    
    # Get current asset data range
    asset_range = dm.get_asset_data_range(provider, symbol, interval)
    
    if not asset_range['has_data']:
        return {
            'symbol': symbol,
            'provider': provider,
            'interval': interval,
            'needs_download': True,
            'download_reason': 'No existing data',
            'missing_range': [(start_date, end_date)],
            'missing_days': (end_date - start_date).days,
            'existing_data': None
        }
    
    # Check if we have the data we need
    existing_start = asset_range['data_range']['start_dt']
    existing_end = asset_range['data_range']['end_dt']
    
    # Determine what's missing
    missing_ranges = []
    total_missing_days = 0
    
    if start_date < existing_start:
        missing_ranges.append((start_date, existing_start))
        total_missing_days += (existing_start - start_date).days
    
    if end_date > existing_end:
        missing_ranges.append((existing_end, end_date))
        total_missing_days += (end_date - existing_end).days
    
    if not missing_ranges:
        return {
            'symbol': symbol,
            'provider': provider,
            'interval': interval,
            'needs_download': False,
            'download_reason': 'Data already complete',
            'missing_range': None,
            'missing_days': 0,
            'existing_data': asset_range
        }
    
    return {
        'symbol': symbol,
        'provider': provider,
        'interval': interval,
        'needs_download': True,
        'download_reason': f'Missing {total_missing_days} days of data',
        'missing_range': missing_ranges,
        'missing_days': total_missing_days,
        'existing_data': asset_range
    }

def smart_fetch_data(provider: str, symbols: Union[str, List[str]], 
                    start_date: datetime, end_date: datetime, 
                    interval: str = '1d', base_path: str = "data") -> Dict[str, pd.DataFrame]:
    """
    Smart data fetching that only downloads what's missing.
    
    Args:
        provider: Data provider name
        symbols: Single symbol string or list of symbols
        start_date: Start date needed
        end_date: End date needed
        interval: Data interval
        base_path: Base path for data storage
        
    Returns:
        Dictionary mapping symbol to DataFrame ready for backtesting
    """
    dm = get_data_manager(base_path)
    
    if isinstance(symbols, str):
        symbols = [symbols]
    
    # Check what each symbol needs
    needs_analysis = {}
    for symbol in symbols:
        needs = check_asset_data_needs(symbol, start_date, end_date, provider, interval, base_path)
        needs_analysis[symbol] = needs
        
        if needs['needs_download']:
            print(f"{symbol}: {needs['download_reason']}")
            if needs['missing_range']:
                for start, end in needs['missing_range']:
                    print(f"  Missing: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        else:
            print(f"{symbol}: Data already complete")
    
    # Fetch data (this will automatically handle missing parts)
    return dm.get_data(provider, symbols, start_date, end_date, interval)
