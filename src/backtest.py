from dataclasses import dataclass
import numpy as np
from scipy import stats


@dataclass
class KupiecResult:
    """
    Container for the results of the Kupiec proportion-of-failures test.

    Attributes:
        n: Total number of observations.
        breaches: Number of VaR breaches observed.
        breach_rate: Observed breach frequency (breaches / n).
        p_target: Target breach probability (VaR level).
        lr_stat: Likelihood ratio statistic.
        critical_value: Chi-square critical value at the chosen significance level.
        p_value: p-value of the test statistic.
        passed: Boolean indicating whether the test is passed (LR <= critical_value).
    """
    n: int
    breaches: int
    breach_rate: float
    p_target: float
    lr_stat: float
    critical_value: float
    p_value: float
    passed: bool

from src.config import (
    alpha,
    backtest_sig
)

def kupiec_test(breaches: int, n, p = alpha, significance = backtest_sig):
    """
    Perform the Kupiec proportion-of-failures test for VaR backtesting.

    Tests:
        H0: True breach probability equals the target VaR level p.

    The likelihood ratio statistic is:
        LR = -2 [ log L(p) - log L(phat) ]
    which is chi-square(1) distributed under H0.

    Args:
        breaches: Number of observed VaR breaches.
        n: Total number of observations.
        p: Target breach probability (VaR level), default 0.01.
        significance: Significance level for the chi-square test, default 0.05.

    Returns:
        KupiecResult: Dataclass containing LR statistic, p-value, critical value,
                      and pass/fail indicator.
    """
    x, phat = breaches, breaches / n

    def log_lik(prob):
        # Avoid log(0) in edge cases
        if prob in (0.0, 1.0):
            prob = min(max(prob, 1e-10), 1 - 1e-10)
        return (n - x) * np.log(1 - prob) + x * np.log(prob)

    lr = -2 * (log_lik(p) - log_lik(phat if 0 < phat < 1 else p))
    crit = stats.chi2.ppf(1 - significance, df=1)
    p_value = 1 - stats.chi2.cdf(lr, df=1)

    return KupiecResult(
        n=n,
        breaches=x,
        breach_rate=phat,
        p_target=p,
        lr_stat=lr,
        critical_value=crit,
        p_value=p_value,
        passed=lr <= crit,
    )
