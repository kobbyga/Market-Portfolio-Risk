import pandas as pd
import numpy as np

from src.config import (
    ASSETS,
    INDICES,
    FX,
    ALL_INSTRUMENTS,
    WEIGHTS,
    PORTFOLIO_VALUE, 
    SCENARIOS,
    STRESS_RHO,
    IN_SAMPLE_START,
    IN_SAMPLE_END,
    BACKTEST_START,
    BACKTEST_END,
    lam,
    alpha,
    backtest_sig
)

from src.data import (
    load_prices,
    split_sample
)

from src.volatility import (
    ewma_volatility,
    fit_garch,
    forecast_garch_vol
)

from src.portfolio import (
    correlation_matrix,
    portfolio_volatility_assets,
    estimate_capm_betas,
    portfolio_volatility_capm,
    portfolio_return_series
)

from src.var_models import (
    normal_var_es,
    student_t_var_es,
    fit_student_t_dof
)

from src.backtest import (
    kupiec_test
)

def run(returns):
    
    # Splitting data between in-sample and out-of-sample

    in_sample, backtest = split_sample(returns)

    port_ret_full = portfolio_return_series(returns)
    port_ret_in = portfolio_return_series(in_sample)
    port_ret_bt = portfolio_return_series(backtest)
    

    # Estimate model parameters

    # EWMA asset volatility

    seed_var = backtest[ASSETS].var()

    ewma_asset_vol = ewma_volatility(
        returns[ASSETS],
        lam=lam,
        seed_variance=seed_var
    )

    # Correlations

    asset_returns_in = in_sample[ASSETS]
    index_returns_in = in_sample[INDICES]

    asset_corr = asset_returns_in.corr()
    index_corr = index_returns_in.corr()

    # CAPM betas

    betas = estimate_capm_betas(
        port_ret_in,
        index_returns_in
    )

    # GARCH volatility

    garch_params = {}
    garch_vol = {}

    for idx in INDICES:

        params, cond_vol = fit_garch(
            returns[idx]
        )

        garch_params[idx] = params
        garch_vol[idx] = cond_vol

    # Student-t calibration

    ewma_port_in = ewma_volatility(
        port_ret_full.to_frame("Portfolio"),
        lam=lam,
        seed_variance=np.array(
            [np.var(port_ret_in.values)]
        )
    ).loc[port_ret_in.index]


    standardised = (
        port_ret_in.values /
        ewma_port_in["Portfolio"].values
    )

    nu = fit_student_t_dof(
        standardised
    )
    

    # Generate daily volatility forecasts

    ewma_port_vol = {}
    capm_port_vol = {}

    # Use base correlations for volatility comparison
    base_asset_corr = asset_corr

    for date in backtest.index:

        # EWMA portfolio volatility

        vols_today = {
            asset:
            ewma_asset_vol.loc[date, asset]

            for asset in ASSETS
        }

        ewma_port_vol[date] = (
            portfolio_volatility_assets(
                vols_today,
                base_asset_corr
            )
        )

        # CAPM/GARCH volatility
    
        index_vol_today = {
            idx:
            garch_vol[idx].loc[date]

            for idx in INDICES

            if date in garch_vol[idx].index
        }
            
        rho_sp_dax = index_corr.loc[
            "SPX",
            "DAX"
        ]

        capm_port_vol[date] = (
            portfolio_volatility_capm(
                betas,
                index_vol_today,
                rho_sp_dax
            )
        )

    ewma_port_vol = pd.Series(
        ewma_port_vol,
        name="EWMA"
    )

    capm_port_vol = pd.Series(
        capm_port_vol,
        name="CAPM_GARCH"
    )

    # Stress scenarios and VaR backtesting

    results = []

    years = sorted(
        set(backtest.index.year)
    )

    for scenario in SCENARIOS:

        stressed_asset_corr = correlation_matrix(
            scenario,
            asset_returns_in
        )

        stressed_index_corr = correlation_matrix(
            scenario,
            index_returns_in
        )

        rho_sp_dax = stressed_index_corr.loc[
            "SPX",
            "DAX"
        ]

        for date in backtest.index:

            # Asset VaR model

            vols_today = {

                asset:
                ewma_asset_vol.loc[date, asset]

                for asset in ASSETS
            }


            sigma_ewma = (
                portfolio_volatility_assets(
                    vols_today,
                    stressed_asset_corr
                )
            )

            # CAPM/GARCH VaR model

            idx_vol_today = {

                idx:
                garch_vol[idx].loc[date]

                for idx in INDICES

                if date in garch_vol[idx].index
            }

            sigma_capm = (
                portfolio_volatility_capm(
                    betas,
                    idx_vol_today,
                    rho_sp_dax
                )
            )

            # VaR calculations

            var_A, _ = normal_var_es(
                sigma_ewma,
                PORTFOLIO_VALUE,
                alpha
            )


            var_B, _ = normal_var_es(
                sigma_capm,
                PORTFOLIO_VALUE,
                alpha
            )


            var_C, _ = student_t_var_es(
                sigma_ewma,
                PORTFOLIO_VALUE,
                nu,
                alpha
            )

            loss = (
                -port_ret_bt.loc[date]
                *
                PORTFOLIO_VALUE
            )

            results.append({

                "date": date,
                "scenario": scenario,

                "loss_gbp": loss,

                "VaR_A": var_A,
                "VaR_B": var_B,
                "VaR_C": var_C,


                "breach_A":
                loss > var_A,

                "breach_B":
                loss > var_B,

                "breach_C":
                loss > var_C,

            })

    var_results = (
        pd.DataFrame(results)
        .set_index("date")
    )

    
    # Kupiec testing

    rows = []

    for task, col in [
        ("A","breach_A"),
        ("B","breach_B"),
        ("C","breach_C")
    ]:

        for scenario in SCENARIOS:

            for year in years:

                sub = var_results[
                    (var_results["scenario"] == scenario)
                    &
                    (var_results.index.year == year)
                ]

                x = int(
                    sub[col].sum()
                )

                n = len(sub)

                res = kupiec_test(
                    x,
                    n,
                    p=alpha
                )

                rows.append({

                    "model": task,
                    "scenario": scenario,
                    "year": year,

                    "n": n,
                    "breaches": x,

                    "breach_rate":
                    res.breach_rate,

                    "lr_stat":
                    res.lr_stat,

                    "passed":
                    res.passed
                })

    summary = pd.DataFrame(rows)
    

    # Return everything needed for analysis

    return {

        "summary": summary,

        "returns": returns,
        "in_sample": in_sample,
        "backtest": backtest,

        "portfolio_returns": port_ret_full,

        "ewma_asset_volatility":
            ewma_asset_vol,
        "ewma_portfolio_volatility":
            ewma_port_vol,
        "capm_portfolio_volatility":
            capm_port_vol,

        "garch_conditional_volatility":
            garch_vol,
        "garch_parameters":
            garch_params,

        "asset_corr":
            asset_corr,
        "index_corr":
            index_corr,
       
        "var_results":
            var_results
    }

def print_headline_table(summary, alpha):

    agg = summary.groupby(["model","scenario"]).agg(
        total_observations=("n", "sum"),
        total_breaches=("breaches", "sum"),
        avg_breach_rates=("breach_rate", "mean"),
        kupiec_passes=("passed", "sum"),
        n_tests=("passed", "count"),
    )

    agg["avg_breach_rate"] = (
        agg["avg_breach_rates"] * 100
    ).round(2).astype(str) + "%"


    agg["expected_breach_rate"] = f"{alpha * 100:.2f}%"


    agg["kupiec_pass_rate"] = (
        agg["kupiec_passes"].astype(str)
        +
        " / "
        +
        agg["n_tests"].astype(str)
    )


    print("\n=== VaR Backtest Summary ===")

    print(
        agg[
            [
                "total_observations",
                "total_breaches",
                "avg_breach_rate",
                "expected_breach_rate",
                "kupiec_pass_rate"
            ]
        ].to_string()
    )
