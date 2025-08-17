import pandas as pd
import numpy as np
from src.Backtester import Strategy
import matplotlib.pyplot as plt

class SMAStrategy(Strategy):
    """
    Simple Moving Average Crossover Strategy
    
    This strategy:
    - Goes LONG when short MA crosses above long MA
    - Goes SHORT when short MA crosses below long MA
    - Uses stop-loss and take-profit for risk management
    """

    def __init__(self, data: dict, short_window: int = 20, long_window: int = 50, 
                 order_size: float = 1.0, init_cash: float = 100_000.0, 
                 risk_free_rate: float = 0.0, params: dict = None):
        """
        Initialize the SMA strategy.
        
        Args:
            data: Dictionary mapping asset names to DataFrames with OHLCV data
            short_window: Short moving average window
            long_window: Long moving average window
            order_size: Position size (1.0 = 100% of portfolio)
            init_cash: Initial capital
            risk_free_rate: Risk-free rate for calculations
            params: Additional parameters (optional)
        """
        # Set parameters
        self.short_window = short_window
        self.long_window = long_window
        self.order_size = order_size
        
        # Call parent constructor
        super().__init__(data, init_cash, risk_free_rate, params)
        
        # Validate parameters
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be less than long_window")
        if self.order_size <= 0:
            raise ValueError("order_size must be positive")

    def generate_signals(self):
        """Generate SMA values for signal calculation."""
        print("Generating SMA signals...")
        
        # Initialize signals as a dictionary
        self.signals = {}
        
        # Generate SMA values for each asset
        for asset in self.assets:
            asset_data = self.data[asset]
            print(f"Processing {asset} with {len(asset_data)} data points")
            
            # Create DataFrame for this asset's SMA values
            asset_signals = pd.DataFrame(index=asset_data.index)
            
            # Calculate moving averages
            asset_signals['short_ma'] = asset_data['Close'].rolling(window=self.short_window, min_periods=self.short_window).mean()
            asset_signals['long_ma'] = asset_data['Close'].rolling(window=self.long_window, min_periods=self.long_window).mean()
            
            # Store in signals dictionary
            self.signals[asset] = asset_signals
        
        print(f"Generated SMA values for {len(self.assets)} assets")
        return self.signals

    def generate_positions(self):
        """Convert SMA values to position sizes using crossover logic."""
        print("Generating positions...")
        
        if self.signals is None:
            self.generate_signals()
        
        # Initialize positions DataFrame
        self.positions = pd.DataFrame(0, index=self.unified_index, columns=self.assets)
        
        # Generate positions for each asset
        for asset in self.assets:
            asset_signals = self.signals[asset]
            
            # Initialize position tracking
            current_position = 0
            
            # Loop through each timestamp
            for timestamp in asset_signals.index:
                # Get current and previous MA values
                short_ma = asset_signals.loc[timestamp, 'short_ma']
                long_ma = asset_signals.loc[timestamp, 'long_ma']
                
                # Skip if we don't have enough data for both MAs
                if pd.isna(short_ma) or pd.isna(long_ma):
                    continue
                
                # Get previous values for crossover detection
                if timestamp > asset_signals.index[0]:
                    prev_timestamp = asset_signals.index[asset_signals.index.get_loc(timestamp) - 1]
                    prev_short_ma = asset_signals.loc[prev_timestamp, 'short_ma']
                    prev_long_ma = asset_signals.loc[prev_timestamp, 'long_ma']
                    
                    # Check if we have valid previous values
                    if not (pd.isna(prev_short_ma) or pd.isna(prev_long_ma)):
                        # Long signal: short MA crosses above long MA
                        if short_ma > long_ma and prev_short_ma <= prev_long_ma:
                            current_position = self.order_size
                        
                        # Short signal: short MA crosses below long MA
                        elif short_ma < long_ma and prev_short_ma >= prev_long_ma:
                            current_position = -self.order_size
                        
                        # Exit signal: when MA cross in opposite direction
                        elif (short_ma < long_ma and prev_short_ma >= prev_long_ma) or \
                             (short_ma > long_ma and prev_short_ma <= prev_long_ma):
                            current_position = 0
                
                # Set position for this timestamp (if timestamp exists in unified index)
                if timestamp in self.unified_index:
                    self.positions.loc[timestamp, asset] = current_position
        
        print(f"Generated positions for {len(self.assets)} assets")
        return self.positions