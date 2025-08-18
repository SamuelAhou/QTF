import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy import stats
import warnings

class Strategy:
    """Base class for trading strategies. Handles signal and position generation."""
    
    def __init__(self, data: Dict[str, pd.DataFrame], params: dict = None):
        
        if data is None:
            raise ValueError("data cannot be None")
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        if not all(isinstance(df, pd.DataFrame) for df in data.values()):
            raise ValueError("all values in data must be pandas DataFrames")
        if not all(df.index.is_monotonic_increasing for df in data.values()):
            raise ValueError("all DataFrames must have a monotonic increasing index")
        if not all(df.index.is_unique for df in data.values()):
            raise ValueError("all DataFrames must have a unique index")

        self.data = data
        self.params = params or {}

        self.signals = None
        self.positions = None
        
        # Extract asset names and create unified index
        self.assets = list(data.keys())
        self.unified_index = self._create_unified_index()

    def _create_unified_index(self):
        """Create a unified index from all asset data."""
        if not self.data:
            return pd.DatetimeIndex([])
        
        # Find the common date range across all assets
        all_indices = [df.index for df in self.data.values()]
        if not all_indices:
            return pd.DatetimeIndex([])
        
        # Start with the first asset's index
        unified = all_indices[0]
        
        # Find intersection with other assets
        for idx in all_indices[1:]:
            unified = unified.intersection(idx)
        
        return unified.sort_values()

    # --- Methods to be overridden by subclasses ---
    def generate_signals(self):
        """Generate trading signals. Must be implemented by subclasses."""
        raise NotImplementedError

    def generate_positions(self):
        """Generate position sizes. Must be implemented by subclasses."""
        raise NotImplementedError

class RiskManager:
    """
    Modular Risk Manager - No risk management by default.
    
    Users can add specific risk controls as needed:
    - risk_manager.add_sltp(stop_loss=0.05, take_profit=0.10)
    - risk_manager.add_position_limits(max_position_pct=0.20)
    - risk_manager.add_var_limits(var_limit=0.02)
    - risk_manager.add_correlation_limits(max_correlation=0.7)
    - risk_manager.add_sector_limits(max_sector_exposure=0.4)
    - risk_manager.add_volatility_targeting(target_vol=0.15)
    - risk_manager.add_drawdown_protection(max_drawdown=0.25)
    """
    
    def __init__(self):
        """Initialize with no risk management enabled."""
        # Risk management flags
        self.sltp_enabled = False
        self.position_limits_enabled = False
        self.var_limits_enabled = False
        self.correlation_limits_enabled = False
        self.sector_limits_enabled = False
        self.volatility_targeting_enabled = False
        self.drawdown_protection_enabled = False
        
        # Risk parameters (only set when enabled)
        self.stop_loss_pct = None
        self.take_profit_pct = None
        self.re_entry_delay = None
        
        self.max_position_pct = None
        self.max_portfolio_exposure = None
        
        self.var_limit = None
        self.var_confidence = None
        self.var_lookback = None
        
        self.max_correlation = None
        self.correlation_lookback = None
        
        self.max_sector_exposure = None
        self.sector_mapping = None
        
        self.target_volatility = None
        self.vol_lookback = None
        
        self.max_drawdown = None
        
        self.use_dynamic_sizing = False
        
        # Risk tracking
        self.track_risk_metrics = True
        self.risk_history = []
        
        # Re-entry tracking
        self.re_entry_restricted = {}  # asset -> exit_timestamp
        self.exit_reasons = {}  # asset -> exit reason
        
        # Risk metrics cache
        self._var_cache = {}
        self._correlation_cache = {}
        self._volatility_cache = {}
        
        # Peak equity for drawdown tracking
        self.peak_equity = 0.0
    
    def add_sltp(self, stop_loss_pct: float, take_profit_pct: float, re_entry_delay: int = 5):
        """
        Add stop-loss and take-profit controls.
        
        Args:
            stop_loss_pct: Stop-loss percentage (e.g., 0.05 for 5%)
            take_profit_pct: Take-profit percentage (e.g., 0.10 for 10%)
            re_entry_delay: Number of periods to wait before re-entry
        """
        if stop_loss_pct <= 0 or stop_loss_pct > 1.0:
            raise ValueError("stop_loss_pct must be between 0 and 1.0")
        if take_profit_pct <= 0 or take_profit_pct > 1.0:
            raise ValueError("take_profit_pct must be between 0 and 1.0")
        if re_entry_delay < 0:
            raise ValueError("re_entry_delay must be greater than 0")
        
        self.sltp_enabled = True
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.re_entry_delay = re_entry_delay
        
        print(f"✅ Stop-loss and take-profit enabled: SL {stop_loss_pct*100:.1f}%, TP {take_profit_pct*100:.1f}%, Re-entry delay: {re_entry_delay}")
    
    def add_position_limits(self, max_position_pct: float, max_portfolio_exposure: float):
        """
        Add position size and portfolio exposure limits.
        
        Args:
            max_position_pct: Maximum percentage of portfolio per asset (e.g., 0.20 for 20%)
            max_portfolio_exposure: Maximum total portfolio exposure (e.g., 0.80 for 80%)
        """
        if max_position_pct <= 0 or max_position_pct > 0.5:
            raise ValueError("max_position_pct must be between 0 and 0.5")
        if max_portfolio_exposure <= 0 or max_portfolio_exposure > 0.95:
            raise ValueError("max_portfolio_exposure must be between 0 and 0.95")
        
        self.position_limits_enabled = True
        self.max_position_pct = max_position_pct
        self.max_portfolio_exposure = max_portfolio_exposure
        
        print(f"✅ Position limits enabled: Max {max_position_pct*100:.0f}% per asset, Max {max_portfolio_exposure*100:.0f}% total exposure")
    
    def add_var_limits(self, var_limit: float, confidence: float = 0.95, lookback: int = 252):
        """
        Add Value at Risk (VaR) limits.
        
        Args:
            var_limit: Daily VaR limit as percentage (e.g., 0.02 for 2%)
            confidence: Confidence level for VaR calculation (e.g., 0.95 for 95%)
            lookback: Number of days for VaR calculation
        """
        if var_limit <= 0 or var_limit > 0.1:
            raise ValueError("var_limit must be between 0 and 0.1")
        if confidence <= 0 or confidence >= 1:
            raise ValueError("confidence must be between 0 and 1")
        if lookback < 30 or lookback > 1000:
            raise ValueError("lookback must be between 30 and 1000")
        
        self.var_limits_enabled = True
        self.var_limit = var_limit
        self.var_confidence = confidence
        self.var_lookback = lookback
        
        print(f"✅ VaR limits enabled: {var_limit*100:.1f}% daily VaR at {confidence*100:.0f}% confidence, {lookback} day lookback")
    
    def add_correlation_limits(self, max_correlation: float, lookback: int = 60):
        """
        Add correlation limits between positions.
        
        Args:
            max_correlation: Maximum allowed correlation (e.g., 0.7 for 70%)
            lookback: Number of days for correlation calculation
        """
        if max_correlation <= 0 or max_correlation >= 1:
            raise ValueError("max_correlation must be between 0 and 1")
        if lookback < 30 or lookback > 500:
            raise ValueError("lookback must be between 30 and 500")
        
        self.correlation_limits_enabled = True
        self.max_correlation = max_correlation
        self.correlation_lookback = lookback
        
        print(f"✅ Correlation limits enabled: Max {max_correlation*100:.0f}% correlation, {lookback} day lookback")
    
    def add_sector_limits(self, max_sector_exposure: float, sector_mapping: Dict[str, str] = None):
        """
        Add sector exposure limits.
        
        Args:
            max_sector_exposure: Maximum exposure per sector (e.g., 0.4 for 40%)
            sector_mapping: Dictionary mapping assets to sectors (optional)
        """
        if max_sector_exposure <= 0 or max_sector_exposure >= 1:
            raise ValueError("max_sector_exposure must be between 0 and 1")
        
        self.sector_limits_enabled = True
        self.max_sector_exposure = max_sector_exposure
        self.sector_mapping = sector_mapping or self._default_sector_mapping()
        
        print(f"✅ Sector limits enabled: Max {max_sector_exposure*100:.0f}% per sector")
    
    def add_volatility_targeting(self, target_volatility: float, lookback: int = 60, use_dynamic_sizing: bool = True):
        """
        Add volatility targeting and dynamic position sizing.
        
        Args:
            target_volatility: Annual volatility target (e.g., 0.15 for 15%)
            lookback: Number of days for volatility calculation
            use_dynamic_sizing: Whether to enable dynamic position sizing
        """
        if target_volatility <= 0 or target_volatility > 0.5:
            raise ValueError("target_volatility must be between 0 and 0.5")
        if lookback < 30 or lookback > 500:
            raise ValueError("lookback must be between 30 and 500")
        
        self.volatility_targeting_enabled = True
        self.target_volatility = target_volatility
        self.vol_lookback = lookback
        self.use_dynamic_sizing = use_dynamic_sizing
        
        print(f"✅ Volatility targeting enabled: {target_volatility*100:.1f}% annual target, {lookback} day lookback, Dynamic sizing: {use_dynamic_sizing}")
    
    def add_drawdown_protection(self, max_drawdown: float):
        """
        Add maximum drawdown protection.
        
        Args:
            max_drawdown: Maximum allowed drawdown (e.g., 0.25 for 25%)
        """
        if max_drawdown <= 0 or max_drawdown > 0.5:
            raise ValueError("max_drawdown must be between 0 and 0.5")
        
        self.drawdown_protection_enabled = True
        self.max_drawdown = max_drawdown
        
        print(f"✅ Drawdown protection enabled: Max {max_drawdown*100:.0f}% drawdown")
    
    def _default_sector_mapping(self) -> Dict[str, str]:
        """Default sector mapping for common assets."""
        return {
            # Crypto
            'BTCUSDT': 'Cryptocurrency', 'ETHUSDT': 'Cryptocurrency', 'BNBUSDT': 'Cryptocurrency',
            'ADAUSDT': 'Cryptocurrency', 'SOLUSDT': 'Cryptocurrency', 'DOTUSDT': 'Cryptocurrency',
            
            # Tech stocks
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
            'TSLA': 'Technology', 'NVDA': 'Technology', 'META': 'Technology',
            
            # Financial stocks
            'JPM': 'Financials', 'BAC': 'Financials', 'WFC': 'Financials', 'GS': 'Financials',
            
            # Energy
            'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy',
            
            # Healthcare
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare',
            
            # Consumer
            'KO': 'Consumer', 'PEP': 'Consumer', 'PG': 'Consumer', 'WMT': 'Consumer'
        }
    
    def is_risk_management_enabled(self) -> bool:
        """Check if any risk management is enabled."""
        return any([
            self.sltp_enabled,
            self.position_limits_enabled,
            self.var_limits_enabled,
            self.correlation_limits_enabled,
            self.sector_limits_enabled,
            self.volatility_targeting_enabled,
            self.drawdown_protection_enabled
        ])
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled risk management features."""
        features = []
        if self.sltp_enabled:
            features.append("Stop-loss & Take-profit")
        if self.position_limits_enabled:
            features.append("Position Limits")
        if self.var_limits_enabled:
            features.append("VaR Limits")
        if self.correlation_limits_enabled:
            features.append("Correlation Limits")
        if self.sector_limits_enabled:
            features.append("Sector Limits")
        if self.volatility_targeting_enabled:
            features.append("Volatility Targeting")
        if self.drawdown_protection_enabled:
            features.append("Drawdown Protection")
        
        return features if features else ["None"]
    
    def calculate_var(self, positions: Dict[str, float], returns_data: Dict[str, pd.Series], 
                     current_equity: float) -> float:
        """Calculate Value at Risk for the current portfolio."""
        if not self.var_limits_enabled or not positions or not returns_data:
            return 0.0
        
        try:
            # Calculate portfolio returns
            portfolio_returns = []
            for asset, pos in positions.items():
                if pos != 0 and asset in returns_data:
                    asset_returns = returns_data[asset].tail(self.var_lookback)
                    if len(asset_returns) > 0:
                        weighted_returns = asset_returns * (pos / current_equity)
                        portfolio_returns.append(weighted_returns)
            
            if not portfolio_returns:
                return 0.0
            
            # Combine all weighted returns
            if len(portfolio_returns) == 1:
                combined_returns = portfolio_returns[0]
            else:
                combined_returns = pd.concat(portfolio_returns, axis=1).sum(axis=1)
            
            # Calculate VaR
            var_percentile = (1 - self.var_confidence) * 100
            var_value = np.percentile(combined_returns, var_percentile)
            
            return abs(var_value)
            
        except Exception as e:
            warnings.warn(f"VaR calculation failed: {e}")
            return 0.0
    
    def check_correlation_limits(self, positions: Dict[str, float], returns_data: Dict[str, pd.Series]) -> List[Tuple[str, str, float]]:
        """Check if any position pairs violate correlation limits."""
        if not self.correlation_limits_enabled:
            return []
        
        violations = []
        
        try:
            # Get assets with non-zero positions
            active_assets = [asset for asset, pos in positions.items() if pos != 0]
            
            if len(active_assets) < 2:
                return violations
            
            # Calculate correlations between all pairs
            for i, asset1 in enumerate(active_assets):
                for asset2 in active_assets[i+1:]:
                    if asset1 in returns_data and asset2 in returns_data:
                        # Get recent returns
                        ret1 = returns_data[asset1].tail(self.correlation_lookback)
                        ret2 = returns_data[asset2].tail(self.correlation_lookback)
                        
                        # Align indices
                        common_idx = ret1.index.intersection(ret2.index)
                        if len(common_idx) >= 30:  # Need at least 30 data points
                            ret1_aligned = ret1.loc[common_idx]
                            ret2_aligned = ret2.loc[common_idx]
                            
                            # Calculate correlation
                            correlation = ret1_aligned.corr(ret2_aligned)
                            
                            if abs(correlation) > self.max_correlation:
                                violations.append((asset1, asset2, correlation))
            
            return violations
            
        except Exception as e:
            warnings.warn(f"Correlation check failed: {e}")
            return violations
    
    def check_sector_exposure(self, positions: Dict[str, float], current_equity: float) -> Dict[str, float]:
        """Check sector exposure limits."""
        if not self.sector_limits_enabled:
            return {}
        
        sector_exposures = {}
        
        try:
            for asset, pos in positions.items():
                if pos != 0:
                    sector = self.sector_mapping.get(asset, 'Unknown')
                    exposure_pct = abs(pos) / current_equity
                    
                    if sector in sector_exposures:
                        sector_exposures[sector] += exposure_pct
                    else:
                        sector_exposures[sector] = exposure_pct
            
            return sector_exposures
            
        except Exception as e:
            warnings.warn(f"Sector exposure check failed: {e}")
            return {}
    
    def calculate_volatility_scale(self, positions: Dict[str, float], returns_data: Dict[str, pd.Series]) -> float:
        """Calculate volatility scaling factor for position sizing."""
        if not self.volatility_targeting_enabled or not positions:
            return 1.0
        
        try:
            # Calculate current portfolio volatility
            portfolio_returns = []
            for asset, pos in positions.items():
                if pos != 0 and asset in returns_data:
                    asset_returns = returns_data[asset].tail(self.vol_lookback)
                    if len(asset_returns) > 0:
                        weighted_returns = asset_returns * (pos / sum(abs(p) for p in positions.values()))
                        portfolio_returns.append(weighted_returns)
            
            if not portfolio_returns:
                return 1.0
            
            # Combine returns and calculate volatility
            if len(portfolio_returns) == 1:
                combined_returns = portfolio_returns[0]
            else:
                combined_returns = pd.concat(portfolio_returns, axis=1).sum(axis=1)
            
            current_vol = combined_returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate scale factor
            if current_vol > 0:
                scale_factor = min(2.0, max(0.1, self.target_volatility / current_vol))
                return scale_factor
            
            return 1.0
            
        except Exception as e:
            warnings.warn(f"Volatility scaling calculation failed: {e}")
            return 1.0
    
    def check_drawdown_limit(self, current_equity: float) -> bool:
        """Check if current drawdown exceeds the maximum allowed."""
        if not self.drawdown_protection_enabled or self.peak_equity <= 0:
            return False
        
        current_drawdown = (current_equity - self.peak_equity) / self.peak_equity
        return current_drawdown < -self.max_drawdown
    
    def update_peak_equity(self, current_equity: float):
        """Update peak equity for drawdown tracking."""
        if self.drawdown_protection_enabled and current_equity > self.peak_equity:
            self.peak_equity = current_equity
    
    def apply_position_limits(self, asset: str, desired_position: float, 
                             current_equity: float, current_positions: dict,
                             returns_data: Dict[str, pd.Series] = None) -> float:
        """Apply comprehensive position limits including advanced risk controls."""
        if desired_position == 0:
            return desired_position
        
        # Start with basic position limits
        if self.position_limits_enabled:
            desired_position = self._apply_basic_position_limits(
                asset, desired_position, current_equity, current_positions
            )
        
        # Apply VaR limits if enabled
        if self.var_limits_enabled and returns_data:
            desired_position = self._apply_var_limits(
                asset, desired_position, current_equity, current_positions, returns_data
            )
        
        # Apply correlation limits if enabled
        if self.correlation_limits_enabled and returns_data:
            desired_position = self._apply_correlation_limits(
                asset, desired_position, current_equity, current_positions, returns_data
            )
        
        # Apply sector exposure limits if enabled
        if self.sector_limits_enabled:
            desired_position = self._apply_sector_limits(
                asset, desired_position, current_equity, current_positions
            )
        
        # Apply volatility scaling if enabled
        if self.volatility_targeting_enabled and returns_data:
            scale_factor = self.calculate_volatility_scale(current_positions, returns_data)
            desired_position *= scale_factor
        
        return desired_position
    
    def _apply_basic_position_limits(self, asset: str, desired_position: float,
                                   current_equity: float, current_positions: dict) -> float:
        """Apply basic position size and portfolio exposure limits."""
        # Calculate current portfolio exposure
        total_exposure = sum(abs(pos) for pos in current_positions.values())
        
        # Calculate maximum allowed position size based on portfolio percentage
        max_position_value = current_equity * self.max_position_pct
        max_position_size = max_position_value
        
        # Check portfolio exposure limits
        if desired_position > 0:  # Long position
            new_total_exposure = total_exposure + desired_position
            max_allowed_exposure = current_equity * self.max_portfolio_exposure
            
            if new_total_exposure > max_allowed_exposure:
                max_position_size = max(0, max_allowed_exposure - total_exposure)
                if max_position_size < desired_position:
                    print(f"⚠️  Position limited for {asset}: Portfolio exposure limit reached")
                    print(f"   Desired: {desired_position:.2f}, Allowed: {max_position_size:.2f}")
        
        elif desired_position < 0:  # Short position
            new_total_exposure = total_exposure + abs(desired_position)
            max_allowed_exposure = current_equity * self.max_portfolio_exposure
            
            if new_total_exposure > max_allowed_exposure:
                max_position_size = -max(0, max_allowed_exposure - total_exposure)
                if abs(max_position_size) < abs(desired_position):
                    print(f"⚠️  Position limited for {asset}: Portfolio exposure limit reached")
                    print(f"   Desired: {desired_position:.2f}, Allowed: {max_position_size:.2f}")
        
        # Apply the more restrictive limit
        if abs(desired_position) > abs(max_position_size):
            return max_position_size
        
        return desired_position
    
    def _apply_var_limits(self, asset: str, position: float, current_equity: float,
                         current_positions: dict, returns_data: Dict[str, pd.Series]) -> float:
        """Apply VaR-based position limits."""
        if position == 0:
            return 0.0
        
        # Test position by temporarily adding it
        test_positions = current_positions.copy()
        test_positions[asset] = position
        
        # Calculate VaR with test position
        test_var = self.calculate_var(test_positions, returns_data, current_equity)
        
        # If VaR exceeds limit, reduce position
        if test_var > self.var_limit:
            # Calculate reduction factor
            reduction_factor = self.var_limit / test_var
            new_position = position * reduction_factor
            
            print(f"⚠️  VaR limit exceeded for {asset}: {test_var:.4f} > {self.var_limit:.4f}")
            print(f"   Position reduced: {position:.2f} -> {new_position:.2f}")
            
            return new_position
        
        return position
    
    def _apply_correlation_limits(self, asset: str, position: float, current_equity: float,
                                current_positions: dict, returns_data: Dict[str, pd.Series]) -> float:
        """Apply correlation-based position limits."""
        if position == 0:
            return 0.0
        
        # Test position by temporarily adding it
        test_positions = current_positions.copy()
        test_positions[asset] = position
        
        # Check correlation violations
        violations = self.check_correlation_limits(test_positions, returns_data)
        
        if violations:
            # Find the highest correlation violation involving this asset
            max_corr = 0.0
            for asset1, asset2, corr in violations:
                if asset1 == asset or asset2 == asset:
                    max_corr = max(max_corr, abs(corr))
            
            if max_corr > self.max_correlation:
                # Reduce position based on correlation
                reduction_factor = self.max_correlation / max_corr
                new_position = position * reduction_factor
                
                print(f"⚠️  Correlation limit exceeded for {asset}: {max_corr:.3f} > {self.max_correlation:.3f}")
                print(f"   Position reduced: {position:.2f} -> {new_position:.2f}")
                
                return new_position
        
        return position
    
    def _apply_sector_limits(self, asset: str, position: float, current_equity: float,
                            current_positions: dict) -> float:
        """Apply sector exposure limits."""
        if position == 0:
            return 0.0
        
        # Test position by temporarily adding it
        test_positions = current_positions.copy()
        test_positions[asset] = position
        
        # Check sector exposures
        sector_exposures = self.check_sector_exposure(test_positions, current_equity)
        
        # Check if any sector exceeds limit
        for sector, exposure in sector_exposures.items():
            if exposure > self.max_sector_exposure:
                # Calculate how much we need to reduce
                excess = exposure - self.max_sector_exposure
                reduction_factor = 1 - (excess / exposure)
                
                # Apply reduction to this asset if it's in the violating sector
                if self.sector_mapping.get(asset) == sector:
                    new_position = position * reduction_factor
                    
                    print(f"⚠️  Sector exposure limit exceeded for {asset} ({sector}): {exposure:.3f} > {self.max_sector_exposure:.3f}")
                    print(f"   Position reduced: {position:.2f} -> {new_position:.2f}")
                    
                    return new_position
        
        return position
    
    def apply_sltp(self, asset: str, current_price: float, entry_price: float,
                   position_size: float, current_equity: float, 
                   current_idx: int) -> tuple:
        """Check stop-loss and take-profit conditions for an asset."""
        if not self.sltp_enabled:
            return False, current_equity
        
        updated_equity = current_equity
        
        # Check stop-loss
        if self.stop_loss_pct is not None:
            if current_price < entry_price * (1 - self.stop_loss_pct):
                realized_pnl = position_size * (current_price - entry_price)
                updated_equity += realized_pnl
                print(f"🛑 Stop-loss triggered for {asset}: Entry ${entry_price:.2f}, Current ${current_price:.2f}")
                print(f"   Realized PnL: ${realized_pnl:.2f}")
                
                # Mark asset as restricted for re-entry
                self.re_entry_restricted[asset] = current_idx
                self.exit_reasons[asset] = 'stop_loss'
                
                return True, updated_equity
        
        # Check take-profit
        if self.take_profit_pct is not None:
            if current_price > entry_price * (1 + self.take_profit_pct):
                realized_pnl = position_size * (current_price - entry_price)
                updated_equity += realized_pnl
                print(f"🎯 Take-profit triggered for {asset}: Entry ${entry_price:.2f}, Current ${current_price:.2f}")
                print(f"   Realized PnL: ${realized_pnl:.2f}")
                
                # Mark asset as restricted for re-entry
                self.re_entry_restricted[asset] = current_idx
                self.exit_reasons[asset] = 'take_profit'
                
                return True, updated_equity
        
        return False, updated_equity
    
    def can_re_enter(self, asset: str, current_idx: int) -> bool:
        """Check if an asset can re-enter based on time delay and exit reason."""
        if not self.sltp_enabled or asset not in self.re_entry_restricted:
            return True  # No restrictions
        
        exit_idx = self.re_entry_restricted[asset]
        time_since_exit = current_idx - exit_idx
        
        # Check if enough time has passed
        if time_since_exit >= self.re_entry_delay:
            # Clear the restriction
            del self.re_entry_restricted[asset]
            del self.exit_reasons[asset]
            return True
        
        return False
    
    def close_position(self, asset: str, strategy_positions: pd.DataFrame, current_idx: int):
        """Close a position temporarily for risk management."""
        if self.sltp_enabled:
            strategy_positions.iloc[current_idx, strategy_positions.columns.get_loc(asset)] = 0
    
    def get_risk_summary(self) -> dict:
        """Get a summary of current risk metrics."""
        summary = {
            'enabled_features': self.get_enabled_features(),
            'total_risk_events': len(self.risk_history),
            'peak_equity': self.peak_equity
        }
        
        # Add specific metrics based on enabled features
        if self.sltp_enabled:
            summary.update({
                'stop_loss_pct': self.stop_loss_pct,
                'take_profit_pct': self.take_profit_pct,
                're_entry_delay': self.re_entry_delay
            })
        
        if self.position_limits_enabled:
            summary.update({
                'max_position_pct': self.max_position_pct,
                'max_portfolio_exposure': self.max_portfolio_exposure
            })
        
        if self.var_limits_enabled:
            summary.update({
                'var_limit': self.var_limit,
                'var_confidence': self.var_confidence,
                'var_lookback': self.var_lookback
            })
        
        if self.correlation_limits_enabled:
            summary.update({
                'max_correlation': self.max_correlation,
                'correlation_lookback': self.correlation_lookback
            })
        
        if self.sector_limits_enabled:
            summary.update({
                'max_sector_exposure': self.max_sector_exposure
            })
        
        if self.volatility_targeting_enabled:
            summary.update({
                'target_volatility': self.target_volatility,
                'vol_lookback': self.vol_lookback,
                'use_dynamic_sizing': self.use_dynamic_sizing
            })
        
        if self.drawdown_protection_enabled:
            summary.update({
                'max_drawdown': self.max_drawdown
            })
        
        return summary
    
    def log_risk_event(self, event_type: str, asset: str, details: dict):
        """Log risk management events for analysis."""
        if self.track_risk_metrics:
            event = {
                'timestamp': pd.Timestamp.now(),
                'event_type': event_type,
                'asset': asset,
                'details': details
            }
            self.risk_history.append(event)
    
    def get_risk_history(self) -> List[dict]:
        """Get the history of risk management events."""
        return self.risk_history.copy()

class Backtester:
    """Handles backtest execution and PnL calculation with optional risk management."""
    
    def __init__(self, strategy: Strategy, risk_manager: RiskManager = None, params: dict = {}):
        if not isinstance(strategy, Strategy):
            raise TypeError("strategy must be a Strategy instance")
        
        if risk_manager is not None and not isinstance(risk_manager, RiskManager):
            raise TypeError("risk_manager must be a RiskManager instance or None")
        
        self.strategy = strategy
        self.risk_manager = risk_manager or RiskManager()  # Create default if none provided
        self.pnl = None
        self.metrics = {}
        self.init_cash = params.get('init_cash', 1e6)
        self.risk_free_rate = params.get('risk_free_rate', 0.0)
        
        # Risk tracking
        self.risk_events = []

    def _prepare_returns_data(self) -> Dict[str, pd.Series]:
        """Prepare returns data for risk calculations."""
        returns_data = {}
        
        try:
            for asset, asset_data in self.strategy.data.items():
                if 'Close' in asset_data.columns:
                    # Calculate returns from close prices
                    close_prices = asset_data['Close']
                    returns = close_prices.pct_change().dropna()
                    returns_data[asset] = returns
                else:
                    # If no Close column, try to use the data directly
                    if len(asset_data.columns) == 1:
                        prices = asset_data.iloc[:, 0]
                        returns = prices.pct_change().dropna()
                        returns_data[asset] = returns
                    else:
                        # Multiple columns, assume first is price
                        prices = asset_data.iloc[:, 0]
                        returns = prices.pct_change().dropna()
                        returns_data[asset] = returns
            
            return returns_data
            
        except Exception as e:
            warnings.warn(f"Failed to prepare returns data: {e}")
            return {}

    def run(self):
        """Execute the backtest using the strategy's signals and positions with optional risk management."""
        
        if self.strategy.signals is None:
            self.strategy.generate_signals()
        
        if self.strategy.positions is None:
            self.strategy.generate_positions()
        
        if self.strategy.positions is None:
            raise RuntimeError("Failed to generate positions. Check strategy implementation.")

        # Prepare returns data for risk calculations (only if risk management is enabled)
        returns_data = {}
        if self.risk_manager.is_risk_management_enabled():
            returns_data = self._prepare_returns_data()
        
        # Setup PnL DataFrame
        idx = self.strategy.unified_index
        self.pnl = pd.DataFrame(index=idx, columns=["equity", "pnl", "returns"], dtype=float)

        # Initialize
        self.pnl.loc[idx[0], "equity"] = self.init_cash
        self.pnl.loc[idx[0], "pnl"] = 0.0
        self.pnl.loc[idx[0], "returns"] = 0.0

        # Get asset names from positions
        assets = self.strategy.positions.columns.tolist()
        
        # Initialize entry tracking
        entry_prices = {}
        
        # Loop through each timestamp for proper position tracking
        for i, t in enumerate(idx):
            current_equity = self.pnl.loc[t, "equity"]
            daily_pnl = 0.0
            
            # Update peak equity for drawdown tracking
            self.risk_manager.update_peak_equity(current_equity)
            
            # Check drawdown limit
            if self.risk_manager.check_drawdown_limit(current_equity):
                print(f"🛑 Maximum drawdown limit exceeded: {((current_equity - self.risk_manager.peak_equity) / self.risk_manager.peak_equity) * 100:.2f}%")
                # Close all positions
                for asset in assets:
                    if self.strategy.positions.loc[t, asset] != 0:
                        self.strategy.positions.loc[t, asset] = 0
                        if asset in entry_prices:
                            del entry_prices[asset]
                
                # Log risk event
                self.risk_manager.log_risk_event(
                    'drawdown_limit', 'portfolio', 
                    {'current_equity': current_equity, 'peak_equity': self.risk_manager.peak_equity}
                )
                continue
            
            # Check for new positions or position changes
            for asset in assets:
                current_position = self.strategy.positions.loc[t, asset]
                previous_position = self.strategy.positions.iloc[i-1][asset] if i > 0 else 0
                
                # Check if we can re-enter this asset (if it was previously restricted)
                if current_position != 0 and previous_position == 0:
                    # Check re-entry restrictions
                    if not self.risk_manager.can_re_enter(asset, i):
                        # Re-entry not allowed yet, keep position at 0
                        self.strategy.positions.loc[t, asset] = 0
                        current_position = 0
                        continue
                    
                    # Apply comprehensive position limits before entering position
                    current_positions_dict = {a: self.strategy.positions.loc[t, a] for a in assets}
                    limited_position = self.risk_manager.apply_position_limits(
                        asset, current_position, current_equity, current_positions_dict, returns_data
                    )
                    
                    # Update position with limited size
                    self.strategy.positions.loc[t, asset] = limited_position
                    current_position = limited_position
                    
                    # Get current price for this asset
                    if asset in self.strategy.data:
                        asset_data = self.strategy.data[asset]
                        if 'Close' in asset_data.columns:
                            current_price = asset_data.loc[t, 'Close']
                        else:
                            current_price = asset_data.loc[t, asset_data.columns[0]]
                        
                        entry_prices[asset] = current_price
                        
                        # Log position entry
                        self.risk_manager.log_risk_event(
                            'position_entry', asset,
                            {'position': limited_position, 'price': current_price, 'equity': current_equity}
                        )
                
                # Position closed by strategy
                elif current_position == 0 and previous_position != 0:
                    if asset in entry_prices:
                        del entry_prices[asset]
                        # Log position exit
                        self.risk_manager.log_risk_event(
                            'position_exit', asset,
                            {'previous_position': previous_position, 'reason': 'strategy'}
                        )
                
                # Position size changed (e.g., from long to short)
                elif current_position != previous_position and previous_position != 0:
                    # Check if we can re-enter after previous risk management exit
                    if not self.risk_manager.can_re_enter(asset, i):
                        # Re-entry not allowed yet, keep previous position
                        self.strategy.positions.loc[t, asset] = previous_position
                        current_position = previous_position
                        continue
                    
                    # Apply comprehensive position limits before changing position
                    current_positions_dict = {a: self.strategy.positions.loc[t, a] for a in assets}
                    limited_position = self.risk_manager.apply_position_limits(
                        asset, current_position, current_equity, current_positions_dict, returns_data
                    )
                    
                    # Update position with limited size
                    self.strategy.positions.loc[t, asset] = limited_position
                    current_position = limited_position
                    
                    # Get current price
                    if asset in self.strategy.data:
                        asset_data = self.strategy.data[asset]
                        if 'Close' in asset_data.columns:
                            current_price = asset_data.loc[t, 'Close']
                        else:
                            current_price = asset_data.loc[t, asset_data.columns[0]]
                        
                        entry_prices[asset] = current_price
                        
                        # Log position change
                        self.risk_manager.log_risk_event(
                            'position_change', asset,
                            {'from': previous_position, 'to': limited_position, 'price': current_price}
                        )
            
            # Apply risk management rules (stop-loss, take-profit)
            if self.risk_manager.sltp_enabled:
                for asset in list(entry_prices.keys()):
                    if asset in self.strategy.data:
                        asset_data = self.strategy.data[asset]
                        if 'Close' in asset_data.columns:
                            current_price = asset_data.loc[t, 'Close']
                        else:
                            current_price = asset_data.loc[t, asset_data.columns[0]]
                        
                        entry_price = entry_prices[asset]
                        position_size = self.strategy.positions.loc[t, asset]
                        
                        # Check risk conditions using RiskManager
                        should_close, updated_equity = self.risk_manager.apply_sltp(
                            asset, current_price, entry_price, position_size, current_equity, i
                        )
                        
                        if should_close:
                            # Update equity with realized PnL
                            current_equity = updated_equity
                            self.pnl.loc[t, "equity"] = current_equity
                            
                            # Close position and remove from tracking
                            self.risk_manager.close_position(asset, self.strategy.positions, i)
                            del entry_prices[asset]
                            
                            # Log risk event
                            self.risk_manager.log_risk_event(
                                'risk_exit', asset,
                                {'reason': self.risk_manager.exit_reasons.get(asset, 'unknown')}
                            )
                            continue
            
            # Calculate PnL for current positions
            for asset in assets:
                current_position = self.strategy.positions.loc[t, asset]
                if current_position != 0:  # Only calculate PnL for open positions
                    if asset in self.strategy.data:
                        asset_data = self.strategy.data[asset]
                        if 'Close' in asset_data.columns:
                            current_price = asset_data.loc[t, 'Close']
                            previous_price = asset_data.loc[idx[i-1], 'Close'] if i > 0 else current_price
                        else:
                            current_price = asset_data.loc[t, asset_data.columns[0]]
                            previous_price = asset_data.loc[idx[i-1], asset_data.columns[0]] if i > 0 else current_price
                        
                        asset_pnl = current_position * (current_price - previous_price)
                        daily_pnl += asset_pnl
            
            # Update PnL DataFrame
            self.pnl.loc[t, "pnl"] = daily_pnl
            if i > 0:
                self.pnl.loc[t, "equity"] = self.pnl.iloc[i-1]["equity"] + daily_pnl
            else:
                self.pnl.loc[t, "equity"] = self.init_cash + daily_pnl
            
            # Calculate returns
            if i > 0:
                self.pnl.loc[t, "returns"] = daily_pnl / self.pnl.iloc[i-1]["equity"]
            else:
                self.pnl.loc[t, "returns"] = 0.0

        return self.pnl
    
    def get_risk_summary(self) -> dict:
        """Get a comprehensive summary of risk metrics and events."""
        risk_summary = self.risk_manager.get_risk_summary()
        
        # Add backtest-specific risk metrics
        if self.pnl is not None:
            equity = self.pnl['equity']
            returns = self.pnl['returns']
            
            # Calculate additional risk metrics
            max_drawdown = (equity / equity.cummax() - 1).min()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            var_95 = np.percentile(returns, 5)  # 95% VaR
            
            risk_summary.update({
                'backtest_max_drawdown': max_drawdown,
                'backtest_volatility': volatility,
                'backtest_var_95': var_95,
                'final_equity': equity.iloc[-1] if len(equity) > 0 else 0,
                'peak_equity': self.risk_manager.peak_equity
            })
        
        return risk_summary
    
    def get_risk_events(self) -> List[dict]:
        """Get all risk management events that occurred during the backtest."""
        return self.risk_manager.get_risk_history()


class Reporter:
    """Handles visualization and reporting of backtest results."""
    
    def __init__(self, backtester: Backtester):
        if not isinstance(backtester, Backtester):
            raise TypeError("backtester must be a Backtester instance")
        
        self.backtester = backtester

    def evaluate(self, periods_per_year: int = 252):
        """Calculate performance metrics."""
        if self.backtester.pnl is None:
            raise RuntimeError("Backtest not run yet.")

        rets = self.backtester.pnl["returns"]
        excess = rets - self.backtester.risk_free_rate / periods_per_year

        mean_excess = excess.mean()
        vol = rets.std()
        sharpe = np.sqrt(periods_per_year) * mean_excess / vol if vol > 0 else np.nan

        downside = excess[excess < 0]
        dd_std = downside.std()
        sortino = np.sqrt(periods_per_year) * mean_excess / dd_std if dd_std > 0 else np.nan

        equity = self.backtester.pnl["equity"]
        roll_max = equity.cummax()
        dd = equity / roll_max - 1.0
        max_dd = dd.min()

        n_years = (equity.index[-1] - equity.index[0]).days / 365.25
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / n_years) - 1 if n_years > 0 else np.nan

        calmar = cagr / abs(max_dd) if max_dd < 0 else np.nan

        self.metrics = {
            "sharpe": sharpe,
            "sortino": sortino,
            "cagr": cagr,
            "max_drawdown": max_dd,
            "calmar": calmar,
            "volatility": vol * np.sqrt(periods_per_year),
        }
        return self.metrics

    def plot(self):
        """Create comprehensive visualization of the backtest results."""
        if self.backtester.pnl is None:
            raise RuntimeError("Backtest not run yet.")

        # Get asset names from positions
        assets = self.backtester.strategy.positions.columns.tolist()
        
        # Find the start date for plotting (first non-NaN signal value)
        start_date = None
        if self.backtester.strategy.signals is not None and assets:
            for asset in assets:
                if asset in self.backtester.strategy.signals:
                    asset_signals = self.backtester.strategy.signals[asset]
                    # Check any signal column for first valid value
                    for signal_col in asset_signals.columns:
                        first_valid_idx = asset_signals[signal_col].first_valid_index()
                        if first_valid_idx is not None:
                            if start_date is None or first_valid_idx < start_date:
                                start_date = first_valid_idx
                            break  # Found a valid signal, no need to check other columns for this asset
        
        # If no valid signals found, use the full data range
        if start_date is None:
            start_date = self.backtester.strategy.data[assets[0]].index[0] if assets else None
        
        # Figure 1: Asset Data with Signals and Volume
        # Create subplots: price (candlestick), signals, volume
        fig1 = sp.make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],  # 2:1:1 aspect ratio
            specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Add candlestick charts for all assets
        for asset in assets:
            asset_data = self.backtester.strategy.data[asset]
            # Filter data from start_date onwards
            filtered_data = asset_data[asset_data.index >= start_date]
            fig1.add_trace(
                go.Candlestick(
                    x=filtered_data.index,
                    open=filtered_data['Open'],
                    high=filtered_data['High'],
                    low=filtered_data['Low'],
                    close=filtered_data['Close'],
                    name=asset,
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    legendgroup='group1',
                    legendgrouptitle_text='Asset Prices'
                ),
                row=1, col=1
            )
            
            # Add volume bars on the candlestick chart (secondary y-axis)
            fig1.add_trace(
                go.Bar(
                    x=filtered_data.index,
                    y=filtered_data['Volume'],
                    name=asset,
                    marker_color='blue',
                    opacity=0.25,
                    legendgroup='group2',
                    legendgrouptitle_text='Volumes',
                    yaxis='y2',
                    hoverinfo='skip'  # Hide volume values on hover
                ),
                row=1, col=1,
                secondary_y=True
            )
        
            # Add moving average signals in the middle row
            if self.backtester.strategy.signals is not None and asset in self.backtester.strategy.signals:
                asset_signals = self.backtester.strategy.signals[asset]
                # Filter signals from start_date onwards
                filtered_signals = asset_signals[asset_signals.index >= start_date]
                
                # Loop through all signal columns and plot them
                for signal_col in filtered_signals.columns:
                    fig1.add_trace(
                        go.Scatter(
                            x=filtered_signals.index,
                            y=filtered_signals[signal_col],
                            mode='lines',
                            name=f'{asset} {signal_col}',
                            line=dict(width=1.5),
                            opacity=0.8,
                            legendgroup='group3',
                            legendgrouptitle_text='Signals'
                        ),
                        row=2, col=1
                    )
            
            # Add positions in the bottom row
            if asset in self.backtester.strategy.positions.columns:
                # Filter positions from start_date onwards
                filtered_positions = self.backtester.strategy.positions[self.backtester.strategy.positions.index >= start_date]
                fig1.add_trace(
                    go.Scatter(
                        x=filtered_positions.index,
                        y=filtered_positions[asset],
                        mode='lines',
                        name=asset,
                        line=dict(width=1.5),
                        legendgroup='group4',
                        legendgrouptitle_text='Positions'
                    ),
                    row=3, col=1
                )
        

        
        # Update layout for Figure 1
        fig1.update_layout(
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # Update y-axis labels
        fig1.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig1.update_yaxes(title_text="Volume", row=1, col=1, secondary_y=True)
        fig1.update_yaxes(title_text="Signals", row=2, col=1)
        fig1.update_yaxes(title_text="Position Size", row=3, col=1)
        fig1.update_xaxes(title_text="Date", row=3, col=1)
        
        fig1.show()
        
        # Figure 2: Portfolio Performance
        fig2 = sp.make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Portfolio Equity', 'Daily PnL', 'Drawdown'),
            row_heights=[0.5, 0.25, 0.25]  # 2:1:1 aspect ratio
        )
        
        # Portfolio equity (normalized by initial value)
        equity = self.backtester.pnl["equity"]
        # Filter equity data from start_date onwards
        filtered_equity = equity[equity.index >= start_date]
        normalized_equity = filtered_equity / filtered_equity.iloc[0]  # Normalize by initial value
        fig2.add_trace(
            go.Scatter(
                x=normalized_equity.index,
                y=normalized_equity,
                mode='lines',
                line=dict(color='blue', width=2),
                name='Portfolio Equity (Normalized)',
                legendrank=3
            ),
            row=1, col=1
        )
        
        # Daily PnL bars
        pnl = self.backtester.pnl["pnl"]
        # Filter PnL data from start_date onwards
        filtered_pnl = pnl[pnl.index >= start_date]
        colors = ['green' if x >= 0 else 'red' for x in filtered_pnl]
        fig2.add_trace(
            go.Bar(
                x=filtered_pnl.index,
                y=filtered_pnl,
                marker_color=colors,
                opacity=0.7,
                name='PnL',
                legendrank=2
            ),
            row=2, col=1
        )
        
        # Add horizontal line at y=0 for PnL
        fig2.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=2, col=1)
        
        # Drawdown
        roll_max = filtered_equity.cummax()
        drawdown = (filtered_equity / roll_max - 1.0) * 100  # Convert to percentage
        fig2.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown,
                mode='lines',
                line=dict(color='red', width=1.5),
                fill='tonexty',
                fillcolor='rgba(255, 0, 0, 0.2)',
                name='Drawdown',
                legendrank=1
            ),
            row=3, col=1
        )
        
        # Add horizontal line at y=0 for drawdown
        fig2.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=3, col=1)
        
        # Update layout for Figure 2
        fig2.update_layout(
            height=800,
            showlegend=True
        )
        
        # Update y-axis labels
        fig2.update_yaxes(title_text="Portfolio Value (Normalized)", row=1, col=1)
        fig2.update_yaxes(title_text="PnL (USD)", row=2, col=1)
        fig2.update_yaxes(title_text="Drawdown (%)", row=3, col=1)
        fig2.update_xaxes(title_text="Date", row=3, col=1)
        
        fig2.show()

    def save(self, dir_path: str):
        """Save backtest results to files."""
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        
        if self.backtester.strategy.signals is not None:
            # Save each asset's signals separately
            for asset, signals_df in self.backtester.strategy.signals.items():
                signals_df.to_parquet(path / f"signals_{asset}.parquet")
        if self.backtester.strategy.positions is not None:
            self.backtester.strategy.positions.to_parquet(path / "positions.parquet")
        if self.backtester.pnl is not None:
            self.backtester.pnl.to_parquet(path / "pnl.parquet")

    def load(self, dir_path: str):
        """Load backtest results from files."""
        path = Path(dir_path)
        
        # Load signals (dictionary structure)
        signals_files = list(path.glob("signals_*.parquet"))
        if signals_files:
            self.backtester.strategy.signals = {}
            for file in signals_files:
                asset = file.stem.replace("signals_", "")
                self.backtester.strategy.signals[asset] = pd.read_parquet(file)
        
        if (path / "positions.parquet").exists():
            self.backtester.strategy.positions = pd.read_parquet(path / "positions.parquet")
        if (path / "pnl.parquet").exists():
            self.backtester.pnl = pd.read_parquet(path / "pnl.parquet")
