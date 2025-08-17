# Modular Risk Management System

## Overview

The Modular Risk Management System is a flexible and user-friendly solution for managing trading risk in the QTF (Quantitative Trading Framework). **By default, no risk management is enabled**, allowing you to start with a clean slate and add only the risk controls you need.

## 🚀 Key Features

### **Default Behavior: No Risk Management**
- **Clean Start**: No risk constraints by default
- **Strategy Freedom**: Your strategy executes without any interference
- **Performance**: No computational overhead from unused risk controls

### **Modular Risk Controls**
- **Stop-Loss & Take-Profit**: `risk_manager.add_sltp(stop_loss=0.05, take_profit=0.10)`
- **Position Limits**: `risk_manager.add_position_limits(max_position_pct=0.20, max_portfolio_exposure=0.80)`
- **VaR Limits**: `risk_manager.add_var_limits(var_limit=0.02, confidence=0.95)`
- **Correlation Controls**: `risk_manager.add_correlation_limits(max_correlation=0.7)`
- **Sector Exposure**: `risk_manager.add_sector_limits(max_sector_exposure=0.4)`
- **Volatility Targeting**: `risk_manager.add_volatility_targeting(target_vol=0.15)`
- **Drawdown Protection**: `risk_manager.add_drawdown_protection(max_drawdown=0.25)`

### **Dependency Injection Pattern**
- **Create RiskManager outside**: Configure risk controls before creating Backtester
- **Pass to Backtester**: Clean separation of concerns
- **Reusable**: Use the same RiskManager for multiple strategies
- **Testable**: Easy to mock and test individual components

## 🛠️ Usage

### **1. Start with No Risk Management**

```python
from src.Backtester import Backtester

# Create backtester with NO risk management
backtester = Backtester(strategy=strategy)

# Run backtest - strategy executes freely
results = backtester.run()
```

### **2. Add Basic Risk Controls**

```python
from src.Backtester import Backtester, RiskManager

# Create and configure risk manager
risk_manager = RiskManager()
risk_manager.add_sltp(
    stop_loss_pct=0.05,      # 5% stop-loss
    take_profit_pct=0.10,    # 10% take-profit
    re_entry_delay=3         # 3 periods delay
)

risk_manager.add_position_limits(
    max_position_pct=0.25,        # Max 25% per asset
    max_portfolio_exposure=0.70   # Max 70% total exposure
)

# Create backtester with configured risk manager
backtester = Backtester(strategy=strategy, risk_manager=risk_manager)

# Run backtest with basic risk management
results = backtester.run()
```

### **3. Add Advanced Risk Controls**

```python
# Create and configure risk manager
risk_manager = RiskManager()

# Add VaR limits
risk_manager.add_var_limits(
    var_limit=0.015,         # 1.5% daily VaR
    confidence=0.95,         # 95% confidence
    lookback=252             # 1 year lookback
)

# Add correlation limits
risk_manager.add_correlation_limits(
    max_correlation=0.6,     # Max 60% correlation
    lookback=60              # 60 days lookback
)

# Add sector limits
risk_manager.add_sector_limits(
    max_sector_exposure=0.35  # Max 35% per sector
)

# Add volatility targeting
risk_manager.add_volatility_targeting(
    target_volatility=0.12,   # 12% annual volatility target
    lookback=60,              # 60 days lookback
    use_dynamic_sizing=True   # Enable dynamic sizing
)

# Add drawdown protection
risk_manager.add_drawdown_protection(
    max_drawdown=0.20         # 20% maximum drawdown
)

# Create backtester with configured risk manager
backtester = Backtester(strategy=strategy, risk_manager=risk_manager)
```

### **4. Mix and Match Risk Controls**

```python
# Create risk manager with only specific features
risk_manager = RiskManager()

# Only volatility targeting and drawdown protection
risk_manager.add_volatility_targeting(0.15)
risk_manager.add_drawdown_protection(0.25)

# Create backtester
backtester = Backtester(strategy=strategy, risk_manager=risk_manager)
```

### **5. Reuse Risk Manager Across Strategies**

```python
# Create and configure risk manager once
risk_manager = RiskManager()
risk_manager.add_sltp(0.05, 0.10)
risk_manager.add_position_limits(0.20, 0.80)
risk_manager.add_var_limits(0.02)

# Use for multiple strategies
backtester1 = Backtester(strategy1, risk_manager)
backtester2 = Backtester(strategy2, risk_manager)
backtester3 = Backtester(strategy3, risk_manager)

# All use the same risk configuration
results1 = backtester1.run()
results2 = backtester2.run()
results3 = backtester3.run()
```

## 📊 Risk Management Presets

### **Risk Tolerance Levels**
- **Ultra Conservative**: 0.8% VaR, 10% max drawdown
- **Conservative**: 1.2% VaR, 15% max drawdown  
- **Moderate**: 1.8% VaR, 20% max drawdown
- **Aggressive**: 2.5% VaR, 25% max drawdown
- **Ultra Aggressive**: 3.5% VaR, 35% max drawdown

### **Trading Styles**
- **Day Trading**: Tight controls, 1.5% VaR, 15% drawdown
- **Swing Trading**: Balanced approach, 2.0% VaR, 22% drawdown
- **Position Trading**: Long-term focus, 2.5% VaR, 25% drawdown
- **Scalping**: Minimal risk, 1.0% VaR, 10% drawdown

### **Asset Class Specific**
- **Cryptocurrency**: High volatility, 2.5% VaR, 30% drawdown
- **Equities**: Moderate risk, 2.0% VaR, 22% drawdown
- **Forex**: Leverage risk, 1.8% VaR, 20% drawdown
- **Commodities**: Variable volatility, 2.2% VaR, 25% drawdown

## 📈 Risk Metrics Explained

### **Value at Risk (VaR)**
- **Definition**: Maximum expected loss over a specific time period at a given confidence level
- **Usage**: Automatically reduces position sizes when VaR exceeds limits
- **Add with**: `risk_manager.add_var_limits(var_limit=0.02)`

### **Correlation Limits**
- **Purpose**: Prevent over-concentration in highly correlated assets
- **Benefit**: Better diversification and reduced systemic risk
- **Add with**: `risk_manager.add_correlation_limits(max_correlation=0.7)`

### **Sector Exposure Limits**
- **Purpose**: Prevent over-concentration in specific sectors
- **Benefit**: Sector diversification and reduced sector-specific risk
- **Add with**: `risk_manager.add_sector_limits(max_sector_exposure=0.4)`

### **Volatility Targeting**
- **Purpose**: Maintain consistent portfolio volatility
- **Benefit**: Stable risk-adjusted returns across market conditions
- **Add with**: `risk_manager.add_volatility_targeting(target_vol=0.15)`

### **Maximum Drawdown Protection**
- **Purpose**: Prevent catastrophic losses
- **Action**: Closes all positions when limit is exceeded
- **Add with**: `risk_manager.add_drawdown_protection(max_drawdown=0.25)`

## 🔍 Risk Event Types

The system logs various types of risk management events:

- **position_entry**: New position opened
- **position_exit**: Position closed by strategy
- **position_change**: Position size modified
- **risk_exit**: Position closed by risk management
- **drawdown_limit**: Maximum drawdown exceeded
- **var_limit**: VaR limit exceeded
- **correlation_limit**: Correlation limit exceeded
- **sector_limit**: Sector exposure limit exceeded

## 📊 Example Output

```
🧪 EXAMPLE 1: NO RISK MANAGEMENT
============================================================
📊 Running backtest with NO risk management...
   Strategy will execute without any constraints
   📊 Results:
      Final Equity: $145,230.45
      Total Return: 45.23%
      Max Drawdown: -12.45%
      Volatility: 18.67%
   🛡️  Risk Management: ['None']

🧪 EXAMPLE 2: BASIC RISK MANAGEMENT
============================================================
🛡️  Adding basic risk controls...
✅ Stop-loss and take-profit enabled: SL 5.0%, TP 10.0%, Re-entry delay: 3
✅ Position limits enabled: Max 30% per asset, Max 80% total exposure
📊 Running backtest with basic risk management...
   📊 Results:
      Final Equity: $138,450.25
      Total Return: 38.45%
      Max Drawdown: -8.67%
      Volatility: 15.23%
   🛡️  Risk Management: ['Stop-loss & Take-profit', 'Position Limits']
   📋 Risk Events: 23 total
      position_entry: 8
      risk_exit: 5
      position_change: 10

🧪 EXAMPLE 5: REUSABLE RISK MANAGER
============================================================
🔄 Using the same risk manager for multiple strategies...
   📊 Testing SMA_10_20...
      SMA_10_20: 42.15% return
   📊 Testing SMA_20_50...
      SMA_20_50: 38.67% return
   📊 Testing SMA_50_100...
      SMA_50_100: 35.89% return
   ✅ All strategies used the same risk manager configuration
```

## ⚙️ Configuration Options

### **Risk Parameters**

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `stop_loss_pct` | Stop-loss percentage | 0.01 - 1.00 | None |
| `take_profit_pct` | Take-profit percentage | 0.01 - 1.00 | None |
| `re_entry_delay` | Re-entry delay periods | > 0 | None |
| `max_position_pct` | Max position per asset | 0.05 - 0.50 | None |
| `max_portfolio_exposure` | Max total exposure | 0.30 - 0.95 | None |
| `var_limit` | Daily VaR limit | 0.005 - 0.100 | None |
| `max_correlation` | Max correlation | 0.30 - 0.90 | None |
| `max_sector_exposure` | Max sector exposure | 0.15 - 0.80 | None |
| `target_volatility` | Annual volatility target | 0.05 - 0.50 | None |
| `max_drawdown` | Max drawdown | 0.10 - 0.50 | None |

### **Sector Mappings**

The system includes predefined sector mappings for common assets:

```python
# Crypto assets
'BTCUSDT': 'Cryptocurrency'
'ETHUSDT': 'Cryptocurrency'

# Tech stocks  
'AAPL': 'Technology'
'MSFT': 'Technology'

# Financial stocks
'JPM': 'Financials'
'BAC': 'Financials'
```

You can customize sector mappings by passing a custom dictionary to `add_sector_limits()`.

## 🧪 Testing

### **Run the Modular Examples**

```bash
python example_modular_risk_management.py
```

This will demonstrate:
1. **No Risk Management**: Strategy executes freely
2. **Basic Risk Management**: Stop-loss and position limits
3. **Advanced Risk Management**: All features enabled
4. **Selective Risk Management**: Only specific features
5. **Reusable Risk Manager**: Same configuration across multiple strategies

### **Test Individual Features**

```python
# Test only VaR limits
risk_manager = RiskManager()
risk_manager.add_var_limits(0.02)
backtester = Backtester(strategy, risk_manager)
results = backtester.run()

# Test only correlation limits
risk_manager = RiskManager()
risk_manager.add_correlation_limits(0.7)
backtester = Backtester(strategy, risk_manager)
results = backtester.run()
```

## 📚 Best Practices

### **1. Start Simple**
- Begin with no risk management
- Create RiskManager outside Backtester
- Add controls one at a time
- Test each addition before adding more

### **2. Understand Your Strategy**
- Know how your strategy behaves without constraints
- Add risk controls that complement your strategy
- Avoid over-constraining your strategy

### **3. Reuse and Configure**
- Create RiskManager once and reuse across strategies
- Use configuration files for different risk profiles
- Maintain consistent risk management across backtests

### **4. Monitor and Adjust**
- Review risk events regularly
- Adjust parameters based on performance
- Remove controls that aren't helping

## 🔮 Future Enhancements

Planned improvements include:

- **Risk Control Templates**: Pre-configured combinations for common use cases
- **Configuration Files**: JSON/YAML files for risk manager setup
- **Risk Performance Analytics**: Detailed analysis of risk management effectiveness
- **Real-time Risk Monitoring**: Live risk metrics during trading
- **Machine Learning Integration**: AI-powered risk parameter optimization

## 🤝 Contributing

To contribute to the risk management system:

1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or support:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed description
4. Contact the development team

---

**Note**: This risk management system is designed for educational and research purposes. Always validate risk parameters and test thoroughly before using in live trading environments.
