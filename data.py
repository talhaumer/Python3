from pymongo import MongoClient
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta
import csv
import time

client = MongoClient()
db = client["stocks_database"]

start = datetime.now().date() + timedelta(-8)
hiredate = str(start)
pattern = '%Y-%m-%d'
epoch = int(time.mktime(time.strptime(hiredate, pattern)))
end = datetime.now().date()
# portfolio_new = pd.DataFrame()
# with open('/home/talha/Downloads/new_stocks_industries_values_with_dereived_industries.csv', 'r') as csv_file:
# 	csv_reader = csv.DictReader(csv_file)

tickers = ["AMZN", "AAPL", "MSFT", "FB"]
for ticker in tickers:
		try:
			portfolio_new = yf.download(ticker, end)['Adj Close']
			df = pd.DataFrame(portfolio_new)
			df.reset_index(inplace=True)
			alpha = df.to_json(orient='records')
			data = json.loads(alpha)
			print(data)
			company = db[ticker]
			x = company.remove({'Date': epoch})
			company.insert_many(data)
			print(x)
		except  Exception as e:
			print(e)
			pass



# FOR TEST  
# tickr = ['AXSM','BGNE','CRSP', 'GDS','OLED', 'SPY']
# priceData = pd.DataFrame()
# for ticker in tickr:
# 	cursor = db[ticker].find()
# 	if cursor.count() != 0:
# 		df =  pd.DataFrame(list(cursor))
# 		print(df)
# 		del df['_id']
# 		df["Date"] = pd.to_datetime(df['Date'],unit='ms')
# 		df.set_index("Date", inplace=True)
# 		df.columns = [ticker]
# 		priceData = pd.concat([priceData, df], axis=1)

# print(priceData)