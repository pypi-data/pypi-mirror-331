import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mtbacktest.simulation import simulate

def cagr(data:pd.Series, periods=252):
    return (data.iloc[-1] / data.iloc[0]) ** (periods / len(data)) - 1
def sharpe_ratio(data:pd.Series, risk_free_rate=0.004):
    returns = cagr(data)
    return (np.mean(returns) - risk_free_rate) / np.std(returns)

