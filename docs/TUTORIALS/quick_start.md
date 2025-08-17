# Quick Start Tutorial

Welcome to QTF! This tutorial will guide you through setting up the framework and running your first backtest in under 10 minutes.

## 🎯 What You'll Learn

- Install and configure QTF
- Download your first dataset
- Create and run a simple strategy
- Understand the results
- Next steps for deeper exploration

## 📋 Prerequisites

- Python 3.8 or higher
- Basic Python knowledge
- Git (for cloning the repository)

## 🚀 Step 1: Installation

### Clone the Repository

```bash
git clone <your-repo-url>
cd QTF
```

### Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install data management dependencies
pip install -r requirements_data.txt
```

### Verify Installation

```bash
python -c "import pandas; import numpy; print('✅ Dependencies installed successfully!')"
```

## 📊 Step 2: Download Your First Dataset

QTF comes with a built-in data downloader. Let's start by downloading some Bitcoin data:

```bash
python main.py
```

This will:
- Download 2 years of BTCUSDT data from Binance
- Store it in the `data/` directory
- Show you detailed information about the downloaded data

**Expected Output:**
```
=== BTCUSDT Data Download from Binance ===

Downloading BTCUSDT data:
  Provider: binance
  Interval: 1d
  Date range: 2022-01-01 to 2024-01-01
  Total days: 730

1. Analyzing data needs...
  Needs download: True
  Reason: No existing data found
  Missing days: 730

2. Downloading data...
  Successfully downloaded data for BTCUSDT
  Data points: 730
  Date range: 2022-01-01 to 2024-01-01
  Columns: ['Open', 'High', 'Low', 'Close', 'Volume']

✅ Script completed successfully!
```

## 🎯 Step 3: Your First Backtest

Now let's run a simple moving average strategy on the data we just downloaded:

### Create a Python Script

Create a file called `my_first_backtest.py`:

```python
#!/usr/bin/env python3
"""
My first QTF backtest - Simple Moving Average Strategy
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.Backtester import Backtester
from strategies.SMA import SMAStrategy
from src.DataProvider import get_data_manager

def main():
    print("=== My First QTF Backtest ===\n")
    
    # 1. Create a simple moving average strategy
    print("1. Creating strategy...")
    strategy = SMAStrategy(short_window=20, long_window=100)
    print(f"   Strategy: {strategy.__class__.__name__}")
    print(f"   Short window: {strategy.short_window}")
    print(f"   Long window: {strategy.long_window}")
    
    # 2. Get data manager and fetch data
    print("\n2. Fetching data...")
    dm = get_data_manager("data")
    
    # Use the BTCUSDT data we downloaded
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Last year
    
    data = dm.get_data("binance", ["BTCUSDT"], start_date, end_date, "1d")
    
    if "BTCUSDT" not in data:
        print("❌ Error: No BTCUSDT data found. Run 'python main.py' first.")
        return
    
    print(f"   Data loaded: {len(data['BTCUSDT'])} data points")
    print(f"   Date range: {data['BTCUSDT'].index.min().strftime('%Y-%m-%d')} to {data['BTCUSDT'].index.max().strftime('%Y-%m-%d')}")
    
    # 3. Create backtester
    print("\n3. Creating backtester...")
    backtester = Backtester(strategy=strategy)
    
    # 4. Run the backtest
    print("\n4. Running backtest...")
    results = backtester.run(data=data)
    
    # 5. Display results
    print("\n5. Results:")
    print("=" * 50)
    
    # Basic metrics
    print(f"📈 Total Return: {results.get('total_return', 0):.2%}")
    print(f"📊 Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
    print(f"📉 Max Drawdown: {results.get('max_drawdown', 0):.2%}")
    print(f"💰 Final Portfolio Value: ${results.get('final_value', 0):,.2f}")
    
    # Trading statistics
    if 'trades' in results:
        trades = results['trades']
        print(f"🔄 Total Trades: {len(trades)}")
        if len(trades) > 0:
            winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
            win_rate = winning_trades / len(trades) * 100
            print(f"✅ Win Rate: {win_rate:.1f}%")
    
    print("=" * 50)
    print("\n🎉 Congratulations! You've completed your first QTF backtest!")
    
    return results

if __name__ == "__main__":
    main()
```

### Run Your First Backtest

```bash
python my_first_backtest.py
```

**Expected Output:**
```
=== My First QTF Backtest ===

1. Creating strategy...
   Strategy: SMAStrategy
   Short window: 20
   Long window: 100

2. Fetching data...
   Data loaded: 365 data points
   Date range: 2023-01-01 to 2024-01-01

3. Creating backtester...
4. Running backtest...

5. Results:
==================================================
📈 Total Return: 15.23%
📊 Sharpe Ratio: 1.45
📉 Max Drawdown: -8.76%
💰 Final Portfolio Value: $11,523.00
🔄 Total Trades: 12
✅ Win Rate: 66.7%
==================================================

🎉 Congratulations! You've completed your first QTF backtest!
```

## 🔍 Understanding the Results

### Key Metrics Explained

- **Total Return**: How much your strategy gained/lost over the period
- **Sharpe Ratio**: Risk-adjusted return (higher is better, >1 is good)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### What Happened

1. **Strategy Creation**: We created a simple moving average crossover strategy
2. **Data Loading**: QTF automatically loaded and prepared the BTCUSDT data
3. **Backtesting**: The system simulated trading based on your strategy rules
4. **Results**: Comprehensive performance metrics were calculated

## 🚀 Step 4: Explore Further

### Try Different Parameters

```python
# More aggressive strategy
strategy = SMAStrategy(short_window=10, long_window=50)

# More conservative strategy  
strategy = SMAStrategy(short_window=50, long_window=200)
```

### Test Different Assets

```python
# Try with different symbols
data = dm.get_data("yahoo", ["AAPL", "GOOGL"], start_date, end_date, "1d")
```

### Add Risk Management

```python
from src.Backtester import RiskManager

# Create risk manager
risk_manager = RiskManager()
risk_manager.add_sltp(stop_loss_pct=0.05, take_profit_pct=0.10)

# Add to backtester
backtester = Backtester(strategy=strategy, risk_manager=risk_manager)
```

## 📚 Next Steps

Now that you've completed your first backtest, here's what to explore next:

1. **Read the Documentation**:
   - [Data Management Guide](../../DATA_MANAGEMENT_README.md)
   - [Risk Management Guide](../../README_RISK_MANAGEMENT.md)
   - [Strategy Development Guide](../STRATEGY_GUIDE.md)

2. **Explore Built-in Strategies**:
   - Study `strategies/SMA.py` and `strategies/PairsTrading.py`
   - Understand how they implement the strategy interface

3. **Create Your Own Strategy**:
   - Use the strategy template in the Strategy Development Guide
   - Start with simple rules and gradually add complexity

4. **Advanced Features**:
   - Multi-asset portfolios
   - Custom indicators and signals
   - Risk management controls
   - Performance visualization

## 🆘 Need Help?

- **Check the documentation** in the `docs/` directory
- **Look at examples** in the `strategies/` directory
- **Review the API reference** for detailed function documentation

---

**🎯 You're now ready to start building your own quantitative trading strategies with QTF!**

The framework is designed to grow with you - start simple and add complexity as you learn. Happy trading! 🚀
