import json
import requests
import numpy as np
import pandas as pd
import pprint as pp
import matplotlib.pyplot as plt
import scipy.stats as stat
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import black_litterman, risk_models
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt import expected_returns
from pypfopt import risk_models
import yfinance as yf
from datetime import datetime
from datetime import timedelta
import pandas_datareader as web
from time import time
from calendar import monthrange
from pandas.tseries.offsets import BMonthEnd
from scipy.stats import norm
from pypfopt import DiscreteAllocation
from collections import defaultdict
from pymongo import MongoClient
from datetime import datetime
import collections
import random
from datetime import date
from dateutil.relativedelta import relativedelta




portfolio = {}
tickr = ["MSFT", "AMZN"]
start = "2015-11-4"
end = "2020-11-5"

CLOSE = "Adj Close"
for tick in tickr:
	pricedata = yf.download(tick, start, end)
	portfolio[tick] = pricedata[CLOSE]

benchmark = pd.DataFrame()

benchmark = yf.download("SPY", start, end)['Adj Close']


data_year = []
#print(ESG)
data_history = []
data_benchmark_month = []
data_month = []
# count_year = 1
min_value = 10000
max_value = 0
today = datetime.now().date() + timedelta(-1)
print("today: \n", today )
month_date = datetime.now() + timedelta(-30)
print("monthdata:\n", month_date)
for key in portfolio.keys():
	#print("key: ",key)
	#print("type(key): ", type(key))
	#print("type(portfolio(key)): ", type(portfolio[key]))
	#print ("--------------------")
	#print (portfolio[key])
	#print ("--------------------")
	# for date in portfolio[key].index:

	for date in portfolio[key].index:
		# #print("date",date)
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
		if  (last_bday == date and d == 'Dec') or today == date:
			if round(portfolio[key][date], 2) < min_value:
				min_value = round(portfolio[key][date], 2)
			if round(benchmark[key][date], 2) < min_value:
				min_value = round(benchmark[key][date], 2)
			if round(portfolio[key][date], 2) > max_value:
				max_value = round(portfolio[key][date], 2)
			if round(benchmark[key][date], 2) > max_value:
				max_value = round(benchmark[key][date], 2)
		#if date.replace(day = monthrange(date.year, date.month)[1]) == date:
			day = str(date.date().strftime('%Y'))
			value = {'x_axis' : day,
					  		'y_axis' : round(portfolio[key][date], 2)}
			value_benchmark =  {'x_axis' : day,
					  		'y_axis' : round(benchmark[key][date], 2)}
			
			history['value'] = day
			history['app_value'] = round(portfolio[key][date], 2)
			history['competitor_value'] = round(benchmark[key][date], 2)
			data_year.append(value)
			data_benchmark_year.append(value_benchmark)
			data_history.append(history)
			# count_year = count_year+1
		#Monthly data for backtest

		# if date >= month_date:	
		# 	day = str(date.date().strftime('%b-%d'))
		# 	value = {'x_axis' : day,
		# 			  		'y_axis' : portfolio[key]['Close'][date]}
		# 	value_benchmark =  {'x_axis' : day,
		# 			  		'y_axis' : benchmark[key]['Close'][date]}
		# 	data_month.append(value)
		# 	data_benchmark_month.append(value_benchmark)

# print("#############################################")
chart_data = {}
chart_data  =  { 'last_refresh':int(time()),
							'data' : data_year}
benchmark_data  =  { 'last_refresh':int(time()),
							'data' : data_benchmark_year}

print("benchmark_data: \n",benchmark_data)