import pandas as pd
import numpy as np
import yfinance as yf

from scripts.src.strategy import Strategy
from scripts.utils import *
from scripts.strategies.PairsTrading import PairsTrading
from scripts.strategies.SMA import SMAStrategy

if __name__ == '__main__':

    data = yf.download(['PEP', 'KO'], start='2010-01-01', end='2020-01-01', progress=False)

    # Define the parameters for the strategies
    params_pairs = {'entry_threshold': 2.0, 
                    'exit_threshold': 0.5, 
                    'order_size': 100.0, 
                    'spread_type': 'log-difference',
                    'kalman_Q': 0.1,
                    'kalman_R': 0.1}

    pairs_strategy = PairsTrading('PairsTrading(PEP-KO)-Ratio', data, params_pairs, 1000.0)

    pairs_strategy.run()
    pairs_strategy.plot('/Users/Samuel/Documents/Projects/Algorithmic-Trading/results/PairsTrading')
    
    print("Pairs Trading Strategy Results:")
    for key, value in pairs_strategy.metrics.items():
        print(f"{key}: {value}")
