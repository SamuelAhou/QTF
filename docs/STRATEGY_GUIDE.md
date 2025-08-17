# Strategy Development Guide

This guide teaches you how to create custom trading strategies in QTF. You'll learn the strategy interface, best practices, and how to implement various trading approaches.

## 🎯 What You'll Learn

- Understanding the Strategy Interface
- Creating Your First Strategy
- Implementing Common Patterns
- Best Practices and Optimization
- Testing and Validation

## 🏗️ Strategy Interface

All strategies in QTF must implement a specific interface. Let's examine the core components:

### Base Strategy Class

```python
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseStrategy(ABC):
    """Base class for all trading strategies in QTF."""
    
    def __init__(self, **kwargs):
        """Initialize strategy parameters."""
        self.parameters = kwargs
        self.positions = {}  # Current positions
        self.trades = []     # Trade history
        
    @abstractmethod
    def generate_signals(self, data):
        """
        Generate trading signals from market data.
        
        Args:
            data (dict): Dictionary of DataFrames keyed by symbol
            
        Returns:
            dict: Dictionary of signals keyed by symbol
                  -1: Sell signal
                   0: Hold/no signal  
                   1: Buy signal
        """
        pass
    
    def calculate_position_sizes(self, signals, data, portfolio_value):
        """
        Calculate position sizes based on signals and portfolio value.
        
        Args:
            signals (dict): Trading signals from generate_signals()
            data (dict): Market data
            portfolio_value (float): Current portfolio value
            
        Returns:
            dict: Position sizes keyed by symbol
        """
        # Default implementation: equal weight per signal
        active_signals = {k: v for k, v in signals.items() if v != 0}
        
        if not active_signals:
            return {}
        
        # Equal weight allocation
        weight_per_position = 1.0 / len(active_signals)
        position_sizes = {}
        
        for symbol, signal in active_signals.items():
            if signal == 1:  # Buy signal
                position_sizes[symbol] = weight_per_position
            elif signal == -1:  # Sell signal
                position_sizes[symbol] = -weight_per_position
                
        return position_sizes
    
    def update_positions(self, new_positions):
        """Update current positions."""
        self.positions.update(new_positions)
    
    def record_trade(self, trade):
        """Record a completed trade."""
        self.trades.append(trade)
```

## 🚀 Creating Your First Strategy

Let's create a simple momentum strategy step by step:

### Step 1: Strategy Definition

```python
from src.strategies.BaseStrategy import BaseStrategy
import pandas as pd
import numpy as np

class MomentumStrategy(BaseStrategy):
    """
    Simple momentum strategy that buys assets with positive momentum
    and sells assets with negative momentum.
    """
    
    def __init__(self, lookback_period=20, momentum_threshold=0.02):
        """
        Initialize the momentum strategy.
        
        Args:
            lookback_period (int): Number of periods to calculate momentum
            momentum_threshold (float): Minimum momentum to trigger signals
        """
        super().__init__(
            lookback_period=lookback_period,
            momentum_threshold=momentum_threshold
        )
        
        # Store parameters
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
    
    def generate_signals(self, data):
        """
        Generate trading signals based on momentum.
        
        Args:
            data (dict): Dictionary of DataFrames keyed by symbol
            
        Returns:
            dict: Trading signals for each symbol
        """
        signals = {}
        
        for symbol, df in data.items():
            if len(df) < self.lookback_period:
                # Not enough data
                signals[symbol] = 0
                continue
            
            # Calculate momentum (price change over lookback period)
            current_price = df['Close'].iloc[-1]
            past_price = df['Close'].iloc[-self.lookback_period]
            momentum = (current_price - past_price) / past_price
            
            # Generate signals based on momentum
            if momentum > self.momentum_threshold:
                signals[symbol] = 1  # Buy signal
            elif momentum < -self.momentum_threshold:
                signals[symbol] = -1  # Sell signal
            else:
                signals[symbol] = 0  # Hold
                
        return signals
    
    def calculate_position_sizes(self, signals, data, portfolio_value):
        """
        Calculate position sizes with momentum-based weighting.
        
        Args:
            signals (dict): Trading signals
            data (dict): Market data
            portfolio_value (float): Portfolio value
            
        Returns:
            dict: Position sizes
        """
        active_signals = {k: v for k, v in signals.items() if v != 0}
        
        if not active_signals:
            return {}
        
        # Calculate momentum scores for weighting
        momentum_scores = {}
        total_score = 0
        
        for symbol, signal in active_signals.items():
            df = data[symbol]
            if len(df) >= self.lookback_period:
                current_price = df['Close'].iloc[-1]
                past_price = df['Close'].iloc[-self.lookback_period]
                momentum = (current_price - past_price) / past_price
                
                # Use absolute momentum for weighting
                momentum_scores[symbol] = abs(momentum)
                total_score += abs(momentum)
        
        # Calculate position sizes
        position_sizes = {}
        
        for symbol, signal in active_signals.items():
            if total_score > 0:
                # Weight by momentum strength
                weight = momentum_scores[symbol] / total_score
                if signal == 1:
                    position_sizes[symbol] = weight
                else:
                    position_sizes[symbol] = -weight
            else:
                # Equal weight fallback
                weight = 1.0 / len(active_signals)
                if signal == 1:
                    position_sizes[symbol] = weight
                else:
                    position_sizes[symbol] = -weight
                    
        return position_sizes
```

### Step 2: Save Your Strategy

Save the strategy in the `strategies/` directory:

```bash
# Create the file
touch strategies/MomentumStrategy.py

# Copy the code above into the file
```

### Step 3: Test Your Strategy

Create a test script:

```python
#!/usr/bin/env python3
"""
Test the Momentum Strategy
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from strategies.MomentumStrategy import MomentumStrategy
from src.Backtester import Backtester
from src.DataProvider import get_data_manager

def test_momentum_strategy():
    """Test the momentum strategy with sample data."""
    
    # Create strategy
    strategy = MomentumStrategy(lookback_period=20, momentum_threshold=0.02)
    
    # Get data
    dm = get_data_manager("data")
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=100)
    
    data = dm.get_data("binance", ["BTCUSDT"], start_date, end_date, "1d")
    
    if "BTCUSDT" not in data:
        print("❌ No BTCUSDT data found. Run 'python main.py' first.")
        return
    
    # Generate signals
    signals = strategy.generate_signals(data)
    print(f"Signals: {signals}")
    
    # Calculate position sizes
    portfolio_value = 10000
    positions = strategy.calculate_position_sizes(signals, data, portfolio_value)
    print(f"Positions: {positions}")
    
    # Run backtest
    backtester = Backtester(strategy=strategy)
    results = backtester.run(data=data)
    
    print(f"\nResults:")
    print(f"Total Return: {results.get('total_return', 0):.2%}")
    print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")

if __name__ == "__main__":
    test_momentum_strategy()
```

## 🔧 Advanced Strategy Patterns

### Pattern 1: Multi-Timeframe Analysis

```python
class MultiTimeframeStrategy(BaseStrategy):
    """Strategy using multiple timeframes for signal generation."""
    
    def __init__(self, short_period=5, medium_period=20, long_period=50):
        super().__init__(
            short_period=short_period,
            medium_period=medium_period,
            long_period=long_period
        )
    
    def generate_signals(self, data):
        signals = {}
        
        for symbol, df in data.items():
            # Short-term trend
            short_ma = df['Close'].rolling(self.short_period).mean()
            # Medium-term trend  
            medium_ma = df['Close'].rolling(self.medium_period).mean()
            # Long-term trend
            long_ma = df['Close'].rolling(self.long_period).mean()
            
            current_price = df['Close'].iloc[-1]
            
            # Multi-timeframe signal logic
            short_bullish = current_price > short_ma.iloc[-1]
            medium_bullish = current_price > medium_ma.iloc[-1]
            long_bullish = current_price > long_ma.iloc[-1]
            
            # All timeframes must align for strong signals
            if short_bullish and medium_bullish and long_bullish:
                signals[symbol] = 1
            elif not short_bullish and not medium_bullish and not long_bullish:
                signals[symbol] = -1
            else:
                signals[symbol] = 0
                
        return signals
```

### Pattern 2: Mean Reversion with Volatility

```python
class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy with volatility adjustment."""
    
    def __init__(self, lookback=20, zscore_threshold=2.0):
        super().__init__(lookback=lookback, zscore_threshold=zscore_threshold)
    
    def generate_signals(self, data):
        signals = {}
        
        for symbol, df in data.items():
            if len(df) < self.lookback:
                signals[symbol] = 0
                continue
            
            # Calculate rolling mean and standard deviation
            rolling_mean = df['Close'].rolling(self.lookback).mean()
            rolling_std = df['Close'].rolling(self.lookback).std()
            
            current_price = df['Close'].iloc[-1]
            current_mean = rolling_mean.iloc[-1]
            current_std = rolling_std.iloc[-1]
            
            if current_std == 0:
                signals[symbol] = 0
                continue
            
            # Calculate z-score
            zscore = (current_price - current_mean) / current_std
            
            # Generate signals based on z-score
            if zscore > self.zscore_threshold:
                signals[symbol] = -1  # Overbought - sell
            elif zscore < -self.zscore_threshold:
                signals[symbol] = 1   # Oversold - buy
            else:
                signals[symbol] = 0   # Hold
                
        return signals
```

### Pattern 3: Risk-Adjusted Position Sizing

```python
class RiskAdjustedStrategy(BaseStrategy):
    """Strategy with risk-adjusted position sizing."""
    
    def __init__(self, max_risk_per_trade=0.02, volatility_lookback=20):
        super().__init__(
            max_risk_per_trade=max_risk_per_trade,
            volatility_lookback=volatility_lookback
        )
    
    def calculate_position_sizes(self, signals, data, portfolio_value):
        """Calculate position sizes based on risk and volatility."""
        
        active_signals = {k: v for k, v in signals.items() if v != 0}
        
        if not active_signals:
            return {}
        
        position_sizes = {}
        
        for symbol, signal in active_signals.items():
            df = data[symbol]
            
            if len(df) < self.volatility_lookback:
                continue
            
            # Calculate volatility
            returns = df['Close'].pct_change().dropna()
            volatility = returns.rolling(self.volatility_lookback).std().iloc[-1]
            
            if volatility == 0:
                continue
            
            # Risk-adjusted position size
            # Higher volatility = smaller position
            risk_adjusted_weight = self.max_risk_per_trade / volatility
            
            # Cap at reasonable levels
            risk_adjusted_weight = min(risk_adjusted_weight, 0.5)
            
            if signal == 1:
                position_sizes[symbol] = risk_adjusted_weight
            else:
                position_sizes[symbol] = -risk_adjusted_weight
                
        return position_sizes
```

## 📊 Strategy Validation

### Performance Metrics

```python
def validate_strategy(strategy, data, initial_capital=10000):
    """Validate strategy performance with comprehensive metrics."""
    
    # Run backtest
    backtester = Backtester(strategy=strategy)
    results = backtester.run(data=data, initial_capital=initial_capital)
    
    print("=== Strategy Validation Results ===")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Value: ${results.get('final_value', 0):,.2f}")
    print(f"Total Return: {results.get('total_return', 0):.2%}")
    print(f"Annualized Return: {results.get('annualized_return', 0):.2%}")
    print(f"Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
    print(f"Max Drawdown: {results.get('max_drawdown', 0):.2%}")
    print(f"Calmar Ratio: {results.get('calmar_ratio', 0):.2f}")
    print(f"Win Rate: {results.get('win_rate', 0):.1%}")
    print(f"Profit Factor: {results.get('profit_factor', 0):.2f}")
    
    # Risk metrics
    print(f"\nRisk Metrics:")
    print(f"Volatility: {results.get('volatility', 0):.2%}")
    print(f"VaR (95%): {results.get('var_95', 0):.2%}")
    print(f"CVaR (95%): {results.get('cvar_95', 0):.2%}")
    
    return results
```

### Walk-Forward Analysis

```python
def walk_forward_analysis(strategy_class, data, 
                         train_period=252, test_period=63, 
                         step_size=21):
    """
    Perform walk-forward analysis to test strategy robustness.
    
    Args:
        strategy_class: Strategy class to test
        data: Market data
        train_period: Training period in days
        test_period: Testing period in days  
        step_size: Step size for forward testing
    """
    
    results = []
    symbols = list(data.keys())
    main_symbol = symbols[0]  # Use first symbol for date range
    
    df = data[main_symbol]
    total_days = len(df)
    
    for start_idx in range(0, total_days - train_period - test_period, step_size):
        # Training period
        train_start = start_idx
        train_end = start_idx + train_period
        
        # Testing period
        test_start = train_end
        test_end = min(test_start + test_period, total_days)
        
        # Split data
        train_data = {}
        test_data = {}
        
        for symbol in symbols:
            train_data[symbol] = df.iloc[train_start:train_end]
            test_data[symbol] = df.iloc[test_start:test_end]
        
        # Train strategy (if needed)
        strategy = strategy_class()
        
        # Test strategy
        backtester = Backtester(strategy=strategy)
        test_results = backtester.run(data=test_data)
        
        results.append({
            'period': f"{df.index[train_start].strftime('%Y-%m-%d')} to {df.index[test_end-1].strftime('%Y-%m-%d')}",
            'return': test_results.get('total_return', 0),
            'sharpe': test_results.get('sharpe_ratio', 0),
            'drawdown': test_results.get('max_drawdown', 0)
        })
    
    # Analyze results
    returns = [r['return'] for r in results]
    sharpe_ratios = [r['sharpe'] for r in results]
    
    print("=== Walk-Forward Analysis Results ===")
    print(f"Number of periods: {len(results)}")
    print(f"Average return: {np.mean(returns):.2%}")
    print(f"Return std dev: {np.std(returns):.2%}")
    print(f"Average Sharpe: {np.mean(sharpe_ratios):.2f}")
    print(f"Sharpe std dev: {np.std(sharpe_ratios):.2f}")
    
    return results
```

## 🎯 Best Practices

### 1. **Parameter Validation**
```python
def __init__(self, lookback_period=20, momentum_threshold=0.02):
    # Validate parameters
    if lookback_period < 1:
        raise ValueError("lookback_period must be >= 1")
    if momentum_threshold <= 0:
        raise ValueError("momentum_threshold must be > 0")
    
    super().__init__(
        lookback_period=lookback_period,
        momentum_threshold=momentum_threshold
    )
```

### 2. **Error Handling**
```python
def generate_signals(self, data):
    signals = {}
    
    for symbol, df in data.items():
        try:
            if len(df) < self.lookback_period:
                signals[symbol] = 0
                continue
            
            # Your signal logic here
            signals[symbol] = self._calculate_signal(df)
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            signals[symbol] = 0  # Default to hold
            
    return signals
```

### 3. **Logging and Debugging**
```python
import logging

class DebugStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_signals(self, data):
        self.logger.info(f"Generating signals for {len(data)} symbols")
        
        signals = {}
        for symbol, df in data.items():
            signal = self._calculate_signal(df)
            signals[symbol] = signal
            
            self.logger.debug(f"{symbol}: signal = {signal}")
        
        self.logger.info(f"Generated {len(signals)} signals")
        return signals
```

### 4. **Performance Optimization**
```python
class OptimizedStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}  # Simple caching
    
    def generate_signals(self, data):
        signals = {}
        
        for symbol, df in data.items():
            # Use cached calculations when possible
            cache_key = f"{symbol}_{len(df)}"
            
            if cache_key in self._cache:
                signals[symbol] = self._cache[cache_key]
            else:
                signal = self._calculate_signal(df)
                self._cache[cache_key] = signal
                signals[symbol] = signal
        
        return signals
```

## 🔍 Testing Your Strategy

### Unit Tests

```python
import unittest
import pandas as pd
import numpy as np

class TestMomentumStrategy(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.strategy = MomentumStrategy(lookback_period=5, momentum_threshold=0.01)
        
        # Create test data
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        prices = np.linspace(100, 110, 30)  # Upward trend
        
        self.test_data = {
            'TEST': pd.DataFrame({
                'Close': prices,
                'Open': prices * 0.99,
                'High': prices * 1.01,
                'Low': prices * 0.98,
                'Volume': 1000
            }, index=dates)
        }
    
    def test_momentum_calculation(self):
        """Test momentum calculation."""
        signals = self.strategy.generate_signals(self.test_data)
        
        # Should have a buy signal for upward trend
        self.assertIn('TEST', signals)
        self.assertEqual(signals['TEST'], 1)
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        short_data = {
            'TEST': self.test_data['TEST'].iloc[:3]  # Only 3 days
        }
        
        signals = self.strategy.generate_signals(short_data)
        self.assertEqual(signals['TEST'], 0)

if __name__ == '__main__':
    unittest.main()
```

## 📚 Next Steps

1. **Study Existing Strategies**: Examine `strategies/SMA.py` and `strategies/PairsTrading.py`
2. **Experiment with Parameters**: Test different parameter combinations
3. **Add Risk Management**: Integrate with the RiskManager class
4. **Create Custom Indicators**: Build reusable technical indicators
5. **Portfolio Strategies**: Develop multi-asset strategies

## 🆘 Need Help?

- **Check the API Reference** for detailed function documentation
- **Look at existing strategies** for implementation examples
- **Use the testing framework** to validate your strategies
- **Join the community** for support and feedback

---

**🎯 You're now ready to create sophisticated trading strategies in QTF!**

Start simple, test thoroughly, and gradually add complexity. The framework is designed to support your growth from basic strategies to advanced quantitative models.
