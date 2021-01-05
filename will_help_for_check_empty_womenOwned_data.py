import csv, time
import pandas as pd

def papoulate_data():
    # csv_reader_ticker=[]
    with open('C:/Users/Ahsan/Desktop/fintech_vesgo/latest_stocks_industries.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        
        for rows in csv_reader:
            try:
                if str(rows['all_names']) == "[]":
                    print(rows['Ticker'])
            except:
                
                pass




if __name__ == '__main__':
    papoulate_data()








