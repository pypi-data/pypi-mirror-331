import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
class Backtest:
    def __init__(self, strategy, data, tickers):
        self.data = data
        self.strategy = strategy()
        self.tickers = tickers
        self.equity = []
        self.positions = pd.DataFrame()
        self.algo_ran = False

    def __prices_to_dict__(self, row):
        if type(self.tickers) == str:
            return {self.tickers: row[f'close_{self.tickers}']}
        return {self.tickers[i]: row[f'close_{self.tickers[i]}'] for i in range(len(self.tickers))}

    def run(self, verbose=0):
        if verbose == 1:
            print(f'Trading {len(self.data)} instances...')
            print(self.tickers)
        for index, row in self.data.iterrows():
            self.strategy.iter(row, self.tickers)
            prices = self.__prices_to_dict__(row)
            self.strategy.trader.update_positions(row[f'timestamp'], prices)
            curr_portfolio = self.strategy.trader.account.portfolio_snapshots.iloc[-1]['portfolio']
            if curr_portfolio.tlv < 1:
                self.equity.append(0)
                continue      
            self.equity.append(curr_portfolio.tlv)
            self.positions = pd.concat([self.positions, curr_portfolio.positions_to_df(row[f'timestamp'])], axis=0)
            if verbose == 2:
                self.strategy.trader.account._show()
        self.algo_ran = True

    def performance(self):
        """
        Evaluates the performance of the strategy on a few metrics compared with benchmark ()
        begining,
        end,
        duration,
        Total Return,
        Annualized Return,.
        Annualized Volatility,
        Sharpe Ratio,
        Max Drawdown,
        Expectation,
        win rate,
        """
        if not self.algo_ran:
            raise Exception("Algorithm has not been run yet")
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        begin = self.data['timestamp'].iloc[0]  
        end = self.data['timestamp'].iloc[-1]
        duration:pd.Timestamp = end - begin
        cum_returns = np.array(self.equity) / self.equity[0]
        total_returns = (self.equity[-1] / self.equity[0] - 1)
        days = duration.days
        annualized_return = ((self.equity[-1] / self.equity[0]) ** (365/days) - 1)
        annualized_volatility = np.std(cum_returns) * np.sqrt(252)
        sharpe_ratio = (annualized_return - 0.004) / annualized_volatility
        max_drawdown = np.min((np.minimum.accumulate(self.equity) - self.equity)/self.equity[0])
        expectation = (self.positions['realized_pl'].mean())
        win_rate = sum(self.positions['realized_pl'] > 0) / len(self.positions)
        
        temp = self.data
        temp['total_prices'] = temp.apply(lambda x: sum([x[f'close_{ticker}'] for ticker in self.tickers]), axis=1)
        total_prices = np.array(temp['total_prices'])
        cum_benchmark_returns = np.array(total_prices) / total_prices[0]
        benchmark_total_returns = total_prices[-1] / total_prices[0] - 1
        benchmark_annualized_return = ((total_prices[-1] / total_prices[0]) ** (365/days) - 1)
        benchmark_annualzied_volatility = (np.std(cum_benchmark_returns) * np.sqrt(252))
        benchmark_sharpe_ratio = (benchmark_annualized_return - 0.004) / benchmark_annualzied_volatility
        benchmark_max_drawdown = np.min((np.minimum.accumulate(total_prices) - total_prices)/total_prices[0])

        
        return pd.DataFrame({
            'begin': pd.Series([begin, begin]),
            'end': pd.Series([end, end]),
            'duration': pd.Series([duration, duration]),
            'Total Return': pd.Series([total_returns, benchmark_total_returns]),
            'Annualized Return': pd.Series([annualized_return, benchmark_annualized_return]),
            'Annualized Volatility': pd.Series([annualized_volatility, benchmark_annualzied_volatility]),
            'Sharpe Ratio': pd.Series([sharpe_ratio, benchmark_sharpe_ratio]),
            'Max Drawdown': pd.Series([max_drawdown, benchmark_max_drawdown]),
            'Expectation': pd.Series([expectation, None]),
            'Win Rate': pd.Series([win_rate, None])}).set_axis(['Strategy', 'Benchmark'], axis=0)
        
    
    def plot(self):
        if not self.algo_ran:
            raise Exception("Algorithm has not been run yet")
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)
        if type(self.tickers) == str:
            fig.add_trace(
                go.Scatter(x=self.data['timestamp'], y=self.data['close_' + self.tickers], mode='lines', name=f'{self.tickers} Prices'),
                row=1, col=1
            )
        else:
            for ticker in self.tickers:
                cum_return = (1 + (self.data['close_' + ticker] - self.data['open_' + ticker])/self.data['open_' + ticker]).cumprod()
                fig.add_trace(
                    go.Scatter(x=self.data['timestamp'], y=cum_return, mode='lines', name=f'{ticker} Cumulative Returns'),
                    row=1, col=1
                )

        fig.add_trace(
            go.Scatter(x=self.data[f'timestamp'], y=self.equity, mode='lines', name='Equity'),
            row=2, col=1
        )
        grouped = self.positions.groupby('symbol')
        for name, group in grouped:
            fig.add_trace(
                go.Scatter(x=group['timestamp'], y=group['units'], mode='lines', name=f'{name} units'),
                row=3, col=1
            )
        fig.show()