from pymongo import MongoClient
import pandas as pd
import numpy as np
import pandas_datareader as web
from datetime import date
from time import time
from dateutil.relativedelta import relativedelta
import urllib.parse, ssl
from collections import OrderedDict
import datetime
from constants_fintech import *
from fintech_methods import *
from news_related import *





vesgo_username	=	urllib.parse.quote(VESGO_CERT_SUBJECT)
vesgo_uri =	"mongodb://"+vesgo_username+"@"+VESGO_SERVER_IP+":"+MONGODB_SERVER_PORT+"/?authMechanism=MONGODB-X509"
client = MongoClient(vesgo_uri, ssl=True, ssl_certfile=VESGO_SLL_CERT, ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=PATH_TO_SLL_CA_CERT, connect=False,)

db = client['profit']
DB_PORTFOLIO_DATA = client.portfolio_dat

DB_PORTFOLIO_DATA = client.portfolio_data
DB_NOTIFICATIONS_DATA = client.notifications_data
DB_USER = client.registered_users
prft = {}


def profits(NAMESPACE):
	print(NAMESPACE)
	weights =  DB_PORTFOLIO_DATA["weights"].find_one({"namespace":NAMESPACE},{"_id":0})
	print(weights)
	if weights:
		tickers = weights["weights"]
		portfolio_date = weights["date"]
		time_end = int(time())
		start_t = 1602488686
		start = datetime.date.fromtimestamp(portfolio_date)
		print(start)
		end = datetime.date.fromtimestamp(time_end)
		tickers_list = []
		for ticker in tickers.keys():
			tickers_list.append(ticker)
		try:
			tickers_list = []
			for ticker in tickers.keys():
				tickers_list.append(ticker)
			if start != end:	
				data = web.get_data_yahoo(tickers_list, start, end)
				adj_close = data['Adj Close']
				stock_monthly_profit = adj_close.iloc[-1,:] - adj_close.iloc[0,:]
				last_profit = stock_monthly_profit.dot(pd.Series(tickers))
				# print(last_profit + 10000)
				prft["amount"] = round(last_profit + 10000, 2)
				pct = round((last_profit / 10000)*100, 2)
				if pct > 0:
					prft["percent"] = f'+{pct}%'
				else:
					prft["percent"] = f'{pct}%'
			else:
				prft["amount"] = "Amount will show after 24 hours"
				prft["percent"] = "Return will show after 24 hours"
			alpha = db.profit_data.find({'namespace':NAMESPACE})
			if alpha.count() == 0:
				x = db.profit_data.insert({'namespace':NAMESPACE, "profit":prft})
			else:
				db.profit_data.update({'namespace':NAMESPACE},{"$set":{"profit":prft}})
		except Exception as e:
			pass
	else:
		pass
#############################################################################################	
		
for name in DB_USER["user_info"].find():
	print(name["namespace"])
	profits(name["namespace"])
