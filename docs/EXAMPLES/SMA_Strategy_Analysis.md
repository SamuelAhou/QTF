# SMA Strategy Analysis

This document provides a comprehensive analysis of the Simple Moving Average (SMA) strategy implemented in QTF. The SMA strategy is a classic trend-following approach that uses moving average crossovers to generate trading signals.

## 🎯 Strategy Overview

The SMA strategy is based on the principle that when a short-term moving average crosses above a long-term moving average, it signals an upward trend (buy signal). Conversely, when the short-term average crosses below the long-term average, it signals a downward trend (sell signal).

### Key Characteristics

- **Strategy Type**: Trend-following
- **Market Conditions**: Trending markets
- **Time Horizon**: Medium to long-term
- **Risk Profile**: Moderate
- **Best For**: Momentum strategies, trend identification

## 🏗️ Implementation Details

### Core Logic

```python
def generate_signals(self, data):
    """
    Generate trading signals based on SMA crossover.
    
    When short_MA > long_MA: BUY signal (1)
    When short_MA < long_MA: SELL signal (-1)
    When short_MA = long_MA: HOLD signal (0)
    """
    signals = {}
    
    for symbol, df in data.items():
        if len(df) < self.long_window:
            signals[symbol] = 0
            continue
        
        # Calculate moving averages
        short_ma = df['Close'].rolling(self.short_window).mean()
        long_ma = df['Close'].rolling(self.long_window).mean()
        
        # Get current values
        current_short_ma = short_ma.iloc[-1]
        current_long_ma = long_ma.iloc[-1]
        
        # Generate signal based on crossover
        if current_short_ma > current_long_ma:
            signals[symbol] = 1      # Buy signal
        elif current_short_ma < current_long_ma:
            signals[symbol] = -1     # Sell signal
        else:
            signals[symbol] = 0      # Hold signal
    
    return signals
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `short_window` | int | 20 | Short-term moving average period |
| `long_window` | int | 100 | Long-term moving average period |

### Parameter Selection Guidelines

#### Conservative Strategy
```python
# Long-term trend following
strategy = SMAStrategy(short_window=50, long_window=200)
```
- **Use Case**: Long-term investors, low turnover
- **Characteristics**: Fewer signals, lower transaction costs
- **Risk**: May miss short-term opportunities

#### Moderate Strategy
```python
# Balanced approach
strategy = SMAStrategy(short_window=20, long_window=100)
```
- **Use Case**: Balanced approach, moderate turnover
- **Characteristics**: Balanced signal frequency, reasonable costs
- **Risk**: Moderate risk-reward profile

#### Aggressive Strategy
```python
# Short-term trend following
strategy = SMAStrategy(short_window=5, long_window=20)
```
- **Use Case**: Active traders, high turnover
- **Characteristics**: Frequent signals, higher transaction costs
- **Risk**: Higher risk, potential for whipsaws

## 📊 Performance Analysis

### Historical Performance

Let's analyze the SMA strategy performance across different parameter combinations:

```python
import pandas as pd
import numpy as np
from src.Backtester import Backtester
from strategies.SMA import SMAStrategy
from src.DataProvider import get_data_manager

def analyze_sma_parameters():
    """Analyze SMA strategy with different parameters."""
    
    # Get data
    dm = get_data_manager("data")
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1000)  # ~3 years
    
    data = dm.get_data("yahoo", ["SPY"], start_date, end_date, "1d")
    
    if "SPY" not in data:
        print("❌ No SPY data found.")
        return
    
    # Parameter combinations to test
    param_combinations = [
        (5, 20),    # Aggressive
        (10, 50),   # Moderate-aggressive
        (20, 100),  # Moderate
        (50, 200),  # Conservative
        (100, 400)  # Very conservative
    ]
    
    results = []
    
    for short, long in param_combinations:
        print(f"\nTesting SMA({short}, {long})...")
        
        # Create strategy
        strategy = SMAStrategy(short_window=short, long_window=long)
        
        # Run backtest
        backtester = Backtester(strategy=strategy)
        backtest_results = backtester.run(data=data)
        
        # Store results
        results.append({
            'short_window': short,
            'long_window': long,
            'total_return': backtest_results.get('total_return', 0),
            'sharpe_ratio': backtest_results.get('sharpe_ratio', 0),
            'max_drawdown': backtest_results.get('max_drawdown', 0),
            'total_trades': backtest_results.get('total_trades', 0),
            'win_rate': backtest_results.get('win_rate', 0)
        })
        
        print(f"  Return: {backtest_results.get('total_return', 0):.2%}")
        print(f"  Sharpe: {backtest_results.get('sharpe_ratio', 0):.2f}")
        print(f"  Max DD: {backtest_results.get('max_drawdown', 0):.2%}")
    
    # Create results DataFrame
    df_results = pd.DataFrame(results)
    
    # Display summary
    print("\n" + "="*60)
    print("SMA Strategy Parameter Analysis Summary")
    print("="*60)
    print(df_results.to_string(index=False))
    
    # Find best parameters
    best_sharpe = df_results.loc[df_results['sharpe_ratio'].idxmax()]
    best_return = df_results.loc[df_results['total_return'].idxmax()]
    
    print(f"\nBest Sharpe Ratio: SMA({best_sharpe['short_window']}, {best_sharpe['long_window']})")
    print(f"Best Total Return: SMA({best_return['short_window']}, {best_return['long_window']})")
    
    return df_results

if __name__ == "__main__":
    analyze_sma_parameters()
```

### Expected Results

Based on typical market conditions, you might see results like:

| Parameters | Total Return | Sharpe Ratio | Max Drawdown | Total Trades |
|------------|--------------|--------------|--------------|--------------|
| SMA(5, 20) | 8.5% | 0.85 | -12.3% | 45 |
| SMA(10, 50) | 12.1% | 1.12 | -9.8% | 28 |
| SMA(20, 100) | 15.3% | 1.45 | -7.2% | 18 |
| SMA(50, 200) | 13.8% | 1.28 | -8.1% | 12 |
| SMA(100, 400) | 11.2% | 1.05 | -6.9% | 8 |

## 🔍 Strategy Behavior Analysis

### Market Conditions Performance

#### Trending Markets
- **Performance**: Excellent
- **Reason**: Moving averages excel at identifying and following trends
- **Example**: 2020-2021 bull market, 2008-2009 bear market

#### Sideways/Ranging Markets
- **Performance**: Poor
- **Reason**: Frequent crossovers generate false signals
- **Example**: 2015-2016 sideways market

#### Volatile Markets
- **Performance**: Mixed
- **Reason**: Can generate whipsaws but also catch quick trends
- **Example**: 2022 high volatility period

### Signal Quality Analysis

```python
def analyze_signal_quality(strategy, data):
    """Analyze the quality of SMA strategy signals."""
    
    signals = strategy.generate_signals(data)
    
    # Get the main symbol data
    symbol = list(data.keys())[0]
    df = data[symbol]
    
    # Calculate moving averages
    short_ma = df['Close'].rolling(strategy.short_window).mean()
    long_ma = df['Close'].rolling(strategy.long_window).mean()
    
    # Find crossover points
    crossovers = []
    for i in range(1, len(df)):
        prev_short = short_ma.iloc[i-1]
        prev_long = long_ma.iloc[i-1]
        curr_short = short_ma.iloc[i]
        curr_long = long_ma.iloc[i]
        
        # Bullish crossover
        if prev_short <= prev_long and curr_short > curr_long:
            crossovers.append({
                'date': df.index[i],
                'type': 'bullish',
                'price': df['Close'].iloc[i],
                'short_ma': curr_short,
                'long_ma': curr_long
            })
        
        # Bearish crossover
        elif prev_short >= prev_long and curr_short < curr_long:
            crossovers.append({
                'date': df.index[i],
                'type': 'bearish',
                'price': df['Close'].iloc[i],
                'short_ma': curr_short,
                'long_ma': curr_long
            })
    
    print(f"Total crossovers: {len(crossovers)}")
    
    # Analyze crossover effectiveness
    if len(crossovers) > 0:
        bullish_crossovers = [c for c in crossovers if c['type'] == 'bullish']
        bearish_crossovers = [c for c in crossovers if c['type'] == 'bearish']
        
        print(f"Bullish crossovers: {len(bullish_crossovers)}")
        print(f"Bearish crossovers: {len(bearish_crossovers)}")
        
        # Calculate average price change after crossover
        price_changes = []
        for crossover in crossovers:
            crossover_idx = df.index.get_loc(crossover['date'])
            if crossover_idx + 20 < len(df):  # Look 20 periods ahead
                future_price = df['Close'].iloc[crossover_idx + 20]
                price_change = (future_price - crossover['price']) / crossover['price']
                price_changes.append(price_change)
        
        if price_changes:
            avg_change = np.mean(price_changes)
            print(f"Average 20-period price change after crossover: {avg_change:.2%}")
    
    return crossovers
```

## 🚀 Optimization Strategies

### Parameter Optimization

```python
def optimize_sma_parameters(data, short_range=(5, 50), long_range=(20, 200)):
    """Optimize SMA parameters using grid search."""
    
    best_params = None
    best_sharpe = -np.inf
    
    results = []
    
    for short in range(short_range[0], short_range[1] + 1, 5):
        for long in range(long_range[0], long_range[1] + 1, 10):
            if short >= long:  # Skip invalid combinations
                continue
            
            try:
                # Create and test strategy
                strategy = SMAStrategy(short_window=short, long_window=long)
                backtester = Backtester(strategy=strategy)
                backtest_results = backtester.run(data=data)
                
                sharpe = backtest_results.get('sharpe_ratio', -np.inf)
                
                results.append({
                    'short': short,
                    'long': long,
                    'sharpe': sharpe,
                    'return': backtest_results.get('total_return', 0),
                    'drawdown': backtest_results.get('max_drawdown', 0)
                })
                
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = (short, long)
                    
            except Exception as e:
                print(f"Error testing SMA({short}, {long}): {e}")
                continue
    
    print(f"Best parameters: SMA({best_params[0]}, {best_params[1]})")
    print(f"Best Sharpe ratio: {best_sharpe:.2f}")
    
    return best_params, results
```

### Risk Management Integration

```python
def sma_with_risk_management():
    """Example of SMA strategy with risk management."""
    
    from src.Backtester import RiskManager
    
    # Create strategy
    strategy = SMAStrategy(short_window=20, long_window=100)
    
    # Create risk manager
    risk_manager = RiskManager()
    
    # Add stop-loss and take-profit
    risk_manager.add_sltp(
        stop_loss_pct=0.05,      # 5% stop-loss
        take_profit_pct=0.15,    # 15% take-profit
        re_entry_delay=5         # 5 periods delay
    )
    
    # Add position limits
    risk_manager.add_position_limits(
        max_position_pct=0.30,        # Max 30% per asset
        max_portfolio_exposure=0.80   # Max 80% total exposure
    )
    
    # Add volatility targeting
    risk_manager.add_volatility_targeting(
        target_volatility=0.15,   # 15% annual volatility target
        lookback=60,              # 60 days lookback
        use_dynamic_sizing=True   # Enable dynamic sizing
    )
    
    # Create backtester
    backtester = Backtester(strategy=strategy, risk_manager=risk_manager)
    
    return backtester
```

## 📈 Visualization Examples

### Moving Average Plot

```python
import matplotlib.pyplot as plt

def plot_sma_strategy(data, strategy):
    """Plot SMA strategy with moving averages and signals."""
    
    symbol = list(data.keys())[0]
    df = data[symbol]
    
    # Calculate moving averages
    short_ma = df['Close'].rolling(strategy.short_window).mean()
    long_ma = df['Close'].rolling(strategy.long_window).mean()
    
    # Generate signals
    signals = strategy.generate_signals(data)
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Price and moving averages
    ax1.plot(df.index, df['Close'], label='Price', alpha=0.7)
    ax1.plot(df.index, short_ma, label=f'SMA({strategy.short_window})', alpha=0.8)
    ax1.plot(df.index, long_ma, label=f'SMA({strategy.long_window})', alpha=0.8)
    
    # Highlight crossover points
    for i in range(1, len(df)):
        if short_ma.iloc[i-1] <= long_ma.iloc[i-1] and short_ma.iloc[i] > long_ma.iloc[i]:
            ax1.axvline(x=df.index[i], color='green', alpha=0.5, linestyle='--')
        elif short_ma.iloc[i-1] >= long_ma.iloc[i-1] and short_ma.iloc[i] < long_ma.iloc[i]:
            ax1.axvline(x=df.index[i], color='red', alpha=0.5, linestyle='--')
    
    ax1.set_title(f'SMA Strategy: {symbol}')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Signals
    signal_series = pd.Series(signals[symbol], index=df.index)
    ax2.plot(df.index, signal_series, label='Signals', linewidth=2)
    ax2.set_ylabel('Signal')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

## 🎯 Best Practices

### 1. **Parameter Selection**
- Start with moderate parameters (20, 100) for initial testing
- Use longer periods for less volatile assets
- Consider market regime when selecting parameters

### 2. **Risk Management**
- Always use stop-losses to limit downside
- Consider position sizing based on volatility
- Monitor drawdown and adjust parameters if needed

### 3. **Market Conditions**
- Avoid using in sideways markets
- Consider combining with other indicators for confirmation
- Test across different market regimes

### 4. **Performance Monitoring**
- Track signal quality over time
- Monitor transaction costs impact
- Regular parameter re-optimization

## 🔄 Alternative Implementations

### Enhanced SMA Strategy

```python
class EnhancedSMAStrategy(SMAStrategy):
    """Enhanced SMA strategy with additional features."""
    
    def __init__(self, short_window=20, long_window=100, 
                 volume_filter=True, trend_strength_filter=True):
        super().__init__(short_window, long_window)
        self.volume_filter = volume_filter
        self.trend_strength_filter = trend_strength_filter
    
    def generate_signals(self, data):
        """Generate signals with additional filters."""
        
        base_signals = super().generate_signals(data)
        
        if not self.volume_filter and not self.trend_strength_filter:
            return base_signals
        
        enhanced_signals = {}
        
        for symbol, signal in base_signals.items():
            if signal == 0:
                enhanced_signals[symbol] = 0
                continue
            
            df = data[symbol]
            
            # Volume filter
            if self.volume_filter:
                avg_volume = df['Volume'].rolling(20).mean()
                current_volume = df['Volume'].iloc[-1]
                if current_volume < avg_volume.iloc[-1] * 0.8:  # 20% below average
                    enhanced_signals[symbol] = 0
                    continue
            
            # Trend strength filter
            if self.trend_strength_filter:
                short_ma = df['Close'].rolling(self.short_window).mean()
                long_ma = df['Close'].rolling(self.long_window).mean()
                
                # Calculate trend strength
                trend_strength = abs(short_ma.iloc[-1] - long_ma.iloc[-1]) / long_ma.iloc[-1]
                
                if trend_strength < 0.02:  # Weak trend
                    enhanced_signals[symbol] = 0
                    continue
            
            enhanced_signals[symbol] = signal
        
        return enhanced_signals
```

## 📚 Conclusion

The SMA strategy is a robust, time-tested approach to trend following that works well in trending markets. While it has limitations in sideways markets, its simplicity and effectiveness make it an excellent starting point for quantitative trading.

### Key Takeaways

1. **Parameter selection is crucial** - longer periods reduce noise but increase lag
2. **Market conditions matter** - avoid sideways markets
3. **Risk management is essential** - always use stop-losses
4. **Regular monitoring required** - track performance and adjust as needed
5. **Consider enhancements** - volume and trend strength filters can improve performance

### Next Steps

1. **Test different parameters** on your preferred assets
2. **Add risk management** controls
3. **Combine with other indicators** for confirmation
4. **Monitor performance** across different market conditions
5. **Consider enhancements** like volume filters and trend strength measures

---

**🎯 The SMA strategy provides a solid foundation for trend-following approaches. Start simple and gradually add complexity as you gain experience!**
