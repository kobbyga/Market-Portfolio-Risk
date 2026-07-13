import pandas as pd
import numpy as np

def load_prices(path):
  """
  Loads DataFrame of csv file containing data, and computes log returns for all tickers

  Args:
      path: csv file containing close prices for all tickers

  Returns:
      returns: DataFrame containing log returns for all tickers
  """
  df = pd.read_csv(path, parse_dates=["Dates"]).set_index("Dates").sort_index()

  returns = np.log(df / df.shift(1)).dropna(how = "any")

  return returns
  
