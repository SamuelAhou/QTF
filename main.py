#!/usr/bin/env python3
"""
QTF - Quantitative Trading Framework
Main script for BTCUSDT SMA strategy backtesting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from src.DataProvider import DataManager
from strategies.SMA import SMAStrategy
from src.Backtester import Backtester, Reporter

if __name__ == "__main__":
    
    # Step 1: Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data_manager = DataManager()
    
    data = data_manager.get_data(
        provider='binance',
        symbols='BTCUSDT',
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )

    # Step 2: Define strategy
    
    # Initialize SMA strategy with 20-day and 50-day moving averages
    strategy = SMAStrategy(
        data=data,
        params={
            'short_window': 5,
            'long_window': 20,
            'order_size': 1.0,
        }
    )

    # Step 3: Run backtest
    backtester = Backtester(strategy)
    results = backtester.run()
    
    # Step 4: Print metrics
    reporter = Reporter(backtester)
    reporter.evaluate()
    reporter.plot()
    reporter.save('outputs')

