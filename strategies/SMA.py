import pandas as pd
import numpy as np
from src.Backtester import Strategy
import matplotlib.pyplot as plt

class SMAStrategy(Strategy):
    """
    Modified SMA Strategy with Z-score signal and Gaussian derivative position function
    
    This strategy:
    - Uses Z_ma = (long_ma - short_ma) / std(long_ma - short_ma) as signal
    - Positions are g(Z_ma) where g() is the first derivative of a Gaussian
    - Scaled so that maximum positions are 2.0
    """

    def __init__(self, data: dict, params: dict = None):
        """
        Initialize the modified SMA strategy.
        
        Args:
            data: Dictionary mapping asset names to DataFrames with OHLCV data
            short_window: Short moving average window
            long_window: Long moving average window
            order_size: Position size scaling factor
            init_cash: Initial capital
            risk_free_rate: Risk-free rate for calculations
            params: Additional parameters (optional)
        """
        # Set parameters
        self.short_window = params.get('short_window', 20)
        self.long_window = params.get('long_window', 50)
        self.order_size = params.get('order_size', 1.0)
        
        # Call parent constructor
        super().__init__(data, params)
        
        # Validate parameters
        if self.short_window >= self.long_window:
            raise ValueError("short_window must be less than long_window")
        if self.order_size <= 0:
            raise ValueError("order_size must be positive")

    def gaussian_derivative(self, x, sigma=1.0):
        """
        First derivative of a Gaussian function.
        
        Args:
            x: Input value
            sigma: Standard deviation of the Gaussian
            
        Returns:
            Scaled first derivative of Gaussian
        """
        # First derivative of Gaussian: -x * exp(-x^2/(2*sigma^2)) / sigma^2
        derivative = -x * np.exp(-x**2 / (2 * sigma**2)) / (sigma**2)
        
        # Scale so that maximum absolute value is 2.0
        # The maximum of |g'(x)| occurs at x = ±sigma
        max_derivative = np.exp(-0.5) / sigma  # Maximum absolute value
        scaled_derivative = (2.0 / max_derivative) * derivative
        
        return scaled_derivative

    def generate_signals(self):
        """Generate Z_ma signals for position calculation."""
        print("Generating Z_ma signals...")
        
        # Initialize signals as a dictionary
        self.signals = {}
        
        # Generate Z_ma signals for each asset
        for asset in self.assets:
            asset_data = self.data[asset]
            print(f"Processing {asset} with {len(asset_data)} data points")
            
            # Create DataFrame for this asset's signals
            asset_signals = pd.DataFrame(index=asset_data.index)
            
            # Calculate moving averages
            short_ma = asset_data['Close'].rolling(window=self.short_window, min_periods=self.short_window).mean()
            long_ma = asset_data['Close'].rolling(window=self.long_window, min_periods=self.long_window).mean()
            
            # Calculate the difference between MAs
            ma_diff = long_ma - short_ma
            
            # Calculate rolling standard deviation of the MA difference
            # Use a window that's reasonable for volatility estimation
            vol_window = min(60, len(asset_data) // 4)  # Use 60 days or 1/4 of data, whichever is smaller
            ma_diff_std = ma_diff.rolling(window=vol_window, min_periods=vol_window).std()
            
            # Calculate Z_ma = (long_ma - short_ma) / std(long_ma - short_ma)
            z_ma = ma_diff / ma_diff_std
            
            # Store signals
            asset_signals['z_ma'] = z_ma
            
            # Store in signals dictionary
            self.signals[asset] = asset_signals
        
        print(f"Generated Z_ma signals for {len(self.assets)} assets")
        return self.signals

    def generate_positions(self):
        """Convert Z_ma signals to position sizes using Gaussian derivative function."""
        print("Generating positions using Gaussian derivative...")
        
        if self.signals is None:
            self.generate_signals()
        
        # Initialize positions DataFrame
        self.positions = pd.DataFrame(0, index=self.unified_index, columns=self.assets)
        
        # Generate positions for each asset
        for asset in self.assets:
            asset_signals = self.signals[asset]
            
            # Loop through each timestamp
            for timestamp in asset_signals.index:
                # Get Z_ma value
                z_ma = asset_signals.loc[timestamp, 'z_ma']
                
                # Skip if we don't have enough data for Z_ma
                if pd.isna(z_ma):
                    continue
                
                # Calculate position using Gaussian derivative: g(Z_ma)
                # The sign convention: positive Z_ma (long MA > short MA) -> long position
                # Negative Z_ma (long MA < short MA) -> short position
                gauss_der = self.gaussian_derivative(z_ma, sigma=2.0)
                position = gauss_der if np.abs(gauss_der) > 0.5 else 0.0

                # Apply order size scaling
                scaled_position = position * self.order_size
                
                # Set position for this timestamp (if timestamp exists in unified index)
                if timestamp in self.unified_index:
                    self.positions.loc[timestamp, asset] = scaled_position
        
        print(f"Generated positions for {len(self.assets)} assets")
        return self.positions