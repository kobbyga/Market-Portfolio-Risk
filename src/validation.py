import numpy as np
import pandas as pd


def check_returns_data(returns):
    """
    Validate returns DataFrame.
    """

    results = {}

    results["shape"] = returns.shape
    results["missing_values"] = returns.isna().sum().sum()
    results["infinite_values"] = np.isinf(returns.values).sum()
    results["sorted_index"] = returns.index.is_monotonic_increasing

    return pd.Series(results)



def check_return_statistics(returns):
    """
    Check whether return magnitudes are reasonable.
    """

    stats = returns.describe().loc[
        ["mean", "std", "min", "max"]
    ]

    return stats



def check_weights(weights):
    """
    Validate portfolio weights.
    """

    total_weight = sum(weights.values())

    return {
        "total_weight": total_weight,
        "weights_sum_to_one": np.isclose(total_weight, 1)
    }



def check_ewma_volatility(ewma_vols):
    """
    Validate EWMA volatility output.
    """

    return pd.Series({
        "shape": ewma_vols.shape,
        "min_vol": ewma_vols.min().min(),
        "max_vol": ewma_vols.max().max(),
        "negative_vols": (ewma_vols < 0).sum().sum(),
        "has_nan": ewma_vols.isna().sum().sum()
    })



def check_var_es(var, es):
    """
    Validate VaR and Expected Shortfall.
    """

    return {
        "VaR_positive": var > 0,
        "ES_positive": es > 0,
        "ES_greater_than_VaR": es >= var
    }

def run_all_checks(returns, summary, ewma_vols, weights):

    print("\n=== Return Checks ===")
    print(check_returns_data(returns))

    print("\n=== Return Statistics ===")
    print(check_return_statistics(returns))

    print("\n=== Portfolio Weights ===")
    print(check_weights(weights))

    print("\n=== EWMA Checks ===")
    print(check_ewma_volatility(ewma_vols))

    print("\n=== Backtest Results ===")
    print(check_backtest(summary))
