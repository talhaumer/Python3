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
from pandas.tseries.offsets import BMonthEnd, BDay, BYearEnd
from scipy.stats import norm
from pypfopt import DiscreteAllocation
from collections import defaultdict
from pymongo import MongoClient
from datetime import datetime
import collections
import random
from datetime import date
from dateutil.relativedelta import relativedelta

def get_CLOSE():
	start = datetime.now().date() + timedelta(-1825)
	end = datetime.now().date()
	portfolio_new = pd.DataFrame()
	tickr = ["MSFT", "AMZN", "AAPL"]
	for tick in tickr:
		portfolio_new[tick] = yf.download(tick, start, end)['Adj Close']

	# print(portfolio_new.tail(5))
	# for key in weights.keys():
	# 	for alpha in portfolio_new.keys():
	# 		if key == alpha:
	# 			portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	# portfolio = {}
	# portfolio = portfolio_new.sum(axis=1)
	
	data = pd.DataFrame()
	data = yf.download("SPY", start, end)['Adj Close']
	# print(data.tail(5))
	return data , portfolio_new


####################################################################################
def bencbenchmark_chart_data_month(data, portfolio_new):
	weights = {"MSFT":30, "AMZN":20, "AAPL":50}
	portfolio_new = portfolio_new.tail(22)
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)
	benchmark = data.tail(22)
	portfolio = {}
	portfolio = portfolio_new.sum(axis=1) 
	data_year = []
	#print(ESG)
	data_history = []
	data_benchmark_month = []
	data_benchmark = []
	data_month = []
	# count_year = 1
	min_value = 10000
	max_value = 0
	today = datetime.now().date() + timedelta(-1)
	month_date = datetime.now() + timedelta(-365)

	# for key in portfolio.keys():
	for date in portfolio.keys():
		history = {
					'name':'year',
					'value':'',
					'app_name':'Fintech',
					'app_value':'',
					'competitor_name':'S&P 500',
					'competitor_value':''	
					}
		d = str(date.date().strftime('%a'))
		last_bday = BDay().rollforward(date)
		if  last_bday == date or today == date:
			if round(portfolio[date], 2) < min_value:
				min_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) < min_value:
				min_value = round(benchmark[date], 2)
			if round(portfolio[date], 2) > max_value:
				max_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) > max_value:
				max_value = round(benchmark[date], 2)

			month = str(date.date().strftime('%b'))
			year = str(date.date().strftime('%d'))
			day = f"{month}-{year}"
			value = {'x_axis' : day,
					  		'y_axis' : round(portfolio[date] + 10000, 2)}
			value_benchmark =  {'x_axis' : day,
					  		'y_axis' : round(benchmark[date] + 10000, 2)}
			
			history['value'] = day
			history['app_value'] = round(portfolio[date] + 10000, 2)
			history['competitor_value'] = round(benchmark[date] + 10000, 2)
			data_year.append(value)
			data_benchmark.append(value_benchmark)
			data_history.append(history)
				

	chart_data_month =  { 'last_refresh':int(time()),
								'data' : data_year}
	benchmark_data_month =  { 'last_refresh':int(time()),
								'data' : data_benchmark}

	print("chart_data_month: \n",chart_data_month)
	print("benchmark_data month: \n",benchmark_data_month)
	return benchmark_data_month, chart_data_month
	_

def bencbenchmark_chart_data_year(data, portfolio_new):
	weights = {"MSFT":30, "AMZN":20, "AAPL":50}
	portfolio_new = portfolio_new.tail(252)
	print(portfolio_new)
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)
	
	benchmark = data.tail(252)
	data_year = []
	#print(ESG)
	data_history = []
	data_benchmark_month = []
	data_benchmark = []
	data_month = []
	# count_year = 1
	min_value = 10000
	max_value = 0
	today = datetime.now().date() + timedelta(-1)
	month_date = datetime.now() + timedelta(-30)

	
	for date in portfolio.keys():
		history = {
					'name':'year',
					'value':'',
					'app_name':'Fintech',
					'app_value':'',
					'competitor_name':'S&P 500',
					'competitor_value':''	
					}
		d = str(date.date().strftime('%m'))
		last_bday = BMonthEnd().rollforward(date)
		if  last_bday == date or today == date:
			if round(portfolio[date], 2) < min_value:
				min_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) < min_value:
				min_value = round(benchmark[date], 2)
			if round(portfolio[date], 2) > max_value:
				max_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) > max_value:
				max_value = round(benchmark[date], 2)

			month = str(date.date().strftime('%b'))
			year = str(date.date().strftime('%y'))
			day = f"{month}-{year}"
			value = {'x_axis' : day,
					  		'y_axis' : round(portfolio[date] + 10000, 2)}
			value_benchmark =  {'x_axis' : day,
					  		'y_axis' : round(benchmark[date] + 10000, 2)}
			
			history['value'] = day
			history['app_value'] = round(portfolio[date] + 10000, 2)
			history['competitor_value'] = round(benchmark[date] + 10000, 2)
			data_year.append(value)
			data_benchmark.append(value_benchmark)
			data_history.append(history)
				

	chart_data_year =  { 'last_refresh':int(time()),
								'data' : data_year}
	benchmark_data_year =  { 'last_refresh':int(time()),
								'data' : data_benchmark}

	print("chart_data_year: \n",chart_data_year)

	print("benchmark_data_year: \n",benchmark_data_year)
	return benchmark_data_year, chart_data_year
	_
##################################################################################
def bencbenchmark_chart_data_week(data, portfolio_new):
	weights = {"MSFT":30, "AMZN":20, "AAPL":50}
	portfolio_new = portfolio_new.tail(5)
	print(portfolio_new)
	print(portfolio_new)
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)
	print(portfolio)
	benchmark = data.tail(5)
	print(benchmark)
	data_year = []
	#print(ESG)
	data_history = []
	data_benchmark_month = []
	data_benchmark = []
	data_month = []
	# count_year = 1
	min_value = 10000
	max_value = 0
	today = datetime.now().date() + timedelta(-1)
	month_date = datetime.now() + timedelta(-30)

	# for key in portfolio.keys():
	print("benchmark", benchmark.keys())
	print(portfolio.keys())
	for date in portfolio.keys():
		print(portfolio[date])
		print(benchmark[date])
		history = {
					'name':'year',
					'value':'',
					'app_name':'Fintech',
					'app_value':'',
					'competitor_name':'S&P 500',
					'competitor_value':''	
					}
		d = str(date.date().strftime('%a'))
		last_bday = BDay().rollforward(date)
		if  last_bday == date or today == date:
			if round(portfolio[date], 2) < min_value:
				min_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) < min_value:
				min_value = round(benchmark[date], 2)
			if round(portfolio[date], 2) > max_value:
				max_value = round(portfolio[date], 2)
			if round(benchmark[date], 2) > max_value:
				max_value = round(benchmark[date], 2)

			day = str(date.date().strftime('%a'))
			value = {'x_axis' : day,
					  		'y_axis' : round(portfolio[date] + 10000, 2)}
			value_benchmark =  {'x_axis' : day,
					  		'y_axis' : round(benchmark[date]  + 10000, 2)}
			
			history['value'] = day
			history['app_value'] = round(portfolio[date] + 10000, 2)
			history['competitor_value'] = round(benchmark[date] + 10000, 2)
			data_year.append(value)
			data_benchmark.append(value_benchmark)
			data_history.append(history)
				

	chart_data_week =  { 'last_refresh':int(time()),
								'data' : data_year}
	benchmark_data_week =  { 'last_refresh':int(time()),
								'data' : data_benchmark}
	print("chart_data_week: \n", chart_data_week)

	print("benchmark_data_week: \n", benchmark_data_week)
	return benchmark_data_week, chart_data_week
##################################################################################
def benchmark_data_all(data, portfolio_new):
	weights = {"MSFT":30, "AMZN":20, "AAPL":50}
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)

	benchmark = data
	data_year = []
	#print(ESG)
	data_history = []
	data_benchmark_month = []
	data_benchmark_year = []
	data_month = []
	# count_year = 1
	min_value = 10000
	max_value = 0
	today = datetime.now().date() + timedelta(-3)
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
			# month = str(date.date().strftime('%b'))
			year = str(date.date().strftime('%Y'))
			day = f"{year}"
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
	return benchmark_data, chart_data, data_history, min_value, max_value

data, portfolio_new = get_CLOSE()
# bencbenchmark_chart_data_week(data, portfolio_new)
bencbenchmark_chart_data_week(data, portfolio_new)