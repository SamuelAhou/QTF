# QTF - Quantitative Trading Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, modular framework for quantitative trading research, backtesting, and risk management. QTF provides a clean, extensible architecture for developing and testing trading strategies with built-in data management, backtesting capabilities, and flexible risk controls.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd QTF

# Install dependencies
pip install -r requirements.txt

# For data management features
pip install -r requirements_data.txt
```

### Your First Backtest

```python
from src.Backtester import Backtester
from strategies.SMA import SMAStrategy

# Create a simple moving average strategy
strategy = SMAStrategy(short_window=20, long_window=100)

# Run backtest
backtester = Backtester(strategy=strategy)
results = backtester.run()

print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

### Download Market Data

```python
python main.py
```

This will download BTCUSDT data from Binance as a demonstration of the data management system.

## 🏗️ Architecture

QTF is built with a modular, dependency-injection pattern:


```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Strategies    │    │   Backtester    │    │ Risk Manager    │
│                 │    │                 │    │                 │
│ • SMA           │───▶│ • Strategy      │◀───│ • Stop-Loss     │
│ • Pairs Trading │    │ • Data          │    │ • Position      │
│ • Custom        │    │ • Performance   │    │ • VaR Limits    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                                │
                       ┌─────────────────┐
                       │ Data Provider   │
                       │                 │
                       │ • Multi-source  │
                       │ • Smart caching │
                       │ • Asset-based   │
                       └─────────────────┘
```

## 📚 Documentation

### **Core Documentation**
- **[Data Management Guide](DATA_MANAGEMENT_README.md)** - How to fetch, store, and manage market data
- **[Risk Management Guide](README_RISK_MANAGEMENT.md)** - Comprehensive risk control system
- **[Strategy Development](docs/STRATEGY_GUIDE.md)** - How to create custom trading strategies
- **[API Reference](docs/API_REFERENCE.md)** - Complete function and class documentation

### **Examples & Tutorials**
- **[Quick Start Tutorial](docs/TUTORIALS/quick_start.md)** - Step-by-step beginner guide
- **[Strategy Examples](docs/EXAMPLES/)** - Analysis of built-in strategies
- **[Jupyter Notebooks](notebooks/)** - Interactive examples and analysis

## 🎯 Key Features

### **Data Management**
- **Multi-source support**: Yahoo Finance, Binance, Alpha Vantage, and more
- **Smart caching**: Never re-download existing data
- **Asset-based storage**: Clean file organization by symbol and interval
- **Intelligent merging**: Automatic data combination and validation

### **Strategy Framework**
- **Modular design**: Easy to create and test new strategies
- **Standardized interface**: Consistent API across all strategies
- **Performance metrics**: Comprehensive backtesting results
- **Extensible**: Add custom indicators and signals

### **Risk Management**
- **Zero overhead by default**: No risk controls unless explicitly added
- **Modular risk controls**: Add only what you need
- **Professional-grade**: VaR, correlation limits, sector exposure
- **Dependency injection**: Clean separation of concerns

### **Backtesting Engine**
- **Realistic simulation**: Transaction costs, slippage, market impact
- **Performance analysis**: Returns, Sharpe ratio, drawdown analysis
- **Visualization**: Charts and performance reports
- **Export capabilities**: PDF reports and data export

## 🔧 Configuration

### Environment Setup

```bash
# Copy and configure environment variables
cp config/.env.example config/.env

# Edit config files
nano config/api_config.py
nano config/risk_config.py
```

### Data Sources

Configure your preferred data providers in `config/api_config.py`:

```python
# Example configuration
BINANCE_API_KEY = "your_api_key"
BINANCE_SECRET_KEY = "your_secret_key"
YAHOO_FINANCE_ENABLED = True
ALPHA_VANTAGE_API_KEY = "your_api_key"
```

## 📊 Built-in Strategies

### Simple Moving Average (SMA)
- **File**: `strategies/SMA.py`
- **Description**: Classic trend-following strategy using moving average crossovers
- **Parameters**: Short and long window periods
- **Best for**: Trending markets, momentum strategies

### Pairs Trading
- **File**: `strategies/PairsTrading.py`
- **Description**: Statistical arbitrage using cointegrated asset pairs
- **Parameters**: Z-score thresholds, lookback periods
- **Best for**: Mean reversion, market-neutral strategies

## 🚀 Getting Started

1. **Install dependencies** (see Installation above)
2. **Configure data sources** in `config/api_config.py`
3. **Run the demo**: `python main.py`
4. **Explore strategies**: Check `strategies/` directory
5. **Create your own**: Use the strategy template in `docs/STRATEGY_GUIDE.md`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/ strategies/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the guides above
- **Issues**: [GitHub Issues](https://github.com/your-repo/QTF/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/QTF/discussions)

## 🙏 Acknowledgments

- Built with modern Python best practices
- Inspired by professional quantitative trading systems
- Community-driven development and testing

---

**Ready to start trading?** Check out the [Quick Start Tutorial](docs/TUTORIALS/quick_start.md) or dive into [Strategy Development](docs/STRATEGY_GUIDE.md)!
