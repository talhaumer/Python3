from pymongo import MongoClient
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta


client = MongoClient()
db = client["stocks_database"]
company= db["Company"]

start = datetime.now().date() + timedelta(-30)
end = datetime.now().date()
portfolio_new = pd.DataFrame()
tickr = ["MSFT", "AAPL", "GOOG"]
for tick in tickr:
	portfolio_new[tick] = yf.download(tick, start, end)['Adj Close']
	portfolio_new.reset_index(inplace=True)
	ast = portfolio_new.to_json("records")
	x = json.loads(ast)
	print(x)
	company.insert_one({tick:x})



# for tick in tickr:
# 	

# ##########################################################
# ticker = ["GOOG"]
# for tic in ticker:
# 	data_from_db = company.find_one({"index":tic})
# 	print(data_from_db["data"])
# 	df = pd.DataFrame(data_from_db["data"])
# 	print(df)
# 	df.set_index("index", inplace=True)
# print(df)

# # print(df)