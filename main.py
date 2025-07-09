import pandas as pd
import numpy as np
import yfinance as yf
from polygon import RESTClient

from scripts.src.strategy import Strategy
from scripts.utils import *
from scripts.strategies.PairsTrading import PairsTrading
from scripts.strategies.SMA import SMAStrategy


def get_polygon_data(ticker, start_date, end_date, api_key):
    client = RESTClient(api_key)

    aggs = []
    for a in client.list_aggs(
        ticker,
        1,
        "day",  # daily resolution; change to "minute" for higher frequency
        start_date,
        end_date,
        limit=50000,
    ):
        aggs.append(a)

    df = pd.DataFrame([{
        "timestamp": pd.to_datetime(a.timestamp, unit='ms'),
        "open": a.open,
        "high": a.high,
        "low": a.low,
        "close": a.close,
        "volume": a.volume,
    } for a in aggs])
    df.set_index("timestamp", inplace=True)
    return df

if __name__ == '__main__':
    API_KEY = ""  # <-- Replace this with your actual Polygon API key
    
    pairs = [['AAPL', 'GOOG'], ['PEP', 'KO'], ['MSFT', 'AMZN']]

    for pair in pairs:

        tickers = [pair[0], pair[1]]

        dfs = []

        for ticker in tickers:
            df = get_polygon_data(ticker, "2023-01-01", "2025-01-01", API_KEY)

            df.columns = pd.MultiIndex.from_product([[col.title() for col in df.columns], [ticker]])
            dfs.append(df)

        data = pd.concat(dfs, axis=1).sort_index()

        # Strategy parameters
        params_pairs = {
            'entry_threshold': 2.0,
            'exit_threshold': 0.5,
            'order_size': 100.0,
            'spread_type': 'zscore',  # Options: 'zscore', 'ratio', 'log-difference', 'kalman'
            'zscore_window': 20,  # Only used if spread_type is 'z
            'kalman_Q': 0.1,
            'kalman_R': 0.1,
            'kalman_window': 20
        }

        #data = yf.download(['PEP', 'KO'], start='2010-01-01', end='2020-01-01', progress=False)

        strategy_name = '(' + '-'.join(pair) + ')' + '-' + params_pairs['spread_type']
        pairs_strategy = PairsTrading(strategy_name, data, params_pairs, 1000.0)

        pairs_strategy.run()
        pairs_strategy.plot('results/PairsTrading')
    
        print("Pairs Trading Strategy Results:")
        for key, value in pairs_strategy.metrics.items():
            print(f"{key}: {value}")
