import pandas as pd
class Position:
    def __init__(self, symbol:str, units:float, price:float) -> None:
        self.symbol = symbol
        self.units = units
        self.avg_price = price
        self.curr_price = price
        self.unrealized_pl = 0
        self.realized_pl = 0
        self.status = 'open'
        self.total_value = self.units * self.avg_price

    def _update_position(self, price:float) -> None:
        self.curr_price = price
        self.unrealized_pl = (self.curr_price - self.avg_price) * self.units
        self.total_value = self.units * price
    
    def _add_to_curr_position(self, units:float, price:float) -> None:
        new_units = units + self.units
        if new_units == 0:
            self._close_curr_position(price)
            return
        self.avg_price = (self.units * self.avg_price + units * price)/(self.units + units)
        self.units += units
        self.unrealized_pl = (price - self.avg_price) * self.units
        self.status='close' if self.units == 0 else 'open'

    def _close_curr_position(self, price:float, **kwargs) -> None:
        units = kwargs.get('close_units', self.units) # The amount of units you want to close
        self.units -= units
        self.realized_pl += (price - self.avg_price) * units
        self.avg_price = (self.units * self.avg_price) / self.units if self.units != 0 else 0
        self.status = 'closed' if self.units == 0 else 'open'
        self._update_position(price)
    
    def _show(self):
        print(f'symbol: {self.symbol}, units: {self.units}, avg_price: {self.avg_price}, curr_price: {self.curr_price}, unrealized_pl: {self.unrealized_pl}, realized_pl: {self.realized_pl}, status: {self.status}, tlv:{self.total_value}')

class Portfolio:

    def __init__(self, positions: set[Position], cash:float):
        self.positions = positions # Note: Positions can be empty
        self.cash = cash # Cash must be initiated by a upper level class method
        self.tlv = sum([pos.total_value for pos in self.positions]) + self.cash

    def _add_position(self, position: Position) -> None:
        dup_pos = [pos for pos in self.positions if pos.symbol == position.symbol]
        cost = position.units * position.avg_price
        self.cash -= cost
        if self.cash < 0:
            self.cash = 0
            raise ValueError('Insufficient cash to buy this position')
        if len(dup_pos) == 1: # There can only be at most 1 duplicate position
            dup = dup_pos[0] # we locate the duplicate position
            dup._add_to_curr_position(position.units, position.avg_price) # We modify the duplicate position

        else:
            self.positions.add(position)
        self.tlv = sum([pos.total_value for pos in self.positions]) + self.cash

    def _close_position(self, symbol:str, price:float, **kwargs) -> None:
        try:
            pos = [pos for pos in self.positions if pos.symbol == symbol][0]
        except IndexError:
            raise ValueError('Position does not exist in the portfolio')
        units = kwargs.get('close_units', pos.units)
        if pos.status == 'closed':
            raise ValueError('Position is already closed')
        close_size = units * price
        pos._close_curr_position(price, close_units=units)
        self.cash += close_size
        self.tlv = sum([pos.total_value for pos in self.positions]) + self.cash

    def _update_portfolio(self, prices:dict) -> None:
        for pos in self.positions:
            pos._update_position(prices[pos.symbol])
        self.tlv = sum([pos.total_value for pos in self.positions]) + self.cash

    def _show(self):
        for pos in self.positions:
            pos._show()
        print(f'Cash: {self.cash},\nTotal Value: {self.tlv},\n')
    
    def positions_to_df(self, timestamp):
        positions = []
        for pos in self.positions:
            positions.append({'timestamp': timestamp, 'symbol': pos.symbol, 'units': pos.units, 'avg_price': pos.avg_price, 'curr_price': pos.curr_price, 'unrealized_pl': pos.unrealized_pl, 'realized_pl': pos.realized_pl, 'status': pos.status, 'total_value': pos.total_value})
        return pd.DataFrame(positions)

class Account:

    def __init__(self, cash:float, **kwargs):
        self.cash = cash
        self.leverage = kwargs.get('leverage', 1)
        self.portfolio_snapshots = kwargs.get('portfolio_snapshots', pd.DataFrame(columns=['timestamp', 'portfolio']))
        self.buying_power = self.cash * self.leverage

    def _update_account(self, timestamp:float, portfolio:Portfolio) -> None:
        self.portfolio_snapshots.loc[timestamp] = portfolio
        self.cash = portfolio.cash
        self.buying_power = self.cash * self.leverage
    
    def get_curr_portfolio(self) -> Portfolio:
        return self.portfolio_snapshots.iloc[-1]['portfolio']
    
    def get_open_positions(self) -> list[Position]:
        return [pos for pos in self.portfolio_snapshots.iloc[-1]['portfolio'].positions if pos.status == 'open']

    def _show(self):
        print(f'cash: {self.cash}, leverage: {self.leverage}, buying_power: {self.buying_power}, snapshots: {len(self.portfolio_snapshots)}')
        curr_portfolio = self.portfolio_snapshots.iloc[-1]['portfolio']
        curr_time = self.portfolio_snapshots.index[-1]
        print(f'Timestamp: {curr_time}')
        curr_portfolio._show()
        print('\n')

class Strategy:

    def __init__(self, **kwargs):
        initial_capital = kwargs.get('initial_capital', 100000)
        self.account = Account(initial_capital)
        portfolio = Portfolio(set(), initial_capital)
        self.account._update_account(0, portfolio)

    def create_position(self, timestamp:float, symbol:str, units:float, price:float) -> None:
        position = Position(symbol, units, price)
        curr_portfolio = self.account.portfolio_snapshots.iloc[-1]['portfolio']
        try:
            curr_portfolio._add_position(position)
            self.account._update_account(timestamp, curr_portfolio)
        except ValueError as e:
            self.account._update_account(timestamp, curr_portfolio)
            print(e)


    def close_position(self, timestamp:float, symbol:str, price:float, **kwargs) -> None:
        curr_portfolio = self.account.portfolio_snapshots.iloc[-1]['portfolio']
        try:
            curr_portfolio._close_position(symbol, price, **kwargs)
            self.account._update_account(timestamp, curr_portfolio)

        except ValueError as e:
            self.account._update_account(timestamp, curr_portfolio)
            print(e)
    
    def update_positions(self, timestamp:float, prices:dict) -> None:
        curr_portfolio = self.account.portfolio_snapshots.iloc[-1]['portfolio']
        curr_portfolio._update_portfolio(prices)
        self.account._update_account(timestamp, curr_portfolio)

    def init(self):
        pass
    
    def iter(self, data:pd.DataFrame) -> None:
        """
        User should define this themselves by extending the strategy class,
        this is where the user define the logic of the trading algorithm,
        and this function would be called once each iteration of the backtest
        iterating through the rows of data fed into the backtest framework
        """
        pass