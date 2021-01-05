from pymongo import MongoClient
import pandas as pd
import numpy as np
import pandas_datareader as web
from datetime import date
from time import time
from dateutil.relativedelta import relativedelta
from constants_fintech import *
from fintech_methods import *
from news_related import *
import urllib.parse, ssl
from collections import OrderedDict
import datetime





vesgo_username	=	urllib.parse.quote(VESGO_CERT_SUBJECT)
vesgo_uri =	"mongodb://"+vesgo_username+"@"+VESGO_SERVER_IP+":"+MONGODB_SERVER_PORT+"/?authMechanism=MONGODB-X509"
client =	MongoClient(vesgo_uri, ssl=True, ssl_certfile=VESGO_SLL_CERT, ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=PATH_TO_SLL_CA_CERT, connect=False,)

db = client['dashboard']
DB_PORTFOLIO_DATA = client.portfolio_dat

DB_PORTFOLIO_DATA = client.portfolio_data
DB_NOTIFICATIONS_DATA = client.notifications_data
DB_USER = client.registered_users
DB_PROFIT = client.profit

def dashboard(namespace):
	NAMESPACE = namespace
	print(NAMESPACE)
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
	for key,val in user_data.items():
		if key == "questionaire":
			questionaire = val
			for k, v in questionaire.items():
				if k == "data":
					dicts = v

	age = next(item for item in dicts if item["question_id"] == "qd1")
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


	
	profit =  DB_PROFIT["profit_data"].find_one({"namespace":NAMESPACE},{"_id":0})
	if profit:
		res["user_info"]["amount"] = profit["profit"]
		res["user_info"]["return"] = profit["profit"]
	else:
		res["user_info"]["amount"] =  "calculate after 24 hours"
		res["user_info"]["return"] =  "calculate after 24 hours"

	print(res)
	return res
#############################################################################################	
		

namespace = "talhaumer-tbSr"
dashboard(namespace)

