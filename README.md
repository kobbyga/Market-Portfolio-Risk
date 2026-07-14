# Market-Portfolio-Risk

A market risk project comparing three volatility-adaptive VaR models across three correlation regimes for a four-asset GBP-denominated equity portfolio (Nike, Citigroup, Commerzbank, Volkswagen), with full Kupiec backtesting conducted yearly over 2020–2023. Includes a CAPM two-factor model validated against GARCH(1,1) estimated index volatility.

## Features

- EWMA Volatility Calculation
- CAPM Beta Estimation
- GARCH (1,1) Parameter Estimation
- Normal and Student-t Distribution VaR
- Stress Testing Across Different Correlation Scenarios
- Kupiec LR Backtesting

## Model Framework

To estimate and validate daily portfolio Value-at-Risk (VaR) at 99% confidence level across three modelling frameworks and three correlation assumptions, using daily returns from 2020–2023 (backtesting period, 1,043 trading days) anchored on parameters estimated from 2010–2019 (in-sample period).

## Repository Structure

```
Market-Portfolio_Risk/
│
├── README.md                  # Project homepage
├── requirements.txt
├── .gitignore
│
├── data/
│   └── data.csv
├── docs/
│   ├── results.md
│   └── methodology.md
├── figures/
│   ├── asset_correlation.png
│   ├── asset_prices.png
│   ├── backtest_distribution.png
│   ├── garch_volatility.png
│   ├── index_correlation.png
│   ├── kupiec_pass_rate.png
│   ├── portfolio_distribution.png
│   ├── return_series.png
│   ├── returns_and_ewma.png
│   └── volatility_comparisons.png
├── notebook/
│   └── marketrisk_demo.ipynb
└──  src/
    ├── __init__.py
    ├── backtest.py
    ├── config.py
    ├── data.py
    ├── model_validation.py
    ├── portfolio.py
    ├── run_model.py
    ├── var_models.py
    ├── visualisations.py
    ├── volatlility.py
    └── visualisation.py
```

## How to run

1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/kobbyga/Market-Portfolio-Risk.git
   cd Market-Portfolio-Risk
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Launch Jupyter Notebook
- Open marketrisk_demo.ipynb
- Run all cells

## Portfolio and Parameters

| Parameter | Value |
|---|---|
| Assets | Nike (NKE), Citigroup (C), Commerzbank (CBK), Volkswagen (VOW) — all in GBP |
| Indices | S&P 500 (GBP), DAX (GBP) |
| Weights | Equal-weighted (25% each) |
| Portfolio Amount | £1,000,000 |
| VaR Confidence Level | 99% (α = 1%) |
| Backtesting Significance Level | 95% (α = 5%) |
| EWMA Lambda (λ) | 0.94 |
| In-sample period | January 2010 – December 2019 |
| Backtesting period | January 2020 – December 2023 |

## Results
Model A: EWMA Volatility + Normal VaR, Model B: CAPM + GARCH, Model C: EWMA Volatility + Student-t VaR

| Model | Scenario | Total Observations | Total Breaches | Average Breach Rate | Expected Breach Rate | Kupiec Pass Rate |
|---|---|---|---|---|---|---|                                                                                          
| A | historical | 1043 | 21 | 2.01% | 5.00% | 2 / 4 |
|   | stress | 1043 | 8 | 0.77% | 5.00% | 4 / 4 |
|   | zero | 1043 | 52 | 4.98% | 5.00% | 1 / 4 |
| B | historical | 1043 | 48 | 4.6% | 5.00% | 0 / 4 |
|   | stress | 1043 | 36 | 3.45% | 5.00% | 0 / 4 |
|   | zero | 1043 | 87 | 8.34% | 5.00% | 0 / 4 |
| C | historical | 1043 | 17 | 1.63% | 5.00% | 3 / 4 |
|   | stress | 1043 | 6 | 0.57% | 5.00% | 4 / 4 |
|   | zero | 1043 | 49 | 4.7% | 5.00% | 1 / 4 |

## Key Charts

- Backtest Distribution, where Portfolio Loss > VaR = Breach
  ![backtest_distribution](figures/backtest_distribution.png)

- Kupiec Test Pass Rate
  ![kupiec_pass_rate](figures/kupiec_pass_rate.png)


## Potential Extensions

- Historical simulation VaR as a non-parametric alternative, relaxing distributional assumptions
- Filtered Historical Simulation (FHS) combining GARCH-standardised residuals with empirical shocks
- GJR-GARCH / EGARCH to capture the leverage effect (negative returns raising volatility more than positive returns of equal size)
- Skewed Student-t distribution to capture both excess kurtosis and negative skew in equity returns
