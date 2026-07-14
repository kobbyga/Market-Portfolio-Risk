import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from scipy.stats import norm, t

def plot_asset_prices(prices, assets=None):
    """
    Plot log asset price evolution over time.
    """
    if assets is None:
        assets = prices.columns

    fig, ax = plt.subplots(figsize=(12, 6))

    for asset in assets:
        ax.plot(prices.index, prices[asset], label=asset)

    ax.set_title("Asset Prices (Log)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
def plot_return_series(returns, asset):
    """
    Plot daily log returns for one asset.
    """

    fig, ax = plt.subplots(figsize=(12,4))

    ax.plot(returns.index, returns[asset])

    ax.set_title(f"{asset} Daily Log Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Return")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    
def plot_return_distribution(portfolio_returns):
    """
    Plot portfolio return distribution with
    Normal and Student-t fitted distributions.
    """

    data = portfolio_returns.dropna().values

    mu = np.mean(data)
    sigma = np.std(data)

    nu = len(data)

    x = np.linspace(
        data.min(),
        data.max(),
        500
    )

    normal_pdf = norm.pdf(
        x,
        mu,
        sigma
    )
    
    nu = 5  # estimated degrees of freedom

    student_pdf = t.pdf(
        x,
        df=nu,
        loc=mu,
        scale=sigma
    )

    fig, ax = plt.subplots(figsize = (12,5))

    ax.hist(
        data,
        bins=80,
        density=True,
        alpha=0.6,
        label="Portfolio Returns"
    )

    ax.plot(
        x,
        normal_pdf,
        label="Normal Distribution"
    )

    ax.plot(
        x,
        student_pdf,
        label="Student-t Distribution"
    )
    
    plt.title(
        "Portfolio Return Distribution"
    )

    ax.set_xlabel("Return")
    ax.set_ylabel("Density")

    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    plt.show()
    
def plot_ewma_volatility(returns, ewma_vols, asset):
    """
    Plot absolute returns with EWMA volatility.
    """

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(
        returns.index,
        returns[asset].abs(),
        alpha=0.5,
        label="Absolute Returns"
    )

    ax.plot(
        ewma_vols.index,
        ewma_vols[asset],
        linewidth=2,
        label="EWMA Volatility"
    )

    ax.set_title(f"{asset}: Returns and EWMA Volatility")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    plt.show()
    
def plot_garch_volatility(garch_vols, index_name):
    """
    Plot conditional GARCH volatility.
    """

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(
        garch_vols[index_name].index,
        garch_vols[index_name],
        linewidth=2
    )

    ax.set_title(f"{index_name} GARCH Conditional Volatility")
    ax.set_ylabel("Volatility")
    ax.grid(True)
    fig.tight_layout()
    plt.show()
    
def plot_correlation_heatmap(corr_matrix, title):
    """
    Plot correlation matrix heatmap.
    """

    plt.figure(figsize=(7, 6))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",       # Standard finance colour map
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"shrink": 0.85, "label": "Correlation"}
    )

    plt.title(title, fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.show()
    
def plot_portfolio_volatility(
    ewma_port_vol,
    garch_port_vol
):
    """
    Compare portfolio volatility estimates.
    """

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(
        ewma_port_vol.index,
        ewma_port_vol.values,
        label="EWMA"
    )

    ax.plot(
        garch_port_vol.index,
        garch_port_vol.values,
        label="CAPM/GARCH"
    )

    ax.set_title("Portfolio Volatility Comparison")

    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    plt.show()
    
def plot_var_backtest(
        var_results,
        model
):
    """
    Plot portfolio losses, VaR threshold and breaches.
    """
    
    scenarios = var_results["scenario"].unique()
    var_col = f"VaR_{model}"
    breach_col = f"breach_{model}"
    
    fig, axes = plt.subplots(
        len(scenarios),
        1,
        figsize=(12, 4 * len(scenarios)),
        sharex=True
    )
    
    for ax, scenario in zip(axes, scenarios):
        data = var_results[
            var_results["scenario"] == scenario
        ]
        
        ax.plot(
            data.index,
            data["loss_gbp"],
            label="Portfolio Loss"
        )
        
        ax.plot(
            data.index,
            data[var_col],
            label= "VaR (99%)"
        )
        
        breaches = data.loc[data[breach_col]]
        
        ax.scatter(
            breaches.index,
            breaches["loss_gbp"],
            color="red",
            label="Breach"
        )
        
        ax.set_title(f"{var_col}: {scenario}")
        ax.legend()
        ax.grid(True)
        
    plt.tight_layout()
    plt.show()
    
def plot_kupiec_results(summary):
    """
    Plot Kupiec test pass rates.
    """

    results = (
        summary
        .groupby(["scenario", "model"])
        ["passed"]
        .sum()
        .unstack()
    )

    fig, ax = plt.subplots(figsize=(12,5))

    results.plot(
        kind = "bar",
        ax = ax,
        color = ['red', 'green', 'blue']
    )
    
    ax.set_ylabel("Pass Rate")
    ax.set_title("Kupiec Test Pass Rate")
    ax.grid(True)
    fig.tight_layout()
    plt.show()
