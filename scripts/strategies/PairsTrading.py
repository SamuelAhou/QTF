from ..src.strategy import Strategy
import pandas as pd
import numpy as np
import statsmodels.api as sm


class PairsTrading(Strategy):

    def __init__(self, name: str, data: pd.DataFrame, params: dict, init_cash: float= 100_000.0):
        super().__init__(name, data, params, init_cash)
        
        assert type(params['entry_threshold']) == float and type(params['exit_threshold']) == float
        self.entry_threshold = params['entry_threshold']
        self.exit_threshold = params['exit_threshold']

        assert type(params['order_size']) == float
        self.order_size = params['order_size']

        assert params['spread_type'] in ['zscore', 'ratio', 'log-difference', 'kalman']
        self.spread_type = params['spread_type']
        if self.spread_type == 'kalman':
            assert type(params['kalman_Q']) == float
            self.kalman_Q = params['kalman_Q']
            assert type(params['kalman_R']) == float
            self.kalman_R = params['kalman_R']

        self.assets = self.data.columns.levels[1]

    def generate_signals(self):
        closeA = self.data['Close'][self.assets[0]]
        closeB = self.data['Close'][self.assets[1]]

        # Filter NA
        filter_na = closeA.notna() & closeB.notna()
        closeA = closeA[filter_na]
        closeB = closeB[filter_na]

        # Compute the spread
        if self.spread_type == 'zscore':
            #TODO: Problem: Look-ahead bias if we use the whole data
            closeA_train, closeB_train = closeA[:int(len(closeA)*0.8)], closeB[:int(len(closeB)*0.8)]
            closeA_test, closeB_test = closeA[int(len(closeA)*0.8):], closeB[int(len(closeB)*0.8):]

            X = sm.tools.add_constant(closeB_train)
            model = sm.regression.linear_model.OLS(closeA_train, X)
            model = model.fit()
            hedge_ratio = model.params.iloc[1]

            spread = closeA - hedge_ratio*closeB
            spread = (spread - spread.rolling(20).mean())/spread.rolling(20).std()
        elif self.spread_type == 'ratio':
            spread = closeA/closeB
            spread = (spread - spread.rolling(20).mean())/spread.rolling(20).std()
        elif self.spread_type == 'log-difference':
            spread = np.log(closeA) - np.log(closeB)
            spread = (spread - spread.rolling(20).mean())/spread.rolling(20).std()
        elif self.spread_type == 'kalman':
            n = len(closeA)

            spread_prior = np.zeros(n)
            spread_post = np.zeros(n)

            beta_post = np.zeros(n)
            P_post = np.zeros(n)

            beta_prior = np.zeros(n)
            P_prior = np.zeros(n)

            for i in range(1, n):
                # Prediction Step
                beta_prior[i] = beta_post[i-1]
                P_prior[i] = P_post[i-1] + self.kalman_Q

                # Update Step
                spread_prior[i] = closeA.iloc[i] - beta_prior[i]*closeB.iloc[i]
                K = P_prior[i]*closeB.iloc[i] / (P_prior[i]*closeB.iloc[i]**2 + self.kalman_R)
                beta_post[i] = beta_prior[i] + K * spread_prior[i]
                P_post[i] = (1 - K*closeB.iloc[i]) * P_prior[i]

                # Update the spread
                spread_post[i] = closeA.iloc[i] - beta_post[i]*closeB.iloc[i]

            spread = pd.Series(spread_post, index=closeA.index)
            spread = (spread - spread.rolling(20).mean())/spread.rolling(20).std()
        else:
            raise ValueError('Invalid spread type')
        
        # TODO: Problem: Why minus sign needed ? Else does opposite of the what it is supposed to do
        spread = -spread
        self.signals['spread'] = spread


    def generate_positions(self):

        for i in range(1, len(self.signals)):
            # Asset 1 overperforms Asset 2 -> Short Asset 1, Long Asset 2
            if self.signals['spread'].iloc[i] > self.entry_threshold and self.signals['spread'].iloc[i-1] < self.entry_threshold:
                self.positions.loc[self.data.index[i], (self.assets[0], 'position')] -= self.order_size
                self.positions.loc[self.data.index[i], (self.assets[0], 'order_size')] = -self.order_size 
                self.positions.loc[self.data.index[i], (self.assets[1], 'position')] += self.order_size
                self.positions.loc[self.data.index[i], (self.assets[1], 'order_size')] = self.order_size
            # Asset 1 underperforms Asset 2 -> Long Asset 1, Short Asset 2
            elif self.signals['spread'].iloc[i] < -self.entry_threshold and self.signals['spread'].iloc[i-1] > -self.entry_threshold:
                self.positions.loc[self.data.index[i], (self.assets[0], 'position')] += self.order_size
                self.positions.loc[self.data.index[i], (self.assets[0], 'order_size')] = self.order_size
                self.positions.loc[self.data.index[i], (self.assets[1], 'position')] -= self.order_size
                self.positions.loc[self.data.index[i], (self.assets[1], 'order_size')] = -self.order_size
            # Spread reverts to the mean -> Close positions
            elif abs(self.signals['spread'].iloc[i]) < self.exit_threshold and abs(self.signals['spread'].iloc[i-1]) > self.exit_threshold:
                self.positions.loc[self.data.index[i], (self.assets[0], 'position')] = 0    
                self.positions.loc[self.data.index[i], (self.assets[0], 'order_size')] = 0
                self.positions.loc[self.data.index[i], (self.assets[1], 'position')] = 0
                self.positions.loc[self.data.index[i], (self.assets[1], 'order_size')] = 0

