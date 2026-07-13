import pandas as pd
import numpy as np

from config import (
    FX,
    IN_SAMPLE_START,
    IN_SAMPLE_END,
    BACKTEST_START,
    BACKTEST_END
)


def load_prices(path):
    """
    Load price data from CSV, convert all assets to GBP, and compute daily log returns.
    
    Args:
        path: Path to CSV file containing columns:
              Dates, NKE, C, SPX, USDGBP, CBK, VOW, DAX, GBPEUR.

    Returns:
        returns: DataFrame of daily log returns for GBP-denominated assets.
    """
    
  df = pd.read_csv(path, parse_dates=["Dates"]).set_index("Dates").sort_index()

  # USD-denominated assets converted to GBP
  usd_assets = ["NKE", "C", "SPX"]
  for col in usd_assets:
    df[col] = df[col] * df["USDGBP"]

  # EUR-denominated assets converted to GBP
  eur_assets = ["CBK", "VOW", "DAX"]
  for col in eur_assets:
    df[col] = df[col] * ( 1/ df["GBPEUR"])

  df = df.drop(columns = FX)

  # Compute log returns for assets 
  returns = np.log(df / df.shift(1)).dropna(how="any")
  
  return returns

def split_sample(returns):
    """
    Split the returns DataFrame into in-sample and backtest periods.

    Args:
        returns: DataFrame of daily log returns for GBP-denominated assets.

    Returns:
        in_sample: DataFrame containing returns between IN_SAMPLE_START and IN_SAMPLE_END.
        backtest: DataFrame containing returns between BACKTEST_START and BACKTEST_END.
    """
    
    in_sample = returns.loc[IN_SAMPLE_START:IN_SAMPLE_END]
    backtest = returns.loc[BACKTEST_START:BACKTEST_END] 
    
    return in_sample, backtest
