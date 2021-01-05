from pymongo import MongoClient
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta

client = MongoClient()
db = client["stocks_database"]

# start = datetime.now().date() + timedelta(-30)
# end = datetime.now().date()
# # portfolio_new = pd.DataFrame()
company = db["tick"]

# tickr = ["MSFT", "AAPL", "GOOG"]
# for tick in tickr:
# 	portfolio_new = yf.download(tick, start, end)['Adj Close']
# 	df = pd.DataFrame(portfolio_new)
# 	df.reset_index(inplace=True)
# 	alpha = df.to_json(orient='records')
# 	data = json.loads(alpha)
# 	print(data)
# 	company.insert_one({tick:data})




# company.insert_one(alpha)
# print("JSON.....  Data---------\n",alpha)



# a = pd.DataFrame(b)
# print(a)
# c = a.astype("int64")
# print(c.index)
# company.insert_one(b)

# for data in company.find():
# 	print("data")

# del data["_id"]
# print(data)
# # c = json.loads(data)
# a = pd.DataFrame(c)
# print(a)
data = company.find_one({'AAPL':{'$exists': True}})
del data["_id"]
df = pd.DataFrame.from_dict(data)
# df.set_index("index", inplace=True)
print(df)