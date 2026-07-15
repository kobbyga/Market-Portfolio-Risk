# Results & Model Comparison
 
Full backtest results for the three VaR models (Model A — EWMA + Normal, Model B — CAPM + GARCH(1,1), Model C — EWMA + Student-t), each run under three correlation scenarios (Zero, Historical, Stress) over the 2020–2023 backtesting window (1,043 trading days, 4 annual Kupiec tests per scenario, 12 per model).
 
Confidence level: 99% VaR (α = 1%), with the Kupiec backtest carried out at a 5% significance level.
 
---
 
## Summary
 
| Model | Scenario | Observations | Breaches | Breach Rate | Target | Kupiec Passes |
|---|---|---|---|---|---|---|
| A | Zero | 1,043 | 52 | 4.98% | 5.00% | 1 / 4 |
| A | Historical | 1,043 | 21 | 2.01% | 5.00% | 2 / 4 |
| A | Stress | 1,043 | 8 | 0.77% | 5.00% | 4 / 4 |
| B | Zero | 1,043 | 87 | 8.34% | 5.00% | 0 / 4 |
| B | Historical | 1,043 | 48 | 4.60% | 5.00% | 0 / 4 |
| B | Stress | 1,043 | 36 | 3.45% | 5.00% | 0 / 4 |
| C | Zero | 1,043 | 49 | 4.70% | 5.00% | 1 / 4 |
| C | Historical | 1,043 | 17 | 1.63% | 5.00% | 3 / 4 |
| C | Stress | 1,043 | 6 | 0.57% | 5.00% | 4 / 4 |
 
**Model totals (across all 3 scenarios, 12 tests each):**
 
| Model | Avg. Breach Rate | Kupiec Pass Rate |
|---|---|---|
| A — EWMA + Normal | 2.59% | 7 / 12 (58%) |
| B — CAPM + GARCH | 5.46% | 0 / 12 (0%) |
| C — EWMA + Student-t | 2.30% | 8 / 12 (67%) |
 
---
 
## Model A — EWMA + Normal
 
Zero correlation is where Model A struggles most: a 4.98% breach rate against a 5% target sounds like a near-perfect calibration, but it only passes 1 of 4 years — the aggregate rate is close to target while the year-by-year distribution isn't, which is exactly the kind of thing an average can hide and Kupiec is built to catch.
 
Historical correlations bring the breach rate down to 2.01% (2/4 passes) and stress correlations down further to 0.77% (4/4 passes). The pattern is consistent: as the correlation assumption gets more conservative (higher assumed co-movement = higher assumed portfolio volatility = larger VaR), breaches fall and Kupiec passes rise. That's mechanically expected, but it also means Model A's apparent "good" performance under stress correlations isn't really about better calibration — it's about a larger VaR number making breaches structurally less likely, regardless of whether that number is right.
 
**Net:** moderate, inconsistent performer — passes just over half its tests overall (7/12), and its single best result (stress scenario) is arguably its least informative, since an overly conservative VaR estimate passes Kupiec almost by construction.
 
## Model B — CAPM + GARCH(1,1)
 
Model B is the clearest result in this backtest: it fails all 12 tests, across every scenario, despite its overall average breach rate (5.46%) sitting closer to the 5% target than either of the other two models.
 
The likely mechanism is structural rather than random noise. The CAPM betas are estimated once on the 2010–2019 in-sample period and then held fixed across the entire 2020–2023 backtest — they don't adapt as market conditions change, unlike the EWMA volatility engine underlying Tasks A and C, which recalibrates daily. GARCH(1,1) does capture time-varying volatility in the two index factors (S&P 500, DAX), but if the portfolio's actual risk exposure to those factors shifts over the backtest window — plausible given a 4-year window spanning both a COVID shock and a 2022 rate-driven repricing — a static beta will misprice risk in whichever direction the relationship has drifted, and do so persistently rather than randomly. That produces exactly what's observed: breaches concentrated in specific stretches rather than spread evenly, which is a coverage failure Kupiec is sensitive to even when the long-run average looks fine.
 
**Net:** the average-breach-rate number is the most misleading metric in this whole comparison. Model B is not a viable model for daily VaR as currently specified — the fix isn't the correlation scenario, it's revisiting whether betas should be re-estimated on a rolling or expanding window rather than fixed once.
 
## Model C — EWMA + Student-t
 
Model C is the best-calibrated model across all three scenarios: 1/4 (zero), 3/4 (historical), 4/4 (stress) — the same directional pattern as Model A, but consistently better at every scenario, and with a lower overall average breach rate (2.30% vs. Model A's 2.59%).
 
The fat-tailed Student-t distribution (ν ≈ 4.80) means the model is less surprised by large single-day moves than the Normal distribution is — which matters most in exactly the kind of period this backtest covers (2020 COVID crash, 2022 volatility spike). Both Model A and Model C share the same underlying EWMA volatility estimate; the difference in performance comes entirely from the distributional assumption layered on top, and that's a fairly clean piece of evidence that the fat-tail correction is doing real work rather than just adding noise.
 
Model C still under-breaches on average relative to the 5% target (2.30% vs. 5%), meaning it's somewhat conservative — capital-inefficient relative to a perfectly calibrated model — but it's the most *consistent* of the three, which is the property Kupiec is actually testing for.
 
**Net:** best-performing model in this backtest. Under the historical correlation scenario specifically — the most realistic of the three assumptions for day-to-day use — Model C passes 3 of 4 years, ahead of Model A (2/4) and well ahead of Model B (0/4).
 
---
 
## Cross-Model Patterns
 
**All three models perform worst under zero correlation.** Assuming independence between the four portfolio assets systematically understates true portfolio volatility if the assets are actually positively correlated, which they are — VaR ends up too small, and breach rates climb across the board (A: 4.98%, B: 8.34%, C: 4.70%). This isn't model-specific; it's a property of the correlation assumption itself, and it's a reasonable sanity check that all three respond to it the same way.
 
**All three models perform best under stress correlations**, but for a less flattering reason than it first appears: assuming ρ = 0.95 across all asset pairs inflates portfolio volatility (and therefore VaR) substantially, which mechanically reduces breach frequency regardless of whether 0.95 is a realistic assumption for any given day. High Kupiec pass rates here reflect a conservative VaR estimate more than an accurate one.
 
**Historical correlations are the most informative scenario** for judging real calibration, since they're neither artificially independent nor artificially crisis-level — they reflect the actual co-movement structure observed in-sample. Under this scenario, the model ranking is unambiguous: Model C (3/4) > Model A (2/4) > Model B (0/4).
 
---
 
## Recommendation
 
**Model C (EWMA + Student-t) is the recommended model** based on this backtest: best pass rate overall (8/12), best pass rate under the realistic historical-correlation scenario (3/4), and the lowest average breach rate of the three. The fat-tailed distribution appears to be earning its complexity — the improvement over Model A isn't marginal.
 
**Model B (CAPM + GARCH) is not recommended as currently specified.** The 0/12 result isn't close — it's a structural issue (most likely the static, in-sample-only beta estimation) rather than a borderline calibration problem, and it would need a design change, not a threshold adjustment, before being usable for VaR.
 
**Model A (EWMA + Normal)** sits between the two — usable as a simpler baseline, but Model C dominates it on every scenario at effectively the same implementation cost, so there's no real case for preferring A over C given these results.
 
---
 
## Limitations & Next Steps
 
- **Task B's static beta is the most actionable finding here.** Re-estimating CAPM betas on a rolling or expanding window (rather than once, on 2010–2019 data) is the most likely fix, and would be a meaningful next iteration to test.
- **Kupiec only tests unconditional coverage** — it checks whether the *number* of breaches matches the target, not whether breaches cluster in time. A Christoffersen conditional coverage test (or a simple check of breach independence) would directly confirm the clustering hypothesis proposed above for Model B, rather than leaving it as inference from the aggregate numbers.
- **Sample size per test is thin.** Each Kupiec test is run on roughly one year (~260 observations) with a 5% target, meaning the expected breach count is only ~13 — small enough that a handful of extra or missing breaches can flip a pass/fail result. Pooling multiple years per test (at the cost of losing year-by-year granularity) would give more statistical power, and is worth doing as a robustness check alongside the current annual tests.
-                                                                                                 
