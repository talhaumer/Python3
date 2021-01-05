import csv
from pymongo import MongoClient
import pandas as pd
import yfinance as yf
from datetime import datetime
import statistics 
from math import sqrt

client         =  MongoClient('localhost', 27017, connect=False)
DB_ASSETS = client.assets_data

all_data = DB_ASSETS["all_assets"].find()
# all_data = ["MSFT"]

def safe_execute(val1,val2):
    try:
        return val1/val2
    except:
        return 0

def calcu_std(val1):
    try:
        return statistics.stdev(val1)
    except:
        return 0

def get_stock(ticker):
    #Doewload stock historical data from yahoo finance
    data = pd.DataFrame(columns=[str(ticker)])
    start = datetime.strptime('07/01/2017', "%m/%d/%Y")
    end = datetime.strptime('07/31/2020', "%m/%d/%Y")
    #Fetch the data
    data[ticker] = yf.download(ticker, start, end)['Adj Close']
    # print(data[str(ticker)][0][0])
    # print(len(data[ticker]))
    year1 = []
    year2 = []
    year3 = []
    for i in range(1,len(data)-1):
        if "2017" in str(data[ticker].keys()[i]) and "2017" in str(data[ticker].keys()[i-1]):
            cal = (data[ticker][i] - data[ticker][i-1]) / data[ticker][i]
            year1.append(cal)
        if "2018" in str(data[ticker].keys()[i]) and "2018" in str(data[ticker].keys()[i-1]):
            cal = (data[ticker][i] - data[ticker][i-1]) / data[ticker][i]
            year2.append(cal)
        if "2019" in str(data[ticker].keys()[i]) and "2019" in str(data[ticker].keys()[i-1]):
            cal = (data[ticker][i] - data[ticker][i-1]) / data[ticker][i]
            year3.append(cal)
    
    # print(len(year1),len(year2),len(year3))
    dm_year1 = safe_execute(sum(year1),len(year1))
    dm_year2 = safe_execute(sum(year2),len(year2))
    dm_year3 = safe_execute(sum(year3),len(year3))
    dv_year1 = calcu_std(year1)
    dv_year2 = calcu_std(year2)
    dv_year3 = calcu_std(year3)

    V_year1 = sqrt(len(year1)) * dv_year1
    V_year2 = sqrt(len(year2)) * dv_year2
    V_year3 = sqrt(len(year3)) * dv_year3
    if V_year1 == 0.0:
        final_volatility = (V_year2+V_year3)/2
    elif V_year1 == 0.0 and V_year2 == 0.0:
        final_volatility = V_year3
    elif V_year1 == 0.0 and V_year2 == 0.0 and V_year3 == 0.0:
        final_volatility = 0.0
    else:
        final_volatility = (V_year1+V_year2+V_year3)/3
    print(final_volatility)
    # with open('/home/fintech/Ahsan/volatility.csv', 'a') as new_file:
    #     csv_writer = csv.DictWriter(new_file, fieldnames=["date",ticker])
    #     csv_writer.writeheader()
    #     csv_writer.writerow(data[ticker])
    return final_volatility
# minm = 10000 
# maxm = 0
for data in all_data:
    try:
        ticker = data["ticker"]
        # print(ticker)
        # print("______________________")
        stock = yf.Ticker(ticker)
        mcaps = stock.info["marketCap"]
        # print(mcaps)
        # print("______________________")
        if mcaps >= 1000000000:
            
            stocks_history = get_stock(ticker)
            # if maxm < stocks_history:
            # 	maxm = stocks_history
            # if minm > stocks_history:
            # 	minm = stocks_history
            DB_ASSETS["all_assets"].update({ "ticker": str(data["ticker"]) },{"$set": { "values.volatility": round(float(stocks_history),2)}})
           
        else:
            DB_ASSETS["all_assets"].update({ "ticker": str(data["ticker"]) },{"$set": { "values.volatility": "NaN"}})
            pass
    except Exception as e:
        DB_ASSETS["all_assets"].update({ "ticker": str(data["ticker"]) },{"$set": { "values.volatility": "NaaN"}})
        # print(e)
        pass
# print("__________________________")
# print(minm,maxm)
