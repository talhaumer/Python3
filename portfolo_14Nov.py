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
from constant_portfolio_related import *
import pandas_datareader as web
from time import time
from calendar import monthrange
from pandas.tseries.offsets import BMonthEnd, BDay, BYearEnd
from scipy.stats import norm
from pypfopt import DiscreteAllocation
from collections import defaultdict
from constant_portfolio_related import *
from pymongo import MongoClient
from datetime import datetime
import collections
import random
from datetime import date
from dateutil.relativedelta import relativedelta
# import time
filename = "/home/fintech/server/model_data.csv"


# client	=MongoClient()
# DB_MCAPS = client.mcaps

#######################################################################
risk_free_rate = 0.03
#######################################################################
def write_file(data):
	with open(filename, "w") as f:
		f.write(str(data))
		f.write("\n")
		



def get_derived_values(list_core_values, DB_VALUES):
	drived_values = {}
	all_derived_values = DB_VALUES["derived_values"].find_one({},{'_id': False})
	for value in list_core_values:
		drived_values[str(value)] = {}
		drived_values[str(value)].update(all_derived_values[str(value)])
	return drived_values

#######################################################################
def fetch_views(DB_MCAPS, tickers_list, db):
	viewdict = {}
	t_list = []
	con =[]
	mcaps = {}
	for ticker in tickers_list:
		view = db.views_percentage.find_one({"ticker":ticker})
		# view = db.views_percentage_new.find_one({"ticker":ticker})
		if view != None:
			val = float(round(view["views_percentage"]/100.0 , 2))
			# if val > 0:
			con.append(val)
			viewdict[view["ticker"]] = val
			t_list.append(str(view["ticker"]))

	for x in t_list:
		for data in DB_MCAPS.mcaps.find({},{"_id":0, x:1}):
			if data != None:
				for key, value in data.items():
					mcaps[key] = value/MILLION
			# v = str(view["views_percentage"])
			# v = v.split("%")[0]
			# viewdict[view["ticker"]] = float(round(float(v)/100.0 , 2))
		# else:
		# 	viewdict[str(ticker)] = 0.75
	# print("viewdict: \n",viewdict)
	# print("mcaps: \n",  mcaps)
	return t_list,viewdict, mcaps
#######################################################################
def calculate_weights(tickers_list,viewdict, starting_investment,risk_free_rate, mcaps):
	# tickers_list.remove("MNTA")
	# del viewdict["MNTA"]
	# del mcps["MNTA"]
	confidences = []
	for i in viewdict.keys():
		confidences.append(0.75)
	start = datetime.strptime(START_DATE, "%m/%d/%Y")
	end = datetime.strptime(END_DATE, "%m/%d/%Y")
	tickers = tickers_list
	# print(tickers)
	# print(viewdict)
	# print(mcaps)
	priceData = yf.download(tickers, start, end)
	historicalPrices = priceData[CLOSE]

	for t in tickers:
		if (t == BENCHMARK_TICKER):
			continue
		stock = yf.Ticker(t)
		try:
			mcaps[t] = stock.info["marketCap"]/1000000
		except:
			pass
	# print(mcaps)
	# mcaps = {'AAPL': 701240000000, 'AMZN': 773520000000, 'FB': 393710000000, 'GOOGL': 749860000000}
	# This line was just for testing purpose
	# If you want mcaps of previous data please visit https://ycharts.com
	# confidences = list(con.Confidences)

	
	stockPrices = historicalPrices.loc[:, historicalPrices.columns != BENCHMARK_TICKER]
	benchmark = historicalPrices[BENCHMARK_TICKER]
	S = risk_models.CovarianceShrinkage(stockPrices).ledoit_wolf()

	delta = black_litterman.market_implied_risk_aversion(benchmark, risk_free_rate=RISK_FREE_RATE)
	prior = black_litterman.market_implied_prior_returns(mcaps, delta, S)
	omega = np.diag(confidences)
	bl = BlackLittermanModel(S, pi="market", market_caps=mcaps, risk_averison="delta", absolute_views=viewdict, omega=omega)

	ret_bl = bl.bl_returns()
	rets_df = pd.DataFrame([prior, ret_bl, pd.Series(viewdict)], 
	     index=["Prior", "Posterior", "Views"]).T

	bl.bl_weights(delta)
	weights = bl.clean_weights()
	ef = EfficientFrontier(ret_bl, S)
	ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
	weights = ef.clean_weights()
	

	latest_prices = stockPrices.iloc[-1].dropna()

	da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=INVESTMENT_AMOUNT)
	alloc, leftover = da.lp_portfolio()
	# alloc, leftover = da.greedy_portfolio()
	# print("leftover money: ", leftover)

	return weights, alloc, priceData, leftover

########################################################################
def calculate_weighted_average(weights, myDictionary, db):
	wE = 0
	wS = 0
	wG = 0
	wB = 0
	high_score_enviroment = 0
	high_score_social = 0
	high_score_governance = 0
	high_beta = 0
	overall_average = 0
	# #print(weights)
	# #print(myDictionary)
	for keys in myDictionary.keys():
		data = db["all_assets"].find_one({"ticker":str(keys)})
		# #print(data["values"]["Environment score"])
		
		score_enviroment = db["all_assets"].find().sort("values.Environment score",-1).limit(1)
		for data in score_enviroment:
			high_score_enviroment = data["values"]["Environment score"]

		score_social = db["all_assets"].find().sort("values.Social score",-1).limit(1)
		for data in score_social:
			high_score_social = data["values"]["Social score"]

		score_governance = db["all_assets"].find().sort("values.Governance score",-1).limit(1)
		for data in score_governance:
			high_score_governance = data["values"]["Governance score"]	

		beta = db["all_assets"].find().sort("values.beta",-1).limit(1)
		for data in beta:
			high_beta = data["values"]["beta"]
			# print(high_beta)



		E = data["values"]["Environment score"]
		wE += (float(E) * float(weights[str(keys)]))

		S = data["values"]["Social score"]
		wS += (float(S) * float(weights[str(keys)]))

		G = data["values"]["Governance score"]
		wG += (float(G) * float(weights[str(keys)]))

		B = data["values"]["beta"]
		wB += (float(B) * float(weights[str(keys)]))
		# print(wB)

		overall_average += float(data["values"]["esg_percentile"]) * float(weights[str(keys)])

	wE = (wE/high_score_enviroment) * 100
	wE = round(wE/10,2)

	wS = (wS/high_score_social) * 100
	wS = round(wS/10,2)

	wG = (wG/high_score_governance) * 100
	#print(wG)
	wG = round(wG/10,2)

	wB = (wB/high_beta) * 100
	wB = round(wB/10,2)

	# overall_average = float(data["values"]["esg_percentile"])
	# #print(len(myDictionary.keys()))
	return wE,wS,wG,wB,overall_average
########################################################################
def get_stock(tickers_list):
	#Doewload stock historical data from yahoo finance
	data = pd.DataFrame(columns=tickers_list)
	#Fetch the data
	start = datetime.strptime('02/01/2014', "%d/%m/%Y")
	end = datetime.strptime('01/01/2020', "%d/%m/%Y")
	for ticker in tickers_list:
		# print(ticker)
		data[ticker] = yf.download(ticker, start, end)['Adj Close']
	return data
#######################################################################
def asset_allocation(lb,ub, invest_on_values, esgl, esgu, women_owned_stocks, removal_stocks, controversy, age, investment_horizon, DB_ASSETS):
	#Method to get tickers of the assets from db based on values
	#of user.
	# #print(lb,ub, invest_on_values, esgl, esgu, women_owned_stocks, removal_stocks, controversy)
	esg = 0
	volatility = 0
	investment_age_horizon_matix = [[0.10,0.10,0.10,0.10],[0.20,0.20,0.30,0.30],[0.30,0.30,0.40,0.40],[0.30,0.40,0.50,0.50]]
	volatility = investment_age_horizon_matix[int(investment_horizon)][int(age)]	
	if invest_on_values == 0:
		assets = DB_ASSETS["all_assets"].find({"$and":[{"values.beta":{"$gte":lb,"$lte":ub}},{"values.volatility":{"$gte":volatility}}]})
		# print("ASSETS1: \n",assets)
	else:
		if esgl <= esgu:
			esg = esgu
		elif esgl >= esgu:
			esg = esgl
		

		# print(int(investment_horizon),int(age))
		if women_owned_stocks == 0:
			assets = DB_ASSETS["all_assets"].find({"$and":[{"values.esg_percentile":{"$gte":esg}},{"values.controvercy":{"$gte":int(controversy)}},{"values.volatility":{"$gte":volatility}},{"values.beta":{"$gte":lb,"$lte":ub}}]})
			# print("ASSETS2: \n",assets)
		else:
			assets = DB_ASSETS["all_assets"].find({"$and":[{"values.esg_percentile":{"$gte":esg}},{"values.controvercy":{"$gte":int(controversy)}},{"values.volatility":{"$gte":volatility}},{"values.women_owned_percentage":{"$gte":women_owned_stocks}},{"values.beta":{"$gte":lb,"$lte":ub}}]})
			# print("ASSETS3: \n",assets)
		
	asset_list = []
	temp_dic = {}
	
	for each_asset in assets:
		# #print("assets:",each_asset)
		no = True
		for each_no in removal_stocks:
			if each_asset['values'][each_no] == 1:
				no = False
				break
		if no:
			del each_asset["_id"]
			asset_list.append(each_asset['ticker'])
			temp_dic[each_asset['ticker']] = each_asset['asset_class']


	# print("esg: \n",esg)
	# print("volatility: \n",volatility)
	# print(len(asset_list))
	# print(temp_dic)
	return asset_list, temp_dic
#######################################################################
#######################################################################
def generate_graph(weights,stocks,stockAlloc):
	# #Generate graph based on the invested amount, number of shares and weights.
	# #Allocate amount to each stock according to weight
	# total_ammount = starting_investment
	# allocated_ammount = starting_investment - leftover
	# # stocks = stocks.dropna()#No need
	# # allocated_ammount.update((x, y*total_ammount) for x, y in weights.items())
	# ##print("##########Allocated ammount to each stock#############\n",allocated_ammount)

	# #Get latest price
	# latest_price = {}
	# for key in weights:
	# 	latest_price[key] = stocks.iloc[0][key]
	##print("##########Latest price of each stock#############\n",latest_price)

	#Calculate shares of each stock to be bought
	allocated_shares = stockAlloc

	for each_share in allocated_shares:
		allocated_shares[each_share] = allocated_shares[each_share]
	##print("##########Total shares of each stock#############\n",allocated_shares)


	#Calculate portfolio value till now
	data_portfolio = stocks.assign(**allocated_shares).mul(stocks)
	calculated_portfolio = pd.DataFrame()
	calculated_portfolio['Close'] = data_portfolio.sum(axis=1)

	return calculated_portfolio
######################################################################
def benchmark_graph(stockAlloc):
	#Need to be revisited and optimized.
	#Generate graph based on the invested amount, number of shares and weights.
	#Allocate amount to each stock according to weight
	data = pd.DataFrame()
	#Fetch the data
	start = datetime.strptime(START_DATE, "%m/%d/%Y")
	end = datetime.strptime(END_DATE, "%m/%d/%Y")
	data = yf.download("SPY", start, end)['Adj Close']
	# for ticker in stockAlloc.keys():
	# 	try:
	# 		data[ticker] = yf.download(ticker, start, end)['Adj Close']
	# 	except:
	# 		pass
	
	return data

######################################################################



def Brownian(seed, N):

	np.random.seed(seed)
	dt = 1./N
	b = np.random.normal(0, 1, int(N))*np.sqrt(dt)
	W = np.cumsum(b)
	return b, W
	

def GBM(S0, mu, sigma, W, T, N):
	t = np.linspace(0, 1, N+1)
	S = []
	S.append(S0)
	
	for i in range(1, N+1):
		drift = (mu - 0.5 * sigma** 2) * t[i]
		diffusion = sigma * W[i-1]
		S_t = S0*np.exp(drift+diffusion)
		S.append(S_t)

	return S, t

def Euler_Maryuma(S0, mu, sigma, b, T, N, M):

	dt = T/N
	wi = [S0]
	for i in range(0, N):
		Winc = np.sum(b[(M*(i-1)+M):(M*i+M)])
		w_i_new = wi[i]+mu*wi[i]*dt+sigma*wi[i]*Winc
		wi.append(w_i_new)
	return wi


def calc_mu_sigma(priceData):


	epsilon = 0.01
	pct_chng = priceData.pct_change().dropna()
	u = pct_chng.mean()

	n_days = len(priceData.index)
	stdev = pct_chng.std()
	n_return = u
	# n_return = u * n_days
	# n_return = (1+u)**n_days - 1

	stdev = stdev * np.sqrt(n_days)

	return n_return, stdev


def calcValue(dailyPrices, numStocks):
	
	for p in dailyPrices:
		value = p * numStocks


# for debugging only
def calcError(soln_type, dailyPrice, simPrice):


	buffer = "#########" + soln_type + "############\n\n"
	i = 0

	
	print("Date\t\tActual\t\tSimulated\tDiff")
	for index, val in dailyPrice.iteritems():
		buffer = buffer + ("{:%m/%d/%Y}\t{:.2f}".format(index, val))
		buffer = buffer + ("\t\t{:.2f}".format(simPrice[i]))
		buffer = buffer + ("\t\t{:.2f}\n".format(val-simPrice[i]))
		i += 1	

	print(buffer)



def run_simulation(model, S0, mu, sigma, T, N, NUM_ITERATIONS):


	sim_result = []
	for i in range(0, NUM_ITERATIONS):
		b, W = Brownian(i, N)
		if (model is SimType.GBM):
			gbm_soln, time = GBM(S0, mu, sigma, W, T, N)
			sim_result.append(gbm_soln)
		if (model is SimType.EULER):
			euler_soln = Euler_Maryuma(S0, mu, sigma, b, T, N, M)
			sim_result.append(euler_soln)

	return sim_result

# for debugging only			
def plot_tickers(portfolio, benchmark):

	plt.figure()

	#x = np.linspace(1, 1, len(s_ret['SPY']))
	#y = np.linspace(-1, 0.5, 1)

	portfolio.plot()
	benchmark.plot()


	plt.xlabel("Years")
	plt.ylabel('Annual Returns')
	plt.legend()
	plt.show()
	

def calc_portfolio_value(simPrices, stockAlloc):
	m = pd.Series(simPrices)
	gains = pd.DataFrame(index=m.index, dtype=float)

	
	for i in range(0, len(m[0])-1):
		total_gain = 0
		a = pd.Series(0, index=m.index)
		for t in m.index:
			start_value = (m[t][i])[0] * stockAlloc[t]
			end_value = (m[t][i])[-1] * stockAlloc[t]
			gain_value = end_value - start_value
			a[t] += gain_value
		gains.insert(len(gains.columns), column=i, value=a)
		gains[i] = gains[i].astype(float)


	return gains.transpose()

def calc_z_score(z_score, stdev, mean):

	lower = (mean - z_score * stdev)
	upper = (mean + z_score * stdev)

	return [lower, upper]


def remove_outliers(input_data):

	
	outliers = input_data.between(input_data.quantile(0.02), input_data.quantile(0.98))
	dropped = input_data.loc[~outliers]
	for i in dropped.index:
		input_data.pop(i)

	new_index = np.arange(0, len(input_data.index))
	new_data = pd.Series(data=input_data.values, index = new_index)

	return new_data

#####################################new###########################################################
def drived_values(values_list, NAMPESPACE, myDictionary, DB_USER, DB_VALUES, DB_ASSETS):
	try:
		# print ("entering into derived values..")

		# print("\nmyDictionary: ", myDictionary)

		user_data = DB_USER['user_info'].find_one({"namespace" : NAMPESPACE})
		for key,val in user_data.items():
			# print(1)
			if key == "questionaire":
				# print(2)
				questionaire = val
				# print(3)
				for k, v in questionaire.items():
					# print(4)
					if k == "data":
						# print(5)
						# print(k, v)
						dicts = v
		# print(dicts)
		# print(6)
		

		drived_values = {}
		all_derived_values = DB_VALUES["derived_values"].find_one({},{'_id': False})
		# print("\nall_derived_values: ", all_derived_values)
		for value in values_list:
			drived_values[str(value)] = {}
			drived_values[str(value)].update(all_derived_values[str(value)])


		# print("\ndrived_values: ", drived_values)
		drived_values_list = []
		for key,val in drived_values.items():
			drived_values_list.append(val)

		# print("\ndrived_values_list: ", drived_values_list)


		counter = collections.Counter() 
		for d in drived_values_list:  
			counter.update(d) 
			  
		result = dict(counter)

		# print("\ncounter: ", counter)
		# print("\nresult: ", result)

		total = len(drived_values_list)

		for j in result:
			result[j] = round((float)(result[j])/total, 2)

		# print(result)



		# Finding the core values
		core_values = {'Adult entertainment': 0.0,'Alcohol': 0.0,'Animal welfare': 0.0,'Coal': 0.0,'Controversial weapons': 0.0,'Firearms': 0.0,'Fur leather': 0.0,'Gambling': 0.0, 'Gmo': 0.0,'Military Contract': 0.0,
		'Nuclear power': 0.0, 'Palm oil': 0.0,'Pesticides': 0.0,'Tobacco': 0.0}
		# print(1)
		for keys in myDictionary.keys():
			# print(2)
			data = DB_ASSETS["all_assets"].find_one({"ticker":str(keys)})
			# print(3)
			# print(data)
			if data:			
				values = data["values"]
				for key,val in values.items():
					if key in core_values:
						core_values[key] = values[key] + core_values[key]			

		total = len(myDictionary)

		for j in core_values:
			core_values[j] = round((float)(core_values[j])/total, 2)

		if core_values != None:
			# print("111111111111111111")
			result.update(core_values)

		# print("\ncore_values: ", core_values)

		finale = result
		return finale
	except Exception as e:
		print(str(e))

##################################################################################################################

def process_create_portfolio(NAMESPACE, DB_MCAPS, DB_USER, DB_ASSETS, DB_PORTFOLIO_DATA, DB_HELP_DATA, DB_VALUES, DB_VIEWS):
	""" Generate a portfolio based on values of a person.
	Each asset daily return based on historical values
	is created and inserted in DB.
	
	Args:
		NAMESPACE: User unique namespace.
		DB_USER: Database containing user information 
	Returns:
			Message containing success or failure status.
				Succes: Message if portfolio is created successfully.
				Failure: Message if there is some exception or portfolio
						 is not created successfully.
	"""
	#Personal : 1
	#Investment : 2
	#Values : 3 Yes:1, No:2, Don't care:3
	#Risk: 4

	#Q8 ESG
	#Q9 Sin
	#Q10 women
	#11 minority
	# NAMESPACE = "bst-Fy9a"
	user_data = DB_USER['user_info'].find_one({"namespace" : NAMESPACE})
	user_dna = user_data['questionaire']
	# print ("questionnaire of ", NAMESPACE ,": \n", user_dna)	tic	tickers = ["FB", "AMZN", "GOOGL", "APPL"]
	

	answer = DB_HELP_DATA['answer_to_risk'].find_one({},{'_id': False})
	
	core_values, risk_lb,risk_ub, risk_count, invest_on_values, esg1, esg2, women_owned_stocks, removal_stocks, controversy, age, investment_horizon = helper_risk(user_dna, answer)
	# #print(core_values, controversy, esg_score)
	# derived_vales = get_derived_values(core_values, DB_VALUES)
	# tickers, assets = asset_allocation(esg_score, nos_list, risk_lb, risk_ub, DB_ASSETS)
	tickers, assets = asset_allocation(risk_lb,risk_ub, invest_on_values, esg1, esg2, women_owned_stocks, removal_stocks, controversy, age, investment_horizon, DB_ASSETS)
	# print(len(tickers))
	# tickers_list = ["AAPL","AMZN","GOOGL", "FB", "SPY"]
	tickers_list,viewdict, mcaps = fetch_views(DB_MCAPS, tickers, DB_VIEWS)
	tickers_list.append("SPY")
	# tickers_list = ["AAPL","AMZN/","GOOGL", "FB", "SPY"]
	# viewdict = {"AAPL":round(0.48044287140393865, 2), "AMZN":round(0.5517003463054123, 2),"GOOGL":round(0.3036967364265295, 2), "FB":round(0.5100119801471847, 2)}
	# viewdict = {"AAPL":0.08, "AMZN": 0.24,"GOOGL": 0.08, "FB": 0.10}
	weights, stockAlloc, priceData, leftover = calculate_weights(tickers_list,viewdict, INVESTMENT_AMOUNT,risk_free_rate, mcaps)
	print(priceData)
	priceData = priceData.dropna()
	# print(stockAlloc)
	# #print("789",stockAlloc,weights)
	#print("stockAlloc: ",stockAlloc)
	# print("weights: ",weights)
	wE,wS,wG,wB,overall_average = calculate_weighted_average(weights, stockAlloc, DB_ASSETS)
	# profit = calculate_profit(weights)	
	model_data = defaultdict(list)
	N = len(priceData.index) 
	tickr = []
	for k in stockAlloc.keys():
		tickr.append(k)
	tickr.append("SPY")

	for t in tickr:
		S0 = priceData[CLOSE][t].iloc[-1] # last close price
		mu, sigma = calc_mu_sigma(priceData[CLOSE][t])
		if (model is SimType.GBM):
			model_data[t] = run_simulation(SimType.GBM, S0, mu, sigma, T, N,  NUM_ITERATIONS)
		if (model is SimType.EULER):
			model_data[t] = run_simulation(SimType.EULER, S0, mu, sigma, T, N,  NUM_ITERATIONS)
	# portfolio = generate_graph(weights,historical_data,stockAlloc)
	benchmark = benchmark_graph(stockAlloc)
	#monte carlo future prediction
	stockAlloc[BENCHMARK_TICKER] = round(INVESTMENT_AMOUNT / priceData[CLOSE][BENCHMARK_TICKER][-1])
	# print("stockAlloc[BENCHMARK_TICKER]: \n",stockAlloc[BENCHMARK_TICKER])
	# print("stockAlloc: \n", stockAlloc)
	portfolioValue = calc_portfolio_value(model_data, stockAlloc)
	# print(portfolioValue)
	# print("portfolioValue\n",portfolioValue)
	benchmark_return = portfolioValue[BENCHMARK_TICKER]
	#print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
	portfolio_df = portfolioValue.drop(columns=BENCHMARK_TICKER)
	# print(portfolio_df.columns)
	portfolio_df.insert(len(portfolio_df.columns), column='Portfolio', value=portfolio_df.sum(axis=1))
	#print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")

	
	benchmark_pct = benchmark_return.pct_change().dropna()
	z_score = pd.Series(stat.zscore(benchmark_pct, axis=0, nan_policy='omit'))
	benchmark_zscore = remove_outliers(z_score)
	port_pct_return = remove_outliers(portfolio_df['Portfolio'].div(INVESTMENT_AMOUNT))
	
	# benchmark_zscore.cumsum().plot(legend=True, label="Benchmark")
	# port_pct_return.cumsum().plot(legend=True, label="Portfolio")

	# QUANTILES = QUANTILES
	confidence_intervals = port_pct_return.quantile(q=QUANTILES)
	# print("-----------------------------------------------")
	# print("intervals")
	# for i in confidence_intervals.index:
		# print(i,": ",confidence_intervals[i])

	tickr.remove("SPY")
	data, portfolio_new = get_close(tickr)
	# start = datetime.strptime(START_DATE, "%m/%d/%Y")
	# end = datetime.strptime(END_DATE, "%m/%d/%Y")
	# pricedata = yf.download(tickr, start, end)
	# portfolio = pricedata[CLOSE]
	# portfolio = {}
	# for tick in tickr:
	# 	pricedata = yf.download(tick, start, end)
	# 	portfolio[tick] = pricedata[CLOSE]
	#print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
	# temp_predict_list = []
	temp_one = []
	# temp_five = {'plan':'5 years'}
	# temp_one['details'] = [{'confidence_level': 25, 'profit': round(confidence_intervals[0.25],2)}, {'confidence_level': 50, 'profit': round(confidence_intervals[0.50],2)}, {'confidence_level': 75, 'profit': round(confidence_intervals[0.75],2)}, {'confidence_level': 90, 'profit': round(confidence_intervals[0.90],2)}, {'confidence_level': 95, 'profit': round(confidence_intervals[0.95],2)}]
	# temp_five['details'] = helper_monet_carlo(portfolio, 1275)
	temp_one = [{"x_axis":2020,"percent_25":round(confidence_intervals[0.25],2),"percent_50":round(confidence_intervals[0.50],2),"percent_75":round(confidence_intervals[0.75],2),"percent_90":round(confidence_intervals[0.90],2)}]
	# temp_predict_list.append(temp_one)
	# print(temp_predict_list)
	# temp_predict_list.append(temp_five)
	
	res = DB_PORTFOLIO_DATA['predicted_data'].find({'namespace':NAMESPACE})
	if res.count() == 0:
		res = DB_PORTFOLIO_DATA['predicted_data'].insert({'namespace':NAMESPACE, "future_data":temp_one})
	else:
		res = DB_PORTFOLIO_DATA['predicted_data'].update({'namespace':NAMESPACE},{"$set":{"future_data":temp_one}})
		#print(temp_one)
	
	# #print(all_tickers)
	category_data = helper_category_data(assets, weights, leftover)
	

	# # Talha's Code start
	values_list = ["Firearms" , "Animal welfare", "Controversial weapons","Gmo", "Military Contract" ,"Adult entertainment","Tobacco","Gambling","Alcohol"]
	values_list = [item for item in values_list if item not in removal_stocks]
	# print("---------------------------------")
	# print(NAMESPACE)
	# print(weights)
	# print(values_list)
	# print("---------------------------------")

	finale = drived_values(values_list, NAMESPACE, weights, DB_USER, DB_VALUES, DB_ASSETS)
	# print(finale,"---------2-------------")
	portfolio_id = random.randrange(100, 999)
	name_list = ["sleek","lacy","thick","colorful","barbed","heavy-duty","curved","pure","lunar","refractory","shiny","conical","dark","transparent","opaque","adequate","permanent","metal","shallow","hollow","thin","metallic","foot-thick","birdlike","hi-tech","five-inch","gangling","almost solid","lightweight","molten","custom-made","dull gray","proprietary","famed","gold-plated","glossy black","indestructible","plain old","two-inch","protective","green and black","austere","segmented"]
	portfolio_title = random.choice(name_list)
	# datetime_now = datetime.date.today()

	datetime_now = int(time())
	ESG = {
		"Environment" : round(wE,2),
		"Social" : round(wS,2),
		"Governance" : round(wG,2),
		"risk" : round(risk_count,2),
		"Overall" : float(round(overall_average,2)),
		"portfolio_id" : portfolio_id,
		"portfolio_title" : portfolio_title,
		"Date": datetime_now
	}
	ESG.update(finale)
	# print("\n\nESG:\n",ESG)
	# # Talha's Code end
	benchmark_data_month,chart_data_month  = bencbenchmark_chart_data_month(data, portfolio_new, weights)
	benchmark_data_year, chart_data_year = bencbenchmark_chart_data_year(data, portfolio_new, weights)
	benchmark_data_week, chart_data_week = bencbenchmark_chart_data_week(data, portfolio_new, weights)
	benchmark_data, chart_data, data_history, min_value, max_value = benchmark_data_all(data, portfolio_new, weights) 
	

	datetime_now = int(time())
	res = DB_PORTFOLIO_DATA['weights'].find({'namespace':NAMESPACE})
	if res.count() == 0:
		res = DB_PORTFOLIO_DATA['weights'].insert({'namespace':NAMESPACE,
														"weights":weights,
														"date": datetime_now})
	else:
		DB_PORTFOLIO_DATA['weights'].update({'namespace':NAMESPACE},{"$set":{"weights":weights, "date": datetime_now}})
	response = DB_PORTFOLIO_DATA['portfolio_summary'].find({'namespace':NAMESPACE})
	print("response", response.count())
	if response.count() == 0:
		DB_PORTFOLIO_DATA['portfolio_summary'].insert({'namespace':NAMESPACE,
												'ESG':ESG,
												'chart_data':{'month_data':chart_data_month,
															'week_data':chart_data_week,
															'day_data':chart_data,
															'year_data':chart_data_year,
															'all_data':chart_data},
												'benchmark_chart_data':{'month_data' : benchmark_data_month,
																		'week_data':benchmark_data_week,
																		'day_data':benchmark_data,
																		'year_data':benchmark_data_year,
																		'title':'S&P 500',
																		'all_data':benchmark_data},
												
												"categories_data":category_data,
												"history" : data_history,
												"details":[],
												"min_value" : min_value,
												"max_value" : max_value
												})

	else:
		#print("Portfolio is going to be stored")
		DB_PORTFOLIO_DATA['portfolio_summary'].update({'namespace':NAMESPACE},
											{'$set':{'ESG':ESG,
												'chart_data':{'month_data':chart_data_month,
															'week_data':chart_data_week,
															'day_data':chart_data,
															'year_data':chart_data_year,
															'all_data':chart_data},
												'benchmark_chart_data':{'month_data' : benchmark_data_month,
																		'week_data':benchmark_data_week,
																		'day_data':benchmark_data,
																		'year_data':benchmark_data_year,
																		'title':'S&P 500',
																		'all_data':benchmark_data},
												
												"categories_data":category_data,
												"history" : data_history,
												"details":[],
												"min_value" : min_value,
												"max_value" : max_value
												}})
	# else:
	# 	#print("Portfolio is going to be stored")
	# 	DB_PORTFOLIO_DATA['portfolio_summary'].update({'namespace':NAMESPACE},
	# 										{'$set':{'chart_data.month_data':chart_data, 
	# 											'ESG':ESG,
	# 											'benchmark_chart_data.month_data' : benchmark_data,
	# 											"categories_data":category_data,
	# 											"history" : data_history,
	# 											"min_value" : min_value,
	# 											"max_value" : max_value
	# 											}})
	# return True
	return json.dumps({"message": "Succes"}), 200, {"ContentType":"application/json"}
#######################################################################

def get_close(ticker):
	start = datetime.now().date() + timedelta(-1825)
	end = datetime.now().date()
	portfolio_new = pd.DataFrame()
	
	for tick in ticker:
		portfolio_new[tick] = yf.download(tick, start, end)[CLOSE]

	print(portfolio_new)
	
	data = pd.DataFrame()
	data = yf.download("SPY", start, end)[CLOSE]
	# print(data.tail(5))
	return data , portfolio_new



#######################################################################
def helper_dna(USER_DNA):
	values = []
	nos_list = []
	esg = 0
	#Filter out only values questions
	# for each_ans in USER_DNA:
	# 	#print("ESG")
	# 	if each_ans['category_id'] == 3:
	# 		values.append(each_ans)
	#Map user values.
	values = USER_DNA
	# print('VAlues: \n', values)
	for each_value in values:
		if each_value['question_id'] == 8 and each_value['answer_id'] == 1:
			#print('chekcing esg')
			esg = 60
		elif each_value['question_id'] == 9 and each_value['answer_id'] == 2:
			nos_list.append("sin_stock")
		elif each_value['question_id'] == 10 and each_value['answer_id'] == 2:
			nos_list.append("women_owned")
		elif each_value['question_id'] == 11 and each_value['answer_id'] == 2:
			nos_list.append("miniority_owned")

	return esg, nos_list

#######################################################################
def helper_risk(USER_DNA, ANSWERS_TO_RISK):
	risk_ans = []
	core_values = []
	invest_on_values = 0
	# nos_list = []
	removal_stocks = []
	esg1 = 0
	esg2 = 0
	age = 0
	investment_horizon = 0
	# upper_investment_horizon = 0
	controversy = 0
	risk_count = 0
	women_owned_stocks = 0

	#Filter out only risk related questions
	# for each_ans in USER_DNA:
	# 	if each_ans['category_id'] == 4:
	# 		risk_ans.append(each_ans)
	# #print(ANSWERS_TO_RISK)
	risk_ans = USER_DNA["data"]
	# print("risk_ans: \n", risk_ans)
	for question in risk_ans:
		try:
			# #print(question)
			# #print("ddddd:",ANSWERS_TO_RISK['3']['1'])
			if question["category_id"] == "Risk":
				risk_count += ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])]
			elif question["category_id"] == "Values":
				if question['question_id'] == "qv1" and ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 1:
					invest_on_values = 1
					# esg = 60
				elif question['question_id'] == "qv2":
					for i in range(0,len(question["answer_id"])-1):
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 1:
							removal_stocks.append("Alcohol")
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 2:
							removal_stocks.append("Tobacco")
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 3:
							removal_stocks.append("Gambling")
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 4:
							pass
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 5:
							removal_stocks.append("Firearms")
							removal_stocks.append("Controversial weapons")
						if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][i])] == 6:
							removal_stocks.append("Adult entertainment")
				
				elif question['question_id'] == "qv3" and ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 1:					
					women_owned_stocks = 40
				elif question['question_id'] == "qv4":					
					if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 25:
						esg1 = 25
					elif ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 26:
						esg1 = 25
						removal_stocks.append("Coal")
						removal_stocks.append("Palm oil")
					elif ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 50:
						esg1 = 50
				elif question['question_id'] == "qv5":
					if ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])] == 50:
						esg2 = 50
				elif question['question_id'] == "qv6" or question['question_id'] == "qv7":
					controversy += ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])]
					core_values.append("Military Contract")
			elif question["category_id"] == "Demographics":
				if question['question_id'] == "qd1":
					age = ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])]
					
			elif question["category_id"] == "Investment":
				if question['question_id'] == "qi4":
					investment_horizon = ANSWERS_TO_RISK[str(question["question_id"])][str(question["answer_id"][0])]

		except Exception as e:
			print(str(e))


	if risk_count <= 22 and risk_count >= 0:
		#print ("User has low risk tolerance")
		risk_lb = 0
		risk_ub = .45
	elif risk_count >= 23 and risk_count <= 32:
		#print ("User has average risk tolerance")
		risk_lb = .45
		risk_ub = 1 
	elif risk_count >= 33 and risk_count <= 48:
		#print ("User has high risk tolerance")
		risk_lb = 1.01
		risk_ub = 10 

	return core_values,risk_lb,risk_ub, risk_count, invest_on_values, esg1, esg2, women_owned_stocks, removal_stocks, controversy, age, investment_horizon
# ############################################################################
# def get_company(symbol, stockAlloc):
# 	temp_dict = {}
# 	#print(stockAlloc)
# 	#print("ffffffffffffffffffffffffffffffff")
# 	temp = {}
# 	for dat in symbol:
# 		#print(dat)
# 		url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(str(dat))

# 		result = requests.get(url).json()
		
# 		for x in result['ResultSet']['Result']:
# 			if x['symbol'] == dat:
# 				temp_dict["ticker"] = str(dat)
# 				temp_dict["ticker_title"] = x['name']
# 				temp_dict["ticker_share"] = round(stockAlloc[str(dat)] * 100,2)
# 				temp.update(temp_dict)
# 				#print(dat, x['name'])
# 	#print("ffffffffffffffffffffffffffffffff")
# 	#print(temp)
# 	return temp

############################################################################
def get_company(symbol, stockAlloc, leftover):
	temp_dict = {}
	#print(stockAlloc)
	#print("ffffffffffffffffffffffffffffffff")
	total = 10000 - int(leftover)
	temp = []
	for dat in symbol:
		#print(dat)
		url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(str(dat))

		result = requests.get(url).json()
		
		for x in result['ResultSet']['Result']:
			temp_dict = {}
			if x['symbol'] == dat:
				temp_dict["ticker"] = str(dat)
				temp_dict["ticker_title"] = x['name']
				temp_dict["ticker_share"] = round(stockAlloc[str(dat)] * 100,2)
				temp_dict["ticker_ammount"] = round(stockAlloc[str(dat)] * int(total),2)
				temp.append(temp_dict)
				#print(dat, x['name'])
	# print("ffffffffffffffffffffffffffffffff")
	# print(temp)
	return temp


############################################################################
def helper_category_data(assets, weights, leftover):	
	#Dictionary containing asset class total weight
	temp_assets = {}
	#Dictionary containg asset class members list.
	temp_dic = {}
	temp_list = []
	for key in weights.keys():
		if assets[key] in temp_assets and weights[key] != 0:
			temp_dic.setdefault(assets[key], []).append(key)
			temp_assets[assets[key]] = temp_assets[assets[key]] + weights[key]
		elif weights[key] != 0:
			temp_dic.setdefault(assets[key], []).append(key)
			temp_assets[assets[key]] = weights[key]
	
	temp_dic_2 = {}
	for key in temp_assets.keys():
		temp_dic_2 = {}
		temp_dic_2['name']=key.capitalize() 
		temp_dic_2['companies']=get_company(temp_dic[key], weights, leftover)
		temp_dic_2['value'] = 100
		temp_dic_2['category_id'] = 1
		temp_dic_2['amount'] = 10000 - int(leftover)
		temp_list.append(temp_dic_2)

	return temp_list
############################################################################
def process_future_prediction(DB_USER, DB_PORTFOLIO_DATA, body):
	# from constants_fintech_methods import FUTURE_DUMMY
	# return json.dumps({"message":FUTURE_DUMMY}), 200, {"ContentType":"application/json"}

	namespace = body["namespace"]

	response = DB_USER['user_info'].find_one({'namespace':namespace})
	data = DB_PORTFOLIO_DATA['predicted_data'].find_one({'namespace':namespace})
	future_data = data['future_data']
	# print(future_data)
	if response:
		return json.dumps({"message":future_data}), 200, {"ContentType":"application/json"}

		# from constants_fintech_methods import FUTURE_DUMMY
		# return json.dumps({"message":FUTURE_DUMMY}), 200, {"ContentType":"application/json"}
	else:
		return json.dumps({"message": "User not found"}), 200, {"ContentType":"application/json"}

############################################################################
def calculate_profit(weights):
	tickers = weights
	try:
		start = date.today() + relativedelta(months=-1)
		end = date.today()
		tickers_list = []
		for ticker in tickers.keys():
			tickers_list.append(ticker)
			
		data = web.get_data_yahoo(tickers_list, start, end)

		adj_close = data['Adj Close']

		stock_monthly_profit = adj_close.iloc[-1,:] - adj_close.iloc[0,:]

		profit = stock_monthly_profit.dot(pd.Series(tickers))
		# print(profit)
		return profit

	except Exception as e:
		print(str(e))

####################################################################################
def bencbenchmark_chart_data_month(data, portfolio_new, weights):
	portfolio_new = portfolio_new.tail(22)
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)
	
	benchmark = data.tail(22)
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

	# print("chart_data_month: \n",chart_data_month)
	# print("benchmark_data month: \n",benchmark_data_month)
	return benchmark_data_month, chart_data_month
	_

def bencbenchmark_chart_data_year(data, portfolio_new, weights):
	portfolio_new = portfolio_new.tail(252)
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

	# print("chart_data_year: \n",chart_data_year)

	# print("benchmark_data_year: \n",benchmark_data_year)
	return benchmark_data_year, chart_data_year
	_
##################################################################################
def bencbenchmark_chart_data_week(data, portfolio_new, weights):
	portfolio_new = portfolio_new.tail(5)
	for key in weights.keys():
		for alpha in portfolio_new.keys():
			if key == alpha:
				portfolio_new[alpha] = weights[key] * portfolio_new[alpha]

	portfolio = {}
	portfolio = portfolio_new.sum(axis=1)

	benchmark = data.tail(5)
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
	# print("chart_data_week: \n", chart_data_week)

	# print("benchmark_data_week: \n", benchmark_data_week)
	return benchmark_data_week, chart_data_week
##################################################################################
def benchmark_data_all(data, portfolio_new, weights):
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
	# print(benchmark_data)
	return benchmark_data, chart_data, data_history, min_value, max_value
##################################################################################
# #!/usr/bin/env python
# import os, json, sqlite3, logging, re, time, ssl
# from flask import Flask, abort, request
# from flask_cors import CORS, cross_origin
# from constants_fintech import *
# from pymongo import MongoClient
# import urllib.parse

# from fintech_methods import *
# from portfolio_related import process_create_portfolio, process_future_prediction
# from news_related import *

# vesgo_username		=	urllib.parse.quote(VESGO_CERT_SUBJECT)
# vesgo_uri			 	=	"mongodb://"+vesgo_username+"@"+VESGO_SERVER_IP+":"+MONGODB_SERVER_PORT+"/?authMechanism=MONGODB-X509"
# client			=	MongoClient(vesgo_uri, ssl=True, ssl_certfile=VESGO_SLL_CERT, ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=PATH_TO_SLL_CA_CERT, connect=False,)

# DB_USER	= client.registered_users
# DB_QUESTIONNAIRE = client.questionnaire
# DB_CATEGORY_DATA = client.category_data
# DB_LIBRARY_DATA = client.library_data
# DB_NOTIFICATIONS_DATA = client.notifications_data
# DB_PORTFOLIO_DATA = client.portfolio_data
# DB_HELP_DATA = client.help_data
# DB_ASSETS = client.assets_data
# DB_CONFIG = client.config
# DB_VALUES = client.db_values
# DB_VIEWS = client.views_calculation
# DB_MCAPS = client.mcaps
# ########################################################

# values_list = ['Firearms', 'Animal welfare', 'Controversial weapons', 'Gmo', 'Military Contract', 'Adult entertainment', 'Tobacco', 'Gambling', 'Alcohol']
# NAMPESPACE = "test1-yPdW"
# myDictionary = {'ATRC': 0.0, 'ATVI': 0.0, 'AUDC': 0.0, 'BEAT': 0.0, 'BKNG': 0.01696, 'BMRN': 0.0, 'BPMC': 0.11334, 'BRKS': 0.0, 'BZUN': 0.00401, 'CCXI': 0.02794, 'CDNA': 0.00561, 'CERN': 0.0, 'CERS': 0.0, 'CG': 0.0, 'CGNX': 0.00481, 'CHRS': 0.0, 'CIGI': 0.0, 'CINF': 0.0, 'CONE': 0.0, 'CREE': 0.00212, 'CSGS': 0.0, 'CSX': 0.0, 'CVGW': 0.0, 'CWST': 0.0, 'DISCA': 0.0, 'DISCK': 0.0, 'DNKN': 0.0, 'DOX': 0.0, 'EBAY': 0.0, 'EDIT': 0.00155, 'EGOV': 0.0, 'ENTG': 0.0, 'EPAY': 0.0, 'EPZM': 0.11315, 'EXC': 0.0, 'EXLS': 0.0, 'FARO': 0.0, 'FAST': 0.0, 'FELE': 0.0, 'FFIV': 0.0, 'FORM': 0.0, 'FWONK': 0.0, 'FWRD': 0.0, 'GBDC': 0.0, 'GBT': 0.05976, 'GLPI': 0.0, 'GLUU': 0.0, 'GNTX': 0.0, 'GTLS': 0.00544, 'GWPH': 0.00738, 'HALO': 0.0, 'HAS': 0.0, 'HMSY': 0.0, 'HOLX': 0.0, 'HSIC': 0.0, 'HUBG': 0.0, 'HURN': 0.0, 'ICFI': 0.0, 'IMMU': 0.08903, 'INDB': 0.0, 'INSG': 0.00244, 'INTC': 0.04087, 'IPAR': 0.0017, 'IRDM': 0.0, 'ITCI': 0.11227, 'JD': 0.0252, 'KLIC': 0.00058, 'KPTI': 0.02655, 'KRNT': 0.0, 'LANC': 0.0, 'LITE': 0.0, 'LMNX': 0.0, 'LNT': 0.0, 'LPSN': 0.0, 'LSCC': 0.0, 'LSXMA': 0.0, 'LSXMK': 0.0, 'MANT': 0.0, 'MAR': 0.0, 'MESO': 0.14002, 'MKSI': 0.00669, 'MTLS': 0.0, 'MU': 0.02142, 'NGHC': 0.0, 'NMIH': 0.0, 'NSTG': 0.00705, 'NTRA': 0.00148, 'OSIS': 0.0, 'PCRX': 0.0, 'PEGA': 0.0, 'PENN': 0.02799, 'PEP': 0.0, 'PFPT': 0.0, 'PINC': 0.0, 'PLXS': 0.0, 'POWI': 0.0, 'PPC': 0.0, 'PRAA': 0.0, 'PRAH': 0.0, 'PRFT': 0.0, 'PTCT': 0.00965, 'PZZA': 0.0, 'QIWI': 0.0, 'RARE': 0.03421, 'RCII': 0.0, 'RDWR': 0.0, 'REG': 0.0, 'REGN': 0.0, 'RGNX': 0.01064, 'RMBS': 0.0, 'RP': 0.0, 'SBGI': 0.0, 'SBNY': 0.0, 'SBUX': 0.0, 'SEIC': 0.0, 'SHEN': 0.0, 'SIGI': 0.0, 'SIMO': 0.0, 'SIRI': 0.0, 'SLAB': 0.01565, 'SLP': 0.0, 'SMCI': 0.0, 'SPNS': 0.0, 'SPSC': 0.0, 'SSNC': 0.0, 'SWKS': 0.01193, 'SYKE': 0.0, 'TER': 0.0, 'TMUS': 0.00025, 'TRHC': 0.0, 'TRMB': 0.0, 'TRS': 0.0, 'TTGT': 0.0, 'UBSI': 0.0, 'UCTT': 0.0, 'VCYT': 0.01415, 'VG': 0.0, 'VICR': 0.00626, 'VNET': 0.0, 'VRTS': 0.0, 'WAFD': 0.0, 'XLRN': 0.00372, 'XNCR': 0.01132, 'YNDX': 0.00292, 'Z': 0.01395}


# drived_values(values_list, NAMPESPACE, myDictionary, DB_USER, DB_VALUES, DB_ASSETS)