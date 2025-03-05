import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

def simulate_GBM(mu=0.1, sigma=0.3, s0=100, periods=252, seed=None, M=1):
    """
    Simulate a random walk of price series based on geometric brownian motion
    s0: initial stock price
    mu: mean return
    sigma: volatility
    periods: number of periods
    """
    vec = []
    if seed is not None:
        np.random.seed(seed)
    for _ in range(M):
        dt = 1 / periods
        st = np.exp((mu - sigma ** 2 / 2) * dt + sigma * np.sqrt(dt) * np.random.normal(0, np.sqrt(dt), size=periods))
        st = s0 * st.cumprod(axis=0)
        vec.append(st)
    return vec

def plot_GBM(mu=0.1, sigma=0.3, s0=100, periods=252, seed=None, M=1):
    st = simulate_GBM(mu, sigma, s0, periods, seed, M)
    for series in st:
        plt.plot(series)
    plt.xlabel('Periods')
    plt.ylabel('Stock Price')
    plt.title('Simulation By Geometric Brownian Motion')
    plt.show()

