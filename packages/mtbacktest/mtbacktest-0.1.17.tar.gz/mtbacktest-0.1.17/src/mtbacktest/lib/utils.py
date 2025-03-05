from strategy import Strategy
from backtest import Backtest
from lib.preprocessing import df_to_dict, data_preprocess
import pandas as pd
import numpy as np

class DummyStrat():
    def __init__(self):
        self.trader = Strategy()
        self.account = self.trader.account
        def signal(dreturn):
            if dreturn > 2:
                return 1
            if dreturn < -2:
                return -1
            return 0
        self.signal_func= signal
    
    def iter(self, data):
        curr_signal = self.signal_func(data['dreturn_AAPL'])
        units = (self.account.buying_power // 2)/data['close_AAPL']
        curr_portfolio = self.account.get_curr_portfolio()
        open_positions = [pos for pos in curr_portfolio.positions if pos.symbol == 'AAPL' and pos.status == 'open']
        if curr_signal == 1:
            '''
            We long equity
            '''
            if len(open_positions) == 0:
                self.trader.create_position(data['timestamp_AAPL'], 'AAPL', units, data['close_AAPL'])
        
        elif curr_signal == -1:
            '''
            We short equity
            '''
            if len(open_positions) == 0:
                self.trader.create_position(data['timestamp_AAPL'], 'AAPL', -units, data['close_AAPL'])

        elif curr_signal == 0 and len(open_positions) > 0:
            '''
            We close position
            '''
            self.trader.close_position(data['timestamp_AAPL'], 'AAPL', data['close_AAPL'])
class MultiTickerDummyStrat():
    def __init__(self):
        self.trader = Strategy()
        self.account = self.trader.account
        def signal(dreturn):
            if dreturn > 2:
                return 1
            if dreturn < -2:
                return -1
            return 0
        self.signal_func= signal
    
    def iter(self, data, ticker):
        curr_signal = self.signal_func(data['dreturn_' + ticker])
        units = (self.account.buying_power // 3)/data['close_' + ticker]
        curr_portfolio = self.account.get_curr_portfolio()
        open_positions = [pos for pos in curr_portfolio.positions if pos.symbol == ticker and pos.status == 'open']
        if curr_signal == 1:
            '''
            We long equity
            '''
            if len(open_positions) == 0:
                self.trader.create_position(data['timestamp'], ticker, units, data['close_'+ticker])
        
        elif curr_signal == -1:
            '''
            We short equity
            '''
            if len(open_positions) == 0:
                self.trader.create_position(data['timestamp'], ticker, -units, data['close_'+ticker])

        elif curr_signal == 0 and len(open_positions) > 0:
            '''
            We close position
            '''
            self.trader.close_position(data['timestamp'], ticker, data['close_'+ticker])