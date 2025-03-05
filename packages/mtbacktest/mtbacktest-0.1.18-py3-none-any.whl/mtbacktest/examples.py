from strategy import Strategy
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
                self.trader.create_position(data['timestamp'], 'AAPL', units, data['close_AAPL'])
        
        elif curr_signal == -1:
            '''
            We short equity
            '''
            if len(open_positions) == 0:
                self.trader.create_position(data['timestamp'], 'AAPL', -units, data['close_AAPL'])

        elif curr_signal == 0 and len(open_positions) > 0:
            '''
            We close position
            '''
            self.trader.close_position(data['timestamp'], 'AAPL', data['close_AAPL'])
class MultiTickerDummyStrat():
    def __init__(self):
        self.trader = Strategy() # A virtual trader that you can submit orders and contains information about the portfolio it manages, you MUST DEFINE THIS AS 'self.trader'
        self.account = self.trader.account
        def signal(dreturn):
            """
            Define the signal such that if the current day return is greater than 2% we open long position,
            and vice versa, this is performed on all tickers passed into the iter function, which runs, 1 iteration
            of the algorithm
            """
            if dreturn > 2:
                return 1
            if dreturn < -2:
                return -1
            return 0
        self.signal_func= signal
    
    def iter(self, data, tickers):
        """
        You must define an iter() method that takes in data and specify what you want to do each iteration
        Note: you can design a different strategy for each ticker, for more customisable strategies.
        """

        for ticker in tickers:

            data['dreturn_' + ticker] = (data['close_' + ticker] - data['open_' + ticker]) / data['open_' + ticker] * 100
            curr_signal = self.signal_func(data['dreturn_' + ticker])
            units = (self.account.buying_power // 3)/data['close_' + ticker]
            curr_portfolio = self.account.portfolio_snapshots.iloc[-1]['portfolio']
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