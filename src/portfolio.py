import numpy as np
import pandas as pd

from config import (
    WEIGHTS,
    PORTFOLIO_VALUE,
    SCENARIOS,
    STRESS_RHO
)

def correlation_matrix(scenario, historical_returns):
   """
    Build a correlation matrix for a given scenario

    Args:
        scenario: One of {"zero", "historical", "stress"} indicating the correlation regime
        historical_returns: DataFrame of historical asset returns whose columns define
                            the set of assets for which the correlation matrix is built

    Returns:
        DataFrame: Correlation matrix corresponding to the selected scenario
    """
  
    cols = historical_returns.columns
  
    if scenario == "zero":
        return pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)
      
    elif scenario == "historical":
        return historical_returns.corr()
      
    elif scenario == "stress":
        arr = np.full((len(cols), len(cols)), STRESS_RHO)
        np.fill_diagonal(arr, 1.0)
        return pd.DataFrame(arr, index=cols, columns=cols)
      
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

def portfolio_volatility_assets(vols_today, corr, weights = WEIGHTS):
 """
    Compute portfolio volatility using asset-level volatilities and correlations

    Implements:
        sigma_P^2 = w' Σ w
    where:
        Σ_ij = sigma_i * sigma_j * rho_ij

    Args:
        vols_today: Dict mapping each ticker to its daily volatility
        corr: Correlation matrix (DataFrame) for the same tickers
        weights: Dict mapping each ticker to its portfolio weight

    Returns:
        float: Portfolio volatility (daily, decimal)
    """

    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])
    sig = np.array([vols_today[t] for t in tickers])
    rho = corr.loc[tickers, tickers].values
    cov = np.outer(sig, sig) * rho

    return float(np.sqrt(w @ cov @ w))

def estimate_capm_betas(portfolio_returns, index_returns):
    """
    Estimate CAPM-style betas via multiple regression:

        r_P = alpha + b_SP500 * r_SP500 + b_DAX * r_DAX + e

    Args:
        portfolio_returns: Series of portfolio returns
        index_returns: DataFrame containing SP500 and DAX returns

    Returns:
        dict: Estimated coefficients {"alpha", "SP500", "DAX"}
    """
  
    X = index_returns.copy()
    X.insert(0, "const", 1.0)
    y = portfolio_returns.reindex(X.index)
    beta_hat = np.linalg.lstsq(X.values, y.values, rcond=None)[0]
  
    return {"alpha": beta_hat[0], "SP500": beta_hat[1], "DAX": beta_hat[2]}
 
 
def portfolio_volatility_capm(betas, index_vols_today, rho_sp_dax):
    """
    Compute portfolio volatility using CAPM betas and index volatilities.

    Implements:
        sigma_P^2 = b_SP500^2 * sigma_SP500^2
                    + b_DAX^2 * sigma_DAX^2
                    + 2 * rho * b_SP500 * b_DAX * sigma_SP500 * sigma_DAX

    Args:
        betas: Dict containing CAPM betas {"SP500", "DAX"}.
        index_vols_today: Dict mapping index names to their daily volatilities.
        rho_sp_dax: Correlation between SP500 and DAX.

    Returns:
        float: Portfolio volatility (daily, decimal).
    """
    b1, b2 = betas["SP500"], betas["DAX"]
    s1, s2 = index_vols_today["SP500"], index_vols_today["DAX"]
    var_p = (b1 ** 2) * s1 ** 2 + (b2 ** 2) * s2 ** 2 + 2 * rho_sp_dax * b1 * b2 * s1 * s2
  
    return float(np.sqrt(var_p))
 
 
def portfolio_return_series(returns, weights = WEIGHTS):
    """
    Compute the portfolio return series as a weighted sum of asset returns.

    Args:
        returns: Dict mapping each ticker to its daily return Series.
        weights: Dict mapping each ticker to its portfolio weight.

    Returns:
        Series: Daily portfolio returns.
    """
    df = pd.DataFrame({t: returns[t] for t in weights})
  
    return (df * pd.Series(weights)).sum(axis=1)
