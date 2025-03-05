import pandas as pd
import numpy as np

def data_preprocess(data:dict, **kwargs) -> tuple[list, pd.DataFrame]:
    """
    The data you gather should be parsed in as a dict object, in the format:
    e.g.
    {"AAPL": {pd.DataFrame}
    "TSLA": {pd.DataFrame}}
    The tickers for each data frame act as keys to the data
    """
    tickers = list(data.keys())
    dataframes = list(data.values())
    if len(dataframes) == 1:
        df = data[f'{tickers[0]}'][0].add_suffix('_'+tickers[0])
        try:
            df.rename(columns={'date_'+tickers[0]: 'timestamp'}, inplace=True)
        except:
            df.rename(columns={'timestamp_'+tickers[0]: 'timestamp'}, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.dropna()
    else:
        for df in dataframes:
            try:
                df.rename(columns={'date': 'timestamp'}, inplace=True)
            except:
                pass
    df = pd.merge(*dataframes, on='timestamp', how='outer', suffixes=['_'+s for s in tickers])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(df['timestamp'].dtype)
    return df.dropna()

def df_to_dict(dataframes:list[pd.DataFrame], tickers:list[str]) -> dict:
    if len(tickers) == 1:
        return {tickers[0]: dataframes}
    return {tickers[i]: dataframes[i] for i in range(len(dataframes))}

def adjust_price(df:pd.DataFrame) -> pd.DataFrame:
    """
    The data frame passed in must have
    'open', 'high', 'low', 'close', 'volume', 'adjusted_close'
    """
    adjust_factor = df['adjusted_close'] / df['close']
    df['close'] = df['adjusted_close']
    df['open'] = df['open'] * adjust_factor
    df['high'] = df['high'] * adjust_factor
    df['low'] = df['low'] * adjust_factor
    df['volume'] = df['volume'] * adjust_factor
    df.drop('adjusted_close', axis=1, inplace=True)
    return df
