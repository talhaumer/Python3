import pandas as pd
import numpy as np
import pandas_datareader as web
from datetime import date
from dateutil.relativedelta import relativedelta




def calculate_profit(tickers, start, end):
	try:
		
		tickers_list = []
		for ticker in tickers.keys():
			tickers_list.append(ticker)
			
		data = web.get_data_yahoo(tickers_list, start, end)

		adj_close = data['Adj Close']

		stock_monthly_profit = adj_close.iloc[-1,:] - adj_close.iloc[0,:]
		print(stock_monthly_profit)
		last_profit = stock_monthly_profit.dot(pd.Series(tickers))
		# print(last_profit)
		return last_profit

	except Exception as e:
		print(str(e))


if __name__ == '__main__':
	start = date.today() + relativedelta(months=-1)
	end = date.today()
	tickers = {'AAPL': 53.0, 'AMZN': 3.0, 'FB': 17.0, 'GOOGL': 1.0}
	last_profit = calculate_profit(tickers, start, end)