"""
Portfolio Optimization and Risk Analysis

This module provides functions to optimize a portfolio of stocks based on Sharpe Ratio and Value at Risk (VaR).
It allows for portfolio weight optimization and visualization of the efficient frontier.

Functions:
    - portfolio_sharpe(stocks_list, n=1000): Computes the optimal portfolio weights to maximize the Sharpe Ratio.
    - portfolio_var(stocks_list, n=1000): Computes the optimal portfolio weights to minimize Value at Risk (VaR).
    - plot_efficient_frontier(mean_variance_pairs, return_shp_max, vol_shp_max):
      Visualizes the efficient frontier using randomly generated portfolios.

Usage:
    weights, sharpe_ratio, return_shp, vol_shp = portfolio_sharpe(stocks_list)
    weights_var, min_var, return_var = portfolio_var(stocks_list)
    fig = plot_efficient_frontier(mean_variance_pairs, return_shp_max, vol_shp_max)
    fig.show()
"""

import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

def portfolio_sharpe(stocks_list, n=1000):
    """
    Computes the optimal portfolio allocation to maximize the Sharpe Ratio.

    Args:
        stocks_list (list): List of stock tickers.
        n (int, optional): Number of randomly generated portfolios. Defaults to 1000.

    Returns:
        tuple: (dict, float, float, float)
            - dict: Optimal portfolio weights.
            - float: Maximum Sharpe Ratio.
            - float: Expected return of the optimal portfolio.
            - float: Expected volatility of the optimal portfolio.
    """
    pricing_data = yf.Tickers(stocks_list).history(period='max')['Close'].dropna()
    pricing_data.index = pd.to_datetime(pricing_data.index).date
    
    port_returns = pricing_data.pct_change().dropna()
    mus = (1 + port_returns.mean()) ** 252 - 1
    cov = port_returns.cov() * 252
    
    mean_variance_pairs, weight_pairs = [], []
    
    for _ in range(n):
        weights = np.random.random(len(stocks_list))
        weights /= np.sum(weights)
        portfolio_E_Return = np.dot(weights, mus.loc[stocks_list])
        portfolio_E_Variance = np.dot(weights.T, np.dot(cov.loc[stocks_list, stocks_list], weights))
        weight_pairs.append(weights)
        mean_variance_pairs.append([portfolio_E_Return, portfolio_E_Variance])
    
    risk_free_rate = 0
    vol_vals = [v[1] for v in mean_variance_pairs]
    vol_min, vol_idx = min(vol_vals), vol_vals.index(min(vol_vals))
    return_vol_min = mean_variance_pairs[vol_idx][0]
    
    shp_vals = [(v[0] - risk_free_rate) / v[1] for v in mean_variance_pairs]
    shp_max, shp_idx = max(shp_vals), shp_vals.index(max(shp_vals))
    return_shp_max, vol_shp_max = mean_variance_pairs[shp_idx]
    
    weight_dict = {stocks_list[i]: round(weight_pairs[shp_idx][i], 2) for i in range(len(stocks_list))}
    
    return weight_dict, shp_max, return_shp_max, vol_shp_max

def portfolio_var(stocks_list, n=1000):
    """
    Computes the optimal portfolio allocation to minimize Value at Risk (VaR).

    Args:
        stocks_list (list): List of stock tickers.
        n (int, optional): Number of randomly generated portfolios. Defaults to 1000.

    Returns:
        tuple: (dict, float, float)
            - dict: Optimal portfolio weights.
            - float: Minimum Value at Risk (VaR).
            - float: Expected return of the minimum VaR portfolio.
    """
    pricing_data = yf.Tickers(stocks_list).history(period='max')['Close'].dropna()
    pricing_data.index = pd.to_datetime(pricing_data.index).date
    
    port_returns = pricing_data.pct_change().dropna()
    mus = (1 + port_returns.mean()) ** 252 - 1
    cov = port_returns.cov() * 252
    
    mean_VaR_pairs, weight_pairs = [], []
    
    for _ in range(n):
        weights = np.random.random(len(stocks_list))
        weights /= np.sum(weights)
        portfolio_return = np.dot(weights, mus.loc[stocks_list])
        portfolio_variance = np.dot(weights.T, np.dot(cov.loc[stocks_list, stocks_list], weights))
        portfolio_std_dev = np.sqrt(portfolio_variance)
        portfolio_VaR = norm.ppf(1 - 0.01, portfolio_return, portfolio_std_dev)
        weight_pairs.append(weights)
        mean_VaR_pairs.append([portfolio_return, portfolio_VaR])
    
    VaR_vals = [v[1] for v in mean_VaR_pairs]
    VaR_min, VaR_idx = min(VaR_vals), VaR_vals.index(min(VaR_vals))
    return_VaR_min = mean_VaR_pairs[VaR_idx][0]
    
    weight_dict = {stocks_list[i]: round(weight_pairs[VaR_idx][i], 2) for i in range(len(stocks_list))}
    
    return weight_dict, VaR_min, return_VaR_min

def plot_efficient_frontier(mean_variance_pairs, return_shp_max, vol_shp_max):
    """
    Plots the efficient frontier of randomly generated portfolios.

    Args:
        mean_variance_pairs (list): List of tuples (expected return, variance).
        return_shp_max (float): Expected return of the optimal Sharpe Ratio portfolio.
        vol_shp_max (float): Expected volatility of the optimal Sharpe Ratio portfolio.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object displaying the efficient frontier.
    """
    mean_variance_pairs = np.array(mean_variance_pairs)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.sqrt(mean_variance_pairs[:, 1]), y=mean_variance_pairs[:, 0], mode='markers',
                             marker=dict(color='blue', opacity=0.5), name='Random Portfolios'))
    fig.add_trace(go.Scatter(x=[vol_shp_max], y=[return_shp_max], mode='markers',
                             marker=dict(color='red', size=10), name='Optimal Sharpe Portfolio'))
    fig.update_layout(
        title='Efficient Frontier: Risk vs. Return',
        xaxis_title='Volatility (Risk)',
        yaxis_title='Expected Return'
    )
    
    return fig
