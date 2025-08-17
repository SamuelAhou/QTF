# API Reference

This document provides comprehensive API documentation for all major components of the QTF framework. Each function, class, and method is documented with examples and usage patterns.

## 📚 Table of Contents

- [DataProvider](#dataprovider)
- [Backtester](#backtester)
- [RiskManager](#riskmanager)
- [Strategy Interface](#strategy-interface)
- [Utility Functions](#utility-functions)

---

## DataProvider

The DataProvider module handles all data fetching, storage, and management operations.

### Core Functions

#### `get_data_manager(data_dir="data")`

Creates and returns a data manager instance for the specified directory.

**Parameters:**
- `data_dir` (str): Path to data directory (default: "data")

**Returns:**
- `DataManager`: Configured data manager instance

**Example:**
```python
from src.DataProvider import get_data_manager

# Get data manager for main data directory
dm = get_data_manager("data")

# Get data manager for test data
test_dm = get_data_manager("test_data")
```

#### `smart_fetch_data(provider, symbol, start_date, end_date, interval)`

Intelligently fetches data, only downloading missing portions and merging with existing data.

**Parameters:**
- `provider` (str): Data provider name (e.g., "yahoo", "binance", "alpha_vantage")
- `symbol` (str): Asset symbol (e.g., "AAPL", "BTCUSDT")
- `start_date` (datetime): Start date for data range
- `end_date` (datetime): End date for data range
- `interval` (str): Data interval (e.g., "1d", "1h", "1m")

**Returns:**
- `pandas.DataFrame`: OHLCV data for the specified symbol and date range

**Example:**
```python
from src.DataProvider import smart_fetch_data
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Fetch one year of daily data
data = smart_fetch_data("yahoo", "AAPL", start_date, end_date, "1d")
print(f"Downloaded {len(data)} data points")
```

#### `check_asset_data_needs(symbol, start_date, end_date, provider, interval)`

Analyzes what data is needed vs. what's already available.

**Parameters:**
- `symbol` (str): Asset symbol
- `start_date` (datetime): Start date
- `end_date` (datetime): End date
- `provider` (str): Data provider
- `interval` (str): Data interval

**Returns:**
- `dict`: Dictionary containing data needs analysis

**Example:**
```python
from src.DataProvider import check_asset_data_needs

needs = check_asset_data_needs("AAPL", start_date, end_date, "yahoo", "1d")

if needs['needs_download']:
    print(f"Missing {needs['missing_days']} days of data")
    for start, end in needs['missing_range']:
        print(f"  Missing: {start} to {end}")
else:
    print("Data already complete!")
```

### DataManager Class

#### `DataManager.get_data(provider, symbols, start_date, end_date, interval)`

Fetches data for multiple symbols from a specified provider.

**Parameters:**
- `provider` (str): Data provider name
- `symbols` (list): List of asset symbols
- `start_date` (datetime): Start date
- `end_date` (datetime): End date
- `interval` (str): Data interval

**Returns:**
- `dict`: Dictionary of DataFrames keyed by symbol

**Example:**
```python
dm = get_data_manager("data")

# Fetch data for multiple symbols
symbols = ["AAPL", "GOOGL", "MSFT"]
data = dm.get_data("yahoo", symbols, start_date, end_date, "1d")

# Access individual symbol data
aapl_data = data["AAPL"]
googl_data = data["GOOGL"]
```

#### `DataManager.get_asset_data_range(provider, symbol, interval)`

Gets information about available data for a specific asset.

**Parameters:**
- `provider` (str): Data provider name
- `symbol` (str): Asset symbol
- `interval` (str): Data interval

**Returns:**
- `dict`: Dictionary containing data range information

**Example:**
```python
asset_info = dm.get_asset_data_range("yahoo", "AAPL", "1d")

if asset_info['has_data']:
    data_range = asset_info['data_range']
    print(f"AAPL data: {data_range['start']} to {data_range['end']}")
    print(f"Total days: {data_range['days']}")
    print(f"Data points: {asset_info['data_points']}")
```

#### `DataManager.get_all_asset_ranges(provider, interval)`

Gets information about all assets for a specific provider and interval.

**Parameters:**
- `provider` (str): Data provider name
- `interval` (str): Data interval

**Returns:**
- `dict`: Dictionary of asset information keyed by symbol

**Example:**
```python
all_assets = dm.get_all_asset_ranges("yahoo", "1d")

for symbol, info in all_assets.items():
    if info['has_data']:
        print(f"{symbol}: {info['data_range']['days']} days")
```

---

## Backtester

The Backtester module handles strategy backtesting and performance analysis.

### Core Class

#### `Backtester(strategy, risk_manager=None, initial_capital=10000)`

Creates a backtester instance for running strategy backtests.

**Parameters:**
- `strategy`: Strategy instance implementing the strategy interface
- `risk_manager` (RiskManager, optional): Risk management instance
- `initial_capital` (float): Starting portfolio value (default: 10000)

**Example:**
```python
from src.Backtester import Backtester
from strategies.SMA import SMAStrategy

# Create strategy
strategy = SMAStrategy(short_window=20, long_window=100)

# Create backtester
backtester = Backtester(strategy=strategy, initial_capital=50000)

# Run backtest
results = backtester.run(data=data)
```

#### `Backtester.run(data, start_date=None, end_date=None)`

Runs the backtest using the provided data.

**Parameters:**
- `data` (dict): Dictionary of DataFrames keyed by symbol
- `start_date` (datetime, optional): Custom start date for backtest
- `end_date` (datetime, optional): Custom end date for backtest

**Returns:**
- `dict`: Comprehensive backtest results

**Example:**
```python
# Run backtest with custom date range
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=252)  # 1 year

results = backtester.run(
    data=data,
    start_date=start_date,
    end_date=end_date
)

# Access results
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### Backtest Results

The `run()` method returns a comprehensive results dictionary containing:

#### Performance Metrics
- `total_return` (float): Total return over the backtest period
- `annualized_return` (float): Annualized return rate
- `sharpe_ratio` (float): Risk-adjusted return metric
- `calmar_ratio` (float): Return to maximum drawdown ratio
- `win_rate` (float): Percentage of profitable trades

#### Risk Metrics
- `max_drawdown` (float): Maximum peak-to-trough decline
- `volatility` (float): Annualized volatility
- `var_95` (float): 95% Value at Risk
- `cvar_95` (float): 95% Conditional Value at Risk

#### Portfolio Metrics
- `initial_capital` (float): Starting portfolio value
- `final_value` (float): Final portfolio value
- `peak_value` (float): Highest portfolio value reached

#### Trading Metrics
- `trades` (list): List of completed trades
- `total_trades` (int): Total number of trades
- `profit_factor` (float): Gross profit to gross loss ratio

**Example:**
```python
results = backtester.run(data=data)

# Performance analysis
print("=== Performance Summary ===")
print(f"Initial Capital: ${results['initial_capital']:,.2f}")
print(f"Final Value: ${results['final_value']:,.2f}")
print(f"Total Return: {results['total_return']:.2%}")
print(f"Annualized Return: {results['annualized_return']:.2%}")

# Risk analysis
print("\n=== Risk Analysis ===")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
print(f"Volatility: {results['volatility']:.2%}")

# Trading analysis
print("\n=== Trading Summary ===")
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.1%}")
print(f"Profit Factor: {results['profit_factor']:.2f}")

# Individual trades
if 'trades' in results:
    print("\n=== Trade Details ===")
    for i, trade in enumerate(results['trades'][:5]):  # First 5 trades
        print(f"Trade {i+1}: {trade['entry_date']} to {trade['exit_date']}")
        print(f"  Symbol: {trade['symbol']}")
        print(f"  P&L: ${trade['pnl']:.2f}")
        print(f"  Return: {trade['return']:.2%}")
```

---

## RiskManager

The RiskManager class provides comprehensive risk management controls.

### Core Class

#### `RiskManager()`

Creates a risk manager instance with no risk controls by default.

**Example:**
```python
from src.Backtester import RiskManager

# Create empty risk manager (no controls)
risk_manager = RiskManager()

# Add specific risk controls as needed
risk_manager.add_sltp(stop_loss_pct=0.05, take_profit_pct=0.10)
```

### Risk Control Methods

#### `add_sltp(stop_loss_pct, take_profit_pct, re_entry_delay=0)`

Adds stop-loss and take-profit controls.

**Parameters:**
- `stop_loss_pct` (float): Stop-loss percentage (e.g., 0.05 for 5%)
- `take_profit_pct` (float): Take-profit percentage (e.g., 0.10 for 10%)
- `re_entry_delay` (int): Periods to wait before re-entering after stop-loss

**Example:**
```python
risk_manager = RiskManager()

# Add 5% stop-loss, 10% take-profit
risk_manager.add_sltp(
    stop_loss_pct=0.05,      # 5% stop-loss
    take_profit_pct=0.10,    # 10% take-profit
    re_entry_delay=3         # 3 periods delay
)
```

#### `add_position_limits(max_position_pct, max_portfolio_exposure)`

Adds position size and portfolio exposure limits.

**Parameters:**
- `max_position_pct` (float): Maximum percentage per individual position
- `max_portfolio_exposure` (float): Maximum total portfolio exposure

**Example:**
```python
risk_manager = RiskManager()

# Limit individual positions to 20% and total exposure to 80%
risk_manager.add_position_limits(
    max_position_pct=0.20,        # Max 20% per asset
    max_portfolio_exposure=0.80   # Max 80% total exposure
)
```

#### `add_var_limits(var_limit, confidence=0.95, lookback=252)`

Adds Value at Risk (VaR) limits.

**Parameters:**
- `var_limit` (float): Maximum daily VaR (e.g., 0.02 for 2%)
- `confidence` (float): Confidence level (default: 0.95)
- `lookback` (int): Lookback period for VaR calculation (default: 252)

**Example:**
```python
risk_manager = RiskManager()

# Limit daily VaR to 1.5% with 95% confidence
risk_manager.add_var_limits(
    var_limit=0.015,         # 1.5% daily VaR
    confidence=0.95,         # 95% confidence
    lookback=252             # 1 year lookback
)
```

#### `add_correlation_limits(max_correlation, lookback=60)`

Adds correlation limits between assets.

**Parameters:**
- `max_correlation` (float): Maximum allowed correlation (e.g., 0.7 for 70%)
- `lookback` (int): Lookback period for correlation calculation (default: 60)

**Example:**
```python
risk_manager = RiskManager()

# Limit correlation between assets to 60%
risk_manager.add_correlation_limits(
    max_correlation=0.6,     # Max 60% correlation
    lookback=60              # 60 days lookback
)
```

#### `add_sector_limits(max_sector_exposure)`

Adds sector exposure limits.

**Parameters:**
- `max_sector_exposure` (float): Maximum exposure per sector (e.g., 0.4 for 40%)

**Example:**
```python
risk_manager = RiskManager()

# Limit sector exposure to 35%
risk_manager.add_sector_limits(max_sector_exposure=0.35)
```

#### `add_volatility_targeting(target_volatility, lookback=60, use_dynamic_sizing=True)`

Adds volatility targeting controls.

**Parameters:**
- `target_volatility` (float): Target annual volatility (e.g., 0.15 for 15%)
- `lookback` (int): Lookback period for volatility calculation (default: 60)
- `use_dynamic_sizing` (bool): Enable dynamic position sizing (default: True)

**Example:**
```python
risk_manager = RiskManager()

# Target 12% annual volatility with dynamic sizing
risk_manager.add_volatility_targeting(
    target_volatility=0.12,   # 12% annual volatility target
    lookback=60,              # 60 days lookback
    use_dynamic_sizing=True   # Enable dynamic sizing
)
```

#### `add_drawdown_protection(max_drawdown, recovery_threshold=0.5)`

Adds drawdown protection controls.

**Parameters:**
- `max_drawdown` (float): Maximum allowed drawdown (e.g., 0.25 for 25%)
- `recovery_threshold` (float): Recovery threshold to resume trading (default: 0.5)

**Example:**
```python
risk_manager = RiskManager()

# Stop trading at 25% drawdown, resume at 12.5% recovery
risk_manager.add_drawdown_protection(
    max_drawdown=0.25,        # 25% max drawdown
    recovery_threshold=0.5     # Resume at 50% recovery (12.5%)
)
```

### Complete Risk Management Example

```python
from src.Backtester import RiskManager, Backtester
from strategies.SMA import SMAStrategy

# Create comprehensive risk manager
risk_manager = RiskManager()

# Basic risk controls
risk_manager.add_sltp(
    stop_loss_pct=0.05,      # 5% stop-loss
    take_profit_pct=0.10,    # 10% take-profit
    re_entry_delay=3         # 3 periods delay
)

# Position and portfolio limits
risk_manager.add_position_limits(
    max_position_pct=0.25,        # Max 25% per asset
    max_portfolio_exposure=0.70   # Max 70% total exposure
)

# Advanced risk controls
risk_manager.add_var_limits(
    var_limit=0.015,         # 1.5% daily VaR
    confidence=0.95,         # 95% confidence
    lookback=252             # 1 year lookback
)

risk_manager.add_correlation_limits(
    max_correlation=0.6,     # Max 60% correlation
    lookback=60              # 60 days lookback
)

risk_manager.add_volatility_targeting(
    target_volatility=0.12,   # 12% annual volatility target
    lookback=60,              # 60 days lookback
    use_dynamic_sizing=True   # Enable dynamic sizing
)

# Create backtester with risk management
strategy = SMAStrategy(short_window=20, long_window=100)
backtester = Backtester(strategy=strategy, risk_manager=risk_manager)

# Run backtest with comprehensive risk controls
results = backtester.run(data=data)
```

---

## Strategy Interface

All strategies in QTF must implement a specific interface.

### Required Methods

#### `generate_signals(data)`

Generates trading signals from market data.

**Parameters:**
- `data` (dict): Dictionary of DataFrames keyed by symbol

**Returns:**
- `dict`: Dictionary of signals keyed by symbol
  - `1`: Buy signal
  - `0`: Hold/no signal
  - `-1`: Sell signal

**Example:**
```python
def generate_signals(self, data):
    signals = {}
    
    for symbol, df in data.items():
        # Your signal logic here
        if self._is_bullish(df):
            signals[symbol] = 1
        elif self._is_bearish(df):
            signals[symbol] = -1
        else:
            signals[symbol] = 0
    
    return signals
```

#### `calculate_position_sizes(signals, data, portfolio_value)`

Calculates position sizes based on signals and portfolio value.

**Parameters:**
- `signals` (dict): Trading signals from `generate_signals()`
- `data` (dict): Market data
- `portfolio_value` (float): Current portfolio value

**Returns:**
- `dict`: Position sizes keyed by symbol (as percentages)

**Example:**
```python
def calculate_position_sizes(self, signals, data, portfolio_value):
    position_sizes = {}
    
    active_signals = {k: v for k, v in signals.items() if v != 0}
    
    if not active_signals:
        return {}
    
    # Equal weight allocation
    weight_per_position = 1.0 / len(active_signals)
    
    for symbol, signal in active_signals.items():
        if signal == 1:
            position_sizes[symbol] = weight_per_position
        else:
            position_sizes[symbol] = -weight_per_position
    
    return position_sizes
```

### Optional Methods

#### `update_positions(new_positions)`

Updates current positions (optional override).

**Parameters:**
- `new_positions` (dict): New position information

#### `record_trade(trade)`

Records completed trades (optional override).

**Parameters:**
- `trade` (dict): Trade information

### Strategy Template

```python
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class MyStrategy(BaseStrategy):
    """
    Template for creating custom strategies.
    """
    
    def __init__(self, param1=10, param2=0.05):
        """
        Initialize strategy parameters.
        
        Args:
            param1 (int): First parameter
            param2 (float): Second parameter
        """
        super().__init__(param1=param1, param2=param2)
        
        # Store parameters
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data):
        """
        Generate trading signals.
        
        Args:
            data (dict): Dictionary of DataFrames keyed by symbol
            
        Returns:
            dict: Trading signals for each symbol
        """
        signals = {}
        
        for symbol, df in data.items():
            # Check if enough data is available
            if len(df) < self.param1:
                signals[symbol] = 0
                continue
            
            # Your signal logic here
            signal = self._calculate_signal(df)
            signals[symbol] = signal
        
        return signals
    
    def _calculate_signal(self, df):
        """
        Calculate signal for a single asset.
        
        Args:
            df (DataFrame): Asset data
            
        Returns:
            int: Signal (-1, 0, 1)
        """
        # Example: Simple moving average crossover
        short_ma = df['Close'].rolling(self.param1).mean()
        long_ma = df['Close'].rolling(self.param1 * 2).mean()
        
        current_price = df['Close'].iloc[-1]
        short_ma_current = short_ma.iloc[-1]
        long_ma_current = long_ma.iloc[-1]
        
        # Generate signal
        if short_ma_current > long_ma_current:
            return 1  # Buy
        elif short_ma_current < long_ma_current:
            return -1  # Sell
        else:
            return 0  # Hold
    
    def calculate_position_sizes(self, signals, data, portfolio_value):
        """
        Calculate position sizes (optional override).
        
        Args:
            signals (dict): Trading signals
            data (dict): Market data
            portfolio_value (float): Portfolio value
            
        Returns:
            dict: Position sizes
        """
        # Use default implementation or override with custom logic
        return super().calculate_position_sizes(signals, data, portfolio_value)
```

---

## Utility Functions

### Performance Calculation

#### `calculate_returns(prices)`

Calculates returns from price series.

**Parameters:**
- `prices` (Series): Price series

**Returns:**
- `Series`: Return series

**Example:**
```python
from src.utils import calculate_returns

returns = calculate_returns(df['Close'])
print(f"Average return: {returns.mean():.4f}")
print(f"Volatility: {returns.std():.4f}")
```

#### `calculate_sharpe_ratio(returns, risk_free_rate=0.02)`

Calculates Sharpe ratio.

**Parameters:**
- `returns` (Series): Return series
- `risk_free_rate` (float): Risk-free rate (default: 0.02)

**Returns:**
- `float`: Sharpe ratio

**Example:**
```python
from src.utils import calculate_sharpe_ratio

sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.02)
print(f"Sharpe Ratio: {sharpe:.2f}")
```

#### `calculate_max_drawdown(equity_curve)`

Calculates maximum drawdown.

**Parameters:**
- `equity_curve` (Series): Portfolio equity curve

**Returns:**
- `float`: Maximum drawdown percentage

**Example:**
```python
from src.utils import calculate_max_drawdown

max_dd = calculate_max_drawdown(portfolio_values)
print(f"Max Drawdown: {max_dd:.2%}")
```

### Data Utilities

#### `resample_data(data, interval)`

Resamples data to different intervals.

**Parameters:**
- `data` (DataFrame): OHLCV data
- `interval` (str): Target interval

**Returns:**
- `DataFrame`: Resampled data

**Example:**
```python
from src.utils import resample_data

# Resample daily data to weekly
weekly_data = resample_data(daily_data, 'W')
print(f"Weekly data: {len(weekly_data)} weeks")
```

#### `add_technical_indicators(df)`

Adds common technical indicators to a DataFrame.

**Parameters:**
- `df` (DataFrame): OHLCV data

**Returns:**
- `DataFrame`: Data with added indicators

**Example:**
```python
from src.utils import add_technical_indicators

# Add common indicators
df_with_indicators = add_technical_indicators(df)

# Access indicators
sma_20 = df_with_indicators['SMA_20']
rsi = df_with_indicators['RSI']
macd = df_with_indicators['MACD']
```

---

## 🔍 Error Handling

### Common Exceptions

#### `InsufficientDataError`

Raised when there's insufficient data for strategy execution.

**Example:**
```python
try:
    signals = strategy.generate_signals(data)
except InsufficientDataError as e:
    print(f"Not enough data: {e}")
    # Handle insufficient data
```

#### `DataProviderError`

Raised when there are issues with data providers.

**Example:**
```python
try:
    data = dm.get_data(provider, symbols, start_date, end_date, interval)
except DataProviderError as e:
    print(f"Data provider error: {e}")
    # Handle data provider issues
```

#### `StrategyError`

Raised when there are issues with strategy execution.

**Example:**
```python
try:
    results = backtester.run(data=data)
except StrategyError as e:
    print(f"Strategy error: {e}")
    # Handle strategy execution issues
```

### Best Practices for Error Handling

```python
def robust_strategy_execution(strategy, data):
    """Execute strategy with comprehensive error handling."""
    
    try:
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Calculate positions
        portfolio_value = 10000
        positions = strategy.calculate_position_sizes(signals, data, portfolio_value)
        
        # Run backtest
        backtester = Backtester(strategy=strategy)
        results = backtester.run(data=data)
        
        return results
        
    except InsufficientDataError as e:
        print(f"Insufficient data: {e}")
        return None
        
    except DataProviderError as e:
        print(f"Data provider error: {e}")
        return None
        
    except StrategyError as e:
        print(f"Strategy error: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

---

## 📚 Additional Resources

- **Quick Start Tutorial**: [docs/TUTORIALS/quick_start.md](../TUTORIALS/quick_start.md)
- **Strategy Development Guide**: [docs/STRATEGY_GUIDE.md](../STRATEGY_GUIDE.md)
- **Data Management Guide**: [DATA_MANAGEMENT_README.md](../../DATA_MANAGEMENT_README.md)
- **Risk Management Guide**: [README_RISK_MANAGEMENT.md](../../README_RISK_MANAGEMENT.md)

---

**🎯 This API reference covers all major components of QTF. Use it alongside the tutorials and guides to build sophisticated trading strategies!**
