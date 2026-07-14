# Methodology

## Model A — EWMA + Normal VaR

Individual asset variances estimated via Exponentially Weighted Moving Average (RiskMetrics λ = 0.94):

$$σ_t^2=λ⋅σ_{t−1}^2+(1−λ)⋅r_{t−1}$$

Initial variance for 1 January 2020 is seeded from the sample variance over 2010–2019. VaR/ES computed from the standard normal distribution:


$$VaR = −Φ^{−1}(α)⋅σP⋅W$$

## Model B — CAPM + GARCH(1,1)

Portfolio volatility estimated indirectly via CAPM betas to the S&P 500 and DAX, combined with GARCH(1,1)-modelled index volatility. GARCH parameters (ω, α, β) estimated in volatility.py and fed into marketrisk_demo.ipynb:

$$σ_P^2=β_{SP500}^2σ_{SP500}^2+β_{DAX}^2σ_{DAX}^2+2ρβ_{SP500}β_{DAX}σ_{SP500}σ_{DAX}$$

Same normal VaR/ES formulae as Model A, applied to GARCH-based portfolio volatility. This factor-based approach mirrors how commercial risk systems map single-stock risk to systematic risk.

Model C — EWMA + Student-t

Same EWMA volatility engine as Model A, but VaR/ES drawn from a fitted Student-t distribution to capture fat tails. Degrees of freedom ν = 4.80 estimated by maximum likelihood on portfolio returns over the full 2010–2023 sample:

$$VaR=−σ_P⋅W⋅t^{−1}(α,ν)$$
$$ES=σ_P⋅W⋅(f_t(t^{−1}(α,ν)))/(α)⋅(ν+(t^{−1}(α,ν)))^2/(ν−1)$$ 

Motivated by the portfolio's excess kurtosis (≈ 8), well beyond what the normal distribution can capture.

## Correlation Scenarios

Each task is run under three correlation regimes, giving a 3×3 grid of model comparisons:

| Scenario | Assumption |
|---|---|
|1 — Zero Correlations | All pairwise correlations = 0; isolates idiosyncratic risk |
| 2 — Historical Correlations | Full 4×4 matrix from 2010–2019 returns | 
| 3 — Stress Correlations | All pairwise correlations = 0.95; diversification collapse under crisis|

## Backtesting — Kupiec Likelihood Ratio Test

VaR backtested year-by-year (2020–2023) using the Kupiec Proportion-of-Failures test. A breach occurs when actual daily portfolio return (GBP) falls below the negative VaR estimate:

$$LR=−2[(n−x)ln⁡(1−p)+xln⁡(p)−(n−x)ln⁡(1−p^{hat})−xln⁡(p^{hat})]∼χ^2(1)$$

where $$p$$=0.05, $$x$$ = breaches$$, $$n$$ = trading days, $$p^{hat}=x/n$$. Critical value at 5% test significance: 3.841 — note this is the significance level of the chi-squared test itself, a separate parameter from the 5% VaR target breach rate
$$(p)$$; the two happen to share a value here but aren't the same thing. Computed for all 9 model-scenario combinations per year in the Backtesting Analysis sheet.
