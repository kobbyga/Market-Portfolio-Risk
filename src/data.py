import pandas as pd
import numpy as np

from config.py import (
    FX
)


def load_prices(path):
  """
  Loads DataFrame of csv file containing data, and computes log returns for all tickers

  Args:
      path: csv file containing close prices for all tickers

  Returns:
      returns: DataFrame containing log returns for all tickers
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
