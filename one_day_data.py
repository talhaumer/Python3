import pandas as pd
import numpy as np
import yfinance as yf

# data = pd.DataFrame()

tickers = ["AAPL", "FB", "AMZN", "MSFT"]

for ticker in tickers:
	data = yf.download(ticker, period='1d', interval='60m')
	
print(data['Adj Close'])