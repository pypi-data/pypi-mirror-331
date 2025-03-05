# Backtest

Custom backtest framework

installation

```python
pip install mtbacktest
```


To back test your strategy using this frame work we first define the strategy you want to run,

An example multi-ticker strategy (long short), the custom strategy class must contain a self.trader attribute for the framework to run

```python
from mtbacktest.strategy import Strategy
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
```

Then you can backtest the strategy like the following, if you choose to bring your own data

```python
from mtbacktest.backtest import Backtest
from mtbacktest.lib.preprocessing import df_to_dict, data_preprocess
import pandas as pd
import numpy as np

data = pd.read_json('test_data1.json')
data2 = pd.read_json('test_data2.json')

# Define your own custom features
data['dreturn'] = ((data['close'] - data['open'])/data['open']) * 100
data2['dreturn'] = ((data2['close'] - data2['open'])/data2['open']) * 100
data2 = data2.iloc[-100:]
data = data.iloc[-100:]

# standardise data for passing into the backtester
data = df_to_dict([data, data2], ['AAPL', 'TSLA']) # dataframe order should align with ticker list order
data = data_preprocess(data)

# Initiate backtest
bt = Backtest(MultiTickerDummyStrat, data, ['AAPL', 'TSLA'])
bt.run(verbose=1)
bt.plot()
```



The library also supports data fetching utilities, you can fetch data for stocks traded on US exchanges and LSE as well as crypto, note that when requesting for crypto data you should add "-USD" as suffix, for example, "BTC-USD", "SOL-USD", are accepted tickers.

An example of usage of the data collection utility is,

```python
from mtbacktest.data import Data
client = Data()
daily_data = client.get_daily_data(['AAPL', 'TSLA']) # for daily data
# The accepted intervals are 1m, 5m, 1h for intraday requests
intraday_data = client.get_intraday_data(['AAPL', 'TSLA'], interval='5m') # for intraday data
```

The data requested from the data module will be already standardised for parsing into the backtester, so no further processing is required, however, you will need to engineer your own feature if required, for future updates, we will implement a function to assist feature engineering.

Using the builtin data module, the work flow look something like this

```python
from mtbacktest.backtest import Backtest
import pandas as pd
import numpy as np
from mtbacktest.data import Data

client = Data()
data = client.get_daily_data(['AAPL', 'TSLA'])
# Initiate backtest
bt = Backtest(MultiTickerDummyStrat, data, ['AAPL', 'TSLA'])
bt.run(verbose=1)
bt.plot()
```

Then produce this graph 

![demo output](assets/demo.PNG)