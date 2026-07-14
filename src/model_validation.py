import numpy as np
import pandas as pd

from src.config import (
    lam,
    backtest_sig
)

def check_returns_data(returns):
    """Validate returns DataFrame."""

    results = {
        "shape": returns.shape,
        "missing_values": returns.isna().sum().sum(),
        "infinite_values": np.isinf(returns.values).sum(),
        "sorted_index": returns.index.is_monotonic_increasing,
    }

    return pd.Series(results)



def check_return_statistics(returns):
    """Check whether return magnitudes are reasonable."""

    return returns.describe().loc[["mean", "std", "min", "max"]]



def check_weights(weights):
    """Validate portfolio weights."""

    total_weight = sum(weights.values())

    return {
        "total_weight": total_weight,
        "weights_sum_to_one": np.isclose(total_weight, 1.0),
    }



def check_ewma_volatility(ewma_vols):
    """Validate EWMA volatility output."""

    return pd.Series({
        "shape": ewma_vols.shape,
        "min_vol": ewma_vols.min().min(),
        "max_vol": ewma_vols.max().max(),
        "negative_vols": (ewma_vols < 0).sum().sum(),
        "nan_values": ewma_vols.isna().sum().sum(),
    })



def check_ewma_recursion(returns, ewma_vols, lam=lam):
    """Verify EWMA recursion relation."""

    if len(returns) < 2:
        return np.nan

    t = min(100, len(returns) - 1)

    lhs = ewma_vols.iloc[t] ** 2
    rhs = (
        lam * ewma_vols.iloc[t - 1] ** 2
        + (1 - lam) * returns.iloc[t - 1] ** 2
    )

    return (lhs - rhs).abs().max()



def check_garch_parameters(alpha, beta):
    """
    Validate GARCH(1,1) parameters.
    """

    persistence = alpha + beta

    return {
        "alpha": alpha,
        "beta": beta,
        "persistence": persistence,
        "stationary": persistence < 1,
    }



def compare_var_models(normal_var, t_var):
    """Compare normal and Student-t VaR outputs."""

    return {
        "t_var_greater_than_normal": t_var >= normal_var,
        "normal_var": normal_var,
        "t_var": t_var,
    }



def run_all_checks(
    returns,
    summary,
    ewma_vols,
    garch_alpha,
    garch_beta,
    weights,
    normal_var,
    t_var
):

    print("=== Return Checks ===")
    print(check_returns_data(returns))

    print("=== Return Statistics ===")
    print(check_return_statistics(returns))

    print("=== Portfolio Weights ===")
    print(check_weights(weights))

    print("=== EWMA Checks ===")
    print(check_ewma_volatility(ewma_vols))

    print("=== EWMA Recursion Error ===")
    print(check_ewma_recursion(returns, ewma_vols))

    print("=== GARCH Parameter Persistence ===")
    print(check_garch_parameters(garch_alpha, garch_beta))

    print("=== VaR Model Outputs ===")
    print(compare_var_models(normal_var, t_var))


