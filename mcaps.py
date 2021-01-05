import csv, time
from pandas_datareader import data
from pymongo import MongoClient



client = MongoClient()
db = client['mcaps']


 

with open('/home/fintech/stocks_industries_values_with_dereived_industries.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    for rows in csv_reader:
        try:
            tickers = rows["Ticker"]
            mcaps = data.get_quote_yahoo(tickers)['marketCap']
            x = mcaps.to_dict()
            db.mcaps.insert_one(x)
            print(x)
        except :
            pass