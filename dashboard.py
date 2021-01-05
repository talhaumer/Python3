from pymongo import MongoClient
from datetime import date
from time import time
from dateutil.relativedelta import relativedelta
import pandas_datareader as web
import pandas as pd



client = MongoClient()

DB_PORTFOLIO_DATA = client.portfolio_data
DB_NOTIFICATIONS_DATA = client.notifications_data
DB_USER = client.registered_users

def dashboard(namespace):
	NAMESPACE = namespace
	TICKER = []
	rep = DB_PORTFOLIO_DATA['weights'].find({'namespace':NAMESPACE})
	for each_res in rep:
		TICKER = each_res['weights'].keys()
	return_list = []
	if not TICKER:
		TICKER = ["General"]

	for each_ticker in TICKER:
		response = DB_NOTIFICATIONS_DATA["news_feed"].find({"$or":[{'ticker':each_ticker},{'ticker':"General"}]}).sort("eve_sec", -1).limit(1)

		for each_res in response:
			del each_res["_id"]
			if not any(d.get('title', None) == each_res['title'] for d in return_list):
				return_list.append(each_res)

	for itm in return_list:
		a = itm

	for k in a.keys():
		if k == "title":
			news = a[k]


	res = {}
	res["user_info"] = {}
	res["user_info"]["return"] = "+20%"
	res["user_info"]["amount"] =  12000.0
	res["user_info"]["user_key_face"] = news
	res["user_info"]["gender"] = ""
	res["user_info"]["age_group"] = ""
	 
	user_data = DB_USER['user_info'].find_one({"namespace" : NAMESPACE})
	print(user_data)
	for key,val in user_data.items():
		if key == "questionaire":
			questionaire = val
			for k, v in questionaire.items():
				if k == "data":
					dicts = v

	age = next(item for item in dicts if item["question_id"] == "qd1")
	print(age)
	for key,val in age.items():
		if key =="answer_id":
			res["user_info"]["age_group"] = val[0]


	# gnder = next(item for item in dicts if item["question_id"] == "qd2")
	# for key,val in gnder.items():
	# 	if key =="answer_id":
	# 		res["user_info"]["gender"] = val[0]


	postive = []
	negative = []


	dvalues = ['Vegan', 'Climate change', 'Alignment with UN SDGs', 'Labor rights', 'Diversity', 'Civil liberties', 'Water', 'Wind power - positive', 'Clean energy', 'Carbon emissions', 'Child labor', 'Stem cell research', 'Interest bearing instruments', 'Minority owned', 'Millennial owned', 'Gender equity', 'LGBTQ', 'Immigration', 'Family values', 'Maternity leave (rights)', 'Abortion', 'Contraceptives', 'Adult entertainment', 'Alcohol', 'Animal welfare', 'Coal', 'Controversial weapons', 'Firearms', 'Fur leather', 'Gambling', 'Gmo', 'Military Contract', 'Nuclear power', 'Palm oil', 'Pesticides', 'Tobacco']
	item = ["Environment", "Social", "Governance"]
	esg = DB_PORTFOLIO_DATA['portfolio_summary'].find_one({'namespace':NAMESPACE},{"_id":0, "ESG":1})
	risk = esg["ESG"]["risk"]
	t_risk = (risk/47)*10
	res["risk"] = round(t_risk, 2)


	for k  in dvalues:
		if esg["ESG"][k] > 0:
			postive.append(k)
		elif esg["ESG"][k] < 0:
			negative.append(k)

	res["positive_values"] = []
	res["positive_values"] = postive
	res["negative_values"] = []
	res["negative_values"] = negative



	res["portfolio_composition"] = {}
	res["portfolio_composition"]["ESG"] = []
	for k in item:
		stu=  {"value": "Environment",
	        "score": 15.5,
	        "score_mean": "",
	        "score_calculation": "",
	        "score_improvement": {
	          
	        }
	}
		if k in esg["ESG"]:
			print(k)
			stu["value"] = k
			stu["score"] = esg["ESG"][k]
			stu["score_mean"] = ""
			stu["score_calculation"] = ""
		res["portfolio_composition"]["ESG"].append(stu)



	res["portfolio_composition"]["derived_values"] = []
	for i in dvalues:
		std=  {"value": "Social",
	        "score": 15.5,
	        "score_mean": "",
	        "score_calculation": "",
	        "score_improvement": {
	          
	        }
	}
		if  i in esg["ESG"]:
			std["value"] = i
			std["score"] = esg["ESG"][i]
			std["score_mean"] = ""
			std["score_calculation"] = ""
			res["portfolio_composition"]["derived_values"].append(std)


	start = date.today() + relativedelta(months=-1)
	end = date.today()
	weights =  DB_PORTFOLIO_DATA["weights"].find_one({"namespace":NAMESPACE},{"_id":0})
	tickers = weights["weights"]
	tickers_list = []
	for ticker in tickers.keys():
		tickers_list.append(ticker)
	try:
		tickers_list = []
		for ticker in tickers.keys():
			tickers_list.append(ticker)
			
		data = web.get_data_yahoo(tickers_list, start, end)

		adj_close = data['Adj Close']

		stock_monthly_profit = adj_close.iloc[-1,:] - adj_close.iloc[0,:]

		last_profit = stock_monthly_profit.dot(pd.Series(tickers))
		# print(last_profit + 10000)
		res["user_info"]["amount"] = round(last_profit + 10000, 2)
		pct = round((last_profit / 10000)*100, 2)
		res["user_info"]["return"] = f'{pct}%'
	except Exception as e:
		print(str(e))



	data = res

	if data != None:
		print(data)
		print("/n:","---------------------------")

# name = "uk-DdZ0"


for name in DB_USER["user_info"].find():
	dashboard(name["namespace"])