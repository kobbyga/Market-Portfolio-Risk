import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar

from config import (
    alpha
)

def normal_var_es(sigma_p, W, alpha):
    """
    Compute Normal VaR and Expected Shortfall for a portfolio.

    Args:
        sigma_p: Daily portfolio volatility (decimal).
        W: Portfolio value.
        alpha: Tail probability level for VaR/ES (default 0.01).

    Returns:
        tuple: (VaR, ES) where both are positive loss amounts.
    """
    z = stats.norm.ppf(alpha)
    var = -z * sigma_p * W
    es = W * sigma_p * stats.norm.pdf(z) / alpha
  
    return var, es


def student_t_var_es(sigma_p, W, nu, alpha):
    """
    Compute Student-t VaR and Expected Shortfall, scaled so sigma_p remains the
    standard deviation of the fitted distribution.

    Args:
        sigma_p: Daily portfolio volatility (decimal).
        W: Portfolio value.
        nu: Degrees of freedom of the Student-t distribution.
        alpha: Tail probability level for VaR/ES (default 0.01).

    Returns:
        tuple: (VaR, ES) where both are positive loss amounts.
    """
    scale = np.sqrt((nu - 2) / nu)
    t_q = stats.t.ppf(alpha, df=nu) * scale
    var = -t_q * sigma_p * W

    t_pdf_at_q = stats.t.pdf(stats.t.ppf(alpha, df=nu), df=nu)
    es_std = (t_pdf_at_q / alpha) * (nu + stats.t.ppf(alpha, df=nu)**2) / (nu - 1)
    es = W * sigma_p * scale * es_std
  
    return var, es


def fit_student_t_dof(standardised_returns, bounds=(2.5, 30.0)):
    """
    Fit the degrees of freedom of a Student-t distribution via MLE, using
    standardised portfolio returns (returns divided by contemporaneous EWMA vol).

    Args:
        standardised_returns: Array of standardised returns.
        bounds: Tuple specifying the lower and upper bounds for degrees of freedom.

    Returns:
        float: Estimated degrees of freedom.
    """
    def neg_log_lik(nu):
        scale = np.sqrt((nu - 2) / nu)
        return -np.sum(stats.t.logpdf(standardised_returns / scale, df=nu) - np.log(scale))

    result = minimize_scalar(neg_log_lik, bounds=bounds, method="bounded")
  
    return float(result.x)
