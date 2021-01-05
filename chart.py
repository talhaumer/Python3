from pandas.tseries.offsets import BMonthEnd, BDay, BYearEnd
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from time import time


tickr = ["MSFT", "AMZN"]

start = datetime.now().date() + timedelta(-1825)
end = datetime.now().date() + timedelta(-1)
print(start)
print(end)

portfolio_new = pd.DataFrame()
for tick in tickr:
	portfolio_new[tick] = yf.download(tick, start, end)['Adj Close']
	# portfolio[tick] = pricedata["Adj Close"]
# print(portfolio_new)
weights = {"MSFT":0.70, "AMZN":0.30}
for key in weights.keys():
	for alpha in portfolio_new.keys():
		if key == alpha:
			portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

portfolio = {}
portfolio = portfolio_new.sum(axis=1)
# print(portfolio)
data = pd.DataFrame()
data = yf.download("SPY", start, end)['Adj Close']
	


benchmark = data

# print(benchmark)

data_year = []
#print(ESG)
data_history = []
data_benchmark_month = []
data_benchmark_year = []
data_month = []
# count_year = 1
min_value = 10000
max_value = 0
today = datetime.now().date() + timedelta(-1)
month_date = datetime.now() + timedelta(-30)

for date in portfolio.keys():
	# print(3)
	history = {
				'name':'year',
				'value':'',
				'app_name':'Fintech',
				'app_value':'',
				'competitor_name':'S&P 500',
				'competitor_value':''	
				}
	d = str(date.date().strftime('%b'))
	last_bday = BMonthEnd().rollforward(date)
	if (last_bday == date and d == 'Dec') or today == date:
		if round(portfolio[date], 2) < min_value:
			min_value = round(portfolio[date], 2)
		if round(benchmark[date], 2) < min_value:
			min_value = round(benchmark[date], 2)
		if round(portfolio[date], 2) > max_value:
			max_value = round(portfolio[date], 2)
		if round(benchmark[date], 2) > max_value:
			max_value = round(benchmark[date], 2)
	#if date.replace(day = monthrange(date.year, date.month)[1]) == date:
		month = str(date.date().strftime('%b'))
		year = str(date.date().strftime('%Y'))
		day = f"{month}-{year}"
		print(day)
		value = {'x_axis' : day,
				  		'y_axis' : round(portfolio[date] + 10000, 2)}
		value_benchmark =  {'x_axis' : day,
				  		'y_axis' : round(benchmark[date] + 10000, 2)}
		
		history['value'] = day
		history['app_value'] = round(portfolio[date] + 10000, 2)
		history['competitor_value'] = round(benchmark[date] + 10000, 2)
		data_year.append(value)
		data_benchmark_year.append(value_benchmark)
		data_history.append(history)
			# count_year = count_year+1
		##Monthly data for backtest

		# if date >= month_date:	
		# 	day = str(date.date().strftime('%b-%d'))
		# 	value = {'x_axis' : day,
		# 			  		'y_axis' : portfolio[key]['Close'][date]}
		# 	value_benchmark =  {'x_axis' : day,
		# 			  		'y_axis' : benchmark[key]['Close'][date]}
		# 	data_month.append(value)
		# 	data_benchmark_month.append(value_benchmark)
chart_data = {}
chart_data  =  { 'last_refresh':int(time()),
							'data' : data_year}
benchmark_data  =  { 'last_refresh':int(time()),
							'data' : data_benchmark_year}
print("###################################################################")
print(benchmark_data)