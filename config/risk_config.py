"""
Risk Management Configuration Presets

This file provides pre-configured risk management settings for different
risk tolerance levels and trading styles. You can use these presets or
create custom configurations based on your specific needs.
"""

from typing import Dict, Any

# =========================
# Risk Tolerance Presets
# =========================

RISK_PRESETS = {
    'ultra_conservative': {
        'description': 'Ultra Conservative - Very low risk, suitable for capital preservation',
        'stop_loss_pct': 0.03,        # 3% stop-loss
        'take_profit_pct': 0.06,      # 6% take-profit
        're_entry_delay': 10,         # 10 periods delay
        'max_position_pct': 0.10,     # Max 10% per asset
        'max_portfolio_exposure': 0.50,  # Max 50% total exposure
        'var_limit': 0.008,           # 0.8% daily VaR limit
        'max_correlation': 0.4,       # Max 40% correlation
        'max_sector_exposure': 0.20,  # Max 20% in any sector
        'target_volatility': 0.06,    # 6% annual volatility target
        'max_drawdown': 0.10,         # 10% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'conservative': {
        'description': 'Conservative - Low risk, suitable for income generation',
        'stop_loss_pct': 0.05,        # 5% stop-loss
        'take_profit_pct': 0.10,      # 10% take-profit
        're_entry_delay': 7,          # 7 periods delay
        'max_position_pct': 0.15,     # Max 15% per asset
        'max_portfolio_exposure': 0.60,  # Max 60% total exposure
        'var_limit': 0.012,           # 1.2% daily VaR limit
        'max_correlation': 0.5,       # Max 50% correlation
        'max_sector_exposure': 0.30,  # Max 30% in any sector
        'target_volatility': 0.10,    # 10% annual volatility target
        'max_drawdown': 0.15,         # 15% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'moderate': {
        'description': 'Moderate - Balanced risk-reward, suitable for growth',
        'stop_loss_pct': 0.07,        # 7% stop-loss
        'take_profit_pct': 0.14,      # 14% take-profit
        're_entry_delay': 5,          # 5 periods delay
        'max_position_pct': 0.20,     # Max 20% per asset
        'max_portfolio_exposure': 0.70,  # Max 70% total exposure
        'var_limit': 0.018,           # 1.8% daily VaR limit
        'max_correlation': 0.6,       # Max 60% correlation
        'max_sector_exposure': 0.40,  # Max 40% in any sector
        'target_volatility': 0.15,    # 15% annual volatility target
        'max_drawdown': 0.20,         # 20% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'aggressive': {
        'description': 'Aggressive - Higher risk, suitable for capital appreciation',
        'stop_loss_pct': 0.10,        # 10% stop-loss
        'take_profit_pct': 0.20,      # 20% take-profit
        're_entry_delay': 3,          # 3 periods delay
        'max_position_pct': 0.25,     # Max 25% per asset
        'max_portfolio_exposure': 0.80,  # Max 80% total exposure
        'var_limit': 0.025,           # 2.5% daily VaR limit
        'max_correlation': 0.7,       # Max 70% correlation
        'max_sector_exposure': 0.50,  # Max 50% in any sector
        'target_volatility': 0.20,    # 20% annual volatility target
        'max_drawdown': 0.25,         # 25% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'ultra_aggressive': {
        'description': 'Ultra Aggressive - Very high risk, suitable for speculation',
        'stop_loss_pct': 0.15,        # 15% stop-loss
        'take_profit_pct': 0.30,      # 30% take-profit
        're_entry_delay': 2,          # 2 periods delay
        'max_position_pct': 0.30,     # Max 30% per asset
        'max_portfolio_exposure': 0.90,  # Max 90% total exposure
        'var_limit': 0.035,           # 3.5% daily VaR limit
        'max_correlation': 0.8,       # Max 80% correlation
        'max_sector_exposure': 0.60,  # Max 60% in any sector
        'target_volatility': 0.30,    # 30% annual volatility target
        'max_drawdown': 0.35,         # 35% maximum drawdown
        'use_dynamic_sizing': True
    }
}

# =========================
# Trading Style Presets
# =========================

TRADING_STYLE_PRESETS = {
    'day_trading': {
        'description': 'Day Trading - Short-term positions with tight risk controls',
        'stop_loss_pct': 0.02,        # 2% stop-loss
        'take_profit_pct': 0.04,      # 4% take-profit
        're_entry_delay': 1,          # 1 period delay
        'max_position_pct': 0.25,     # Max 25% per asset
        'max_portfolio_exposure': 0.80,  # Max 80% total exposure
        'var_limit': 0.015,           # 1.5% daily VaR limit
        'max_correlation': 0.6,       # Max 60% correlation
        'max_sector_exposure': 0.40,  # Max 40% in any sector
        'target_volatility': 0.25,    # 25% annual volatility target
        'max_drawdown': 0.15,         # 15% maximum drawdown
        'use_dynamic_sizing': False   # No dynamic sizing for day trading
    },
    
    'swing_trading': {
        'description': 'Swing Trading - Medium-term positions with moderate risk',
        'stop_loss_pct': 0.08,        # 8% stop-loss
        'take_profit_pct': 0.16,      # 16% take-profit
        're_entry_delay': 5,          # 5 periods delay
        'max_position_pct': 0.20,     # Max 20% per asset
        'max_portfolio_exposure': 0.70,  # Max 70% total exposure
        'var_limit': 0.020,           # 2.0% daily VaR limit
        'max_correlation': 0.6,       # Max 60% correlation
        'max_sector_exposure': 0.35,  # Max 35% in any sector
        'target_volatility': 0.18,    # 18% annual volatility target
        'max_drawdown': 0.22,         # 22% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'position_trading': {
        'description': 'Position Trading - Long-term positions with wider stops',
        'stop_loss_pct': 0.12,        # 12% stop-loss
        'take_profit_pct': 0.24,      # 24% take-profit
        're_entry_delay': 10,         # 10 periods delay
        'max_position_pct': 0.15,     # Max 15% per asset
        'max_portfolio_exposure': 0.60,  # Max 60% total exposure
        'var_limit': 0.025,           # 2.5% daily VaR limit
        'max_correlation': 0.5,       # Max 50% correlation
        'max_sector_exposure': 0.30,  # Max 30% in any sector
        'target_volatility': 0.20,    # 20% annual volatility target
        'max_drawdown': 0.25,         # 25% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'scalping': {
        'description': 'Scalping - Very short-term positions with minimal risk',
        'stop_loss_pct': 0.01,        # 1% stop-loss
        'take_profit_pct': 0.02,      # 2% take-profit
        're_entry_delay': 1,          # 1 period delay
        'max_position_pct': 0.30,     # Max 30% per asset
        'max_portfolio_exposure': 0.90,  # Max 90% total exposure
        'var_limit': 0.010,           # 1.0% daily VaR limit
        'max_correlation': 0.7,       # Max 70% correlation
        'max_sector_exposure': 0.50,  # Max 50% in any sector
        'target_volatility': 0.30,    # 30% annual volatility target
        'max_drawdown': 0.10,         # 10% maximum drawdown
        'use_dynamic_sizing': False
    }
}

# =========================
# Asset Class Specific Presets
# =========================

ASSET_CLASS_PRESETS = {
    'cryptocurrency': {
        'description': 'Cryptocurrency - High volatility, high risk',
        'stop_loss_pct': 0.10,        # 10% stop-loss
        'take_profit_pct': 0.20,      # 20% take-profit
        're_entry_delay': 3,          # 3 periods delay
        'max_position_pct': 0.15,     # Max 15% per asset
        'max_portfolio_exposure': 0.60,  # Max 60% total exposure
        'var_limit': 0.025,           # 2.5% daily VaR limit
        'max_correlation': 0.8,       # Max 80% correlation (crypto is highly correlated)
        'max_sector_exposure': 0.60,  # Max 60% in crypto sector
        'target_volatility': 0.25,    # 25% annual volatility target
        'max_drawdown': 0.30,         # 30% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'equities': {
        'description': 'Equities - Moderate volatility, moderate risk',
        'stop_loss_pct': 0.07,        # 7% stop-loss
        'take_profit_pct': 0.14,      # 14% take-profit
        're_entry_delay': 5,          # 5 periods delay
        'max_position_pct': 0.20,     # Max 20% per asset
        'max_portfolio_exposure': 0.70,  # Max 70% total exposure
        'var_limit': 0.020,           # 2.0% daily VaR limit
        'max_correlation': 0.6,       # Max 60% correlation
        'max_sector_exposure': 0.40,  # Max 40% in any sector
        'target_volatility': 0.18,    # 18% annual volatility target
        'max_drawdown': 0.22,         # 22% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'forex': {
        'description': 'Forex - Moderate volatility, leverage risk',
        'stop_loss_pct': 0.05,        # 5% stop-loss
        'take_profit_pct': 0.10,      # 10% take-profit
        're_entry_delay': 5,          # 5 periods delay
        'max_position_pct': 0.15,     # Max 15% per asset
        'max_portfolio_exposure': 0.60,  # Max 60% total exposure
        'var_limit': 0.018,           # 1.8% daily VaR limit
        'max_correlation': 0.7,       # Max 70% correlation
        'max_sector_exposure': 0.50,  # Max 50% in any currency pair
        'target_volatility': 0.15,    # 15% annual volatility target
        'max_drawdown': 0.20,         # 20% maximum drawdown
        'use_dynamic_sizing': True
    },
    
    'commodities': {
        'description': 'Commodities - Variable volatility, inflation hedge',
        'stop_loss_pct': 0.08,        # 8% stop-loss
        'take_profit_pct': 0.16,      # 16% take-profit
        're_entry_delay': 7,          # 7 periods delay
        'max_position_pct': 0.18,     # Max 18% per asset
        'max_portfolio_exposure': 0.65,  # Max 65% total exposure
        'var_limit': 0.022,           # 2.2% daily VaR limit
        'max_correlation': 0.6,       # Max 60% correlation
        'max_sector_exposure': 0.35,  # Max 35% in any sector
        'target_volatility': 0.20,    # 20% annual volatility target
        'max_drawdown': 0.25,         # 25% maximum drawdown
        'use_dynamic_sizing': True
    }
}

# =========================
# Utility Functions
# =========================

def get_risk_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get a risk management preset by name.
    
    Args:
        preset_name: Name of the preset (e.g., 'conservative', 'aggressive')
        
    Returns:
        Dictionary with risk management parameters
        
    Raises:
        ValueError: If preset name is not found
    """
    if preset_name in RISK_PRESETS:
        return RISK_PRESETS[preset_name].copy()
    elif preset_name in TRADING_STYLE_PRESETS:
        return TRADING_STYLE_PRESETS[preset_name].copy()
    elif preset_name in ASSET_CLASS_PRESETS:
        return ASSET_CLASS_PRESETS[preset_name].copy()
    else:
        available_presets = (list(RISK_PRESETS.keys()) + 
                           list(TRADING_STYLE_PRESETS.keys()) + 
                           list(ASSET_CLASS_PRESETS.keys()))
        raise ValueError(f"Preset '{preset_name}' not found. Available presets: {available_presets}")

def list_available_presets() -> Dict[str, list]:
    """List all available risk management presets."""
    return {
        'risk_tolerance': list(RISK_PRESETS.keys()),
        'trading_style': list(TRADING_STYLE_PRESETS.keys()),
        'asset_class': list(ASSET_CLASS_PRESETS.keys())
    }

def create_custom_preset(base_preset: str, **modifications) -> Dict[str, Any]:
    """
    Create a custom preset based on an existing one with modifications.
    
    Args:
        base_preset: Name of the base preset
        **modifications: Key-value pairs to modify
        
    Returns:
        Dictionary with modified risk management parameters
    """
    base_config = get_risk_preset(base_preset)
    custom_config = base_config.copy()
    
    # Apply modifications
    for key, value in modifications.items():
        if key in custom_config:
            custom_config[key] = value
        else:
            print(f"Warning: Unknown parameter '{key}' ignored")
    
    return custom_config

def validate_risk_config(config: Dict[str, Any]) -> bool:
    """
    Validate a risk management configuration.
    
    Args:
        config: Risk management configuration dictionary
        
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    errors = []
    
    # Check required parameters
    required_params = [
        'stop_loss_pct', 'take_profit_pct', 're_entry_delay',
        'max_position_pct', 'max_portfolio_exposure', 'var_limit',
        'max_correlation', 'max_sector_exposure', 'target_volatility',
        'max_drawdown', 'use_dynamic_sizing'
    ]
    
    for param in required_params:
        if param not in config:
            errors.append(f"Missing required parameter: {param}")
    
    # Check parameter ranges
    if 'stop_loss_pct' in config and (config['stop_loss_pct'] <= 0 or config['stop_loss_pct'] > 0.5):
        errors.append("stop_loss_pct must be between 0 and 0.5")
    
    if 'take_profit_pct' in config and (config['take_profit_pct'] <= 0 or config['take_profit_pct'] > 1.0):
        errors.append("take_profit_pct must be between 0 and 1.0")
    
    if 'var_limit' in config and (config['var_limit'] <= 0 or config['var_limit'] > 0.1):
        errors.append("var_limit must be between 0 and 0.1")
    
    if 'max_drawdown' in config and (config['max_drawdown'] <= 0 or config['max_drawdown'] > 0.5):
        errors.append("max_drawdown must be between 0 and 0.5")
    
    if errors:
        raise ValueError(f"Invalid configuration:\n" + "\n".join(errors))
    
    return True

# =========================
# Example Usage
# =========================

if __name__ == "__main__":
    print("🎯 Risk Management Configuration Presets")
    print("=" * 50)
    
    # List available presets
    presets = list_available_presets()
    print("Available presets:")
    for category, preset_list in presets.items():
        print(f"  {category}: {', '.join(preset_list)}")
    
    print("\n📊 Example: Conservative preset")
    conservative = get_risk_preset('conservative')
    print(f"Description: {conservative['description']}")
    print(f"VaR Limit: {conservative['var_limit']*100:.1f}%")
    print(f"Max Drawdown: {conservative['max_drawdown']*100:.0f}%")
    
    print("\n🔧 Example: Custom preset based on moderate")
    custom = create_custom_preset('moderate', 
                                 stop_loss_pct=0.06,  # Tighter stop-loss
                                 var_limit=0.015)     # Lower VaR
    print(f"Custom stop-loss: {custom['stop_loss_pct']*100:.0f}%")
    print(f"Custom VaR: {custom['var_limit']*100:.1f}%")
    
    print("\n✅ Configuration validation test")
    try:
        validate_risk_config(custom)
        print("Custom configuration is valid!")
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
