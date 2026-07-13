from __future__ import annotations
import numpy as np
import pandas as pd
from arch import arch_model

from config import (
    lam
)
 
def ewma_volatility(returns, lam, seed_variance = None):
  """
    Compute RiskMetrics EWMA volatility for all assets in a returns DataFrame

    sigma_t^2 = lam * sigma_{t-1}^2 + (1 - lam) * r_{t-1}^2

    Args:
        returns: DataFrame of daily log returns (columns = tickers)
        lam: EWMA decay factor (default 0.94)
        seed_variance: Optional Series of initial variances for each asset
                       If None, uses each column's sample variance

    Returns:
        ewma_vol: DataFrame of daily EWMA volatilities for each asset
  """
  r = returns.values                     
  T, N = r.shape

  # Seed variance per asset
  if seed_variance is None:
    seed_variance = returns.var()

  # Allocate variance matrix
  var = np.empty((T, N))
  var[0, :] = seed_variance.values

  # Vectorised EWMA recursion
  for t in range(1, T):
    var[t, :] = lam * var[t - 1, :] + (1 - lam) * (r[t - 1, :] ** 2)

  # Convert to volatility DataFrame
  ewma_vol = pd.DataFrame(
    np.sqrt(var),
    index=returns.index,
    columns=returns.columns
    )

  return ewma_vol

def fit_garch(returns):
    """
    Fits GARCH(1,1) to a return series via the `arch` package 
    
    Args:
        returns: DataFrame of daily log returns (columns = tickers)
 
    Returns:
        params: dict with omega, alpha, beta, mu (in daily return units, not %)
        cond_vol: fitted in-sample conditional volatility, daily decimal (not %)
    """
    # arch_model expects returns scaled to roughly O(1) for numerical stability
    scaled = returns * 100
    am = arch_model(scaled, mean="Constant", vol="GARCH", p=1, q=1, dist="normal")
    res = am.fit(disp="off")
 
    omega = res.params["omega"] / 100**2
    alpha = res.params["alpha[1]"]
    beta = res.params["beta[1]"]
    mu = res.params["mu"] / 100
 
    cond_vol = (res.conditional_volatility / 100)
    cond_vol.index = returns.index
 
    return {"omega": omega, "alpha": alpha, "beta": beta, "mu": mu}, cond_vol

def forecast_garch_vol(returns, params, cond_vol, horizon_index)
    """
    One-step-ahead GARCH(1,1) forecast over a horizon, using realised returns
    as they arrive (standard daily VaR setup).

    Args:
        returns: Series of realised daily log returns.
        params: dict with keys {"omega", "alpha", "beta"}.
        cond_vol: Series of in-sample conditional volatilities.
        horizon_index: DatetimeIndex of forecast dates.

    Returns:
        Series of forecast GARCH volatilities over the horizon.
    """
    # Combine in-sample + horizon dates
    all_index = cond_vol.index.union(horizon_index)
    all_returns = returns.reindex(all_index).fillna(0.0).values

    # Seed variance from last in-sample conditional vol
    prev_var = cond_vol.iloc[-1] ** 2

    # Prepare output array
    out = np.empty(len(horizon_index))

    # Map horizon dates to integer positions
    horizon_pos = all_index.get_indexer(horizon_index)

    omega = params["omega"]
    alpha = params["alpha"]
    beta = params["beta"]

    # Sequential recursion 
    for i, pos in enumerate(horizon_pos):
        prev_ret = all_returns[pos - 1]
        new_var = omega + alpha * prev_ret**2 + beta * prev_var
        out[i] = np.sqrt(new_var)
        prev_var = new_var

    return pd.Series(out, index=horizon_index, name="garch_vol")
