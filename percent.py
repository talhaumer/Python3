import requests
import json
import csv
import pandas as pd  
from scipy import stats

def papoulate_data():
    with open('/home/talha/Downloads/abc.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('/home/talha/Downloads/abcd.csv', 'w') as new_file:
            fieldnames = ["Ticker", "Industry","Environment score", "Social score", "Governance score", "Percentile", "Controversy", "Adult entertainment - negative","Firearms","Animal welfare","Nuclear power","Alcohol","Tobacco","Gambling","Palm oil","Controversial weapons","Fur leather","Gmo","Catholic","Coal","Pesticides","Military contract", "Avg Volume", "EPS", "Marcket cap", "Beta", "View", "ESG", "ESG_Percentile"]


            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)


            csv_writer.writeheader()
            data = pd.read_csv('/home/talha/Downloads/abc.csv')
            col_names = list(data.columns)
            for item in col_names:
                if item == "ESG":
                    industry_values = [0 if pd.isna(item) else float(item) for item in data[item].values]
                    print(industry_values)
                    percentiles = [stats.percentileofscore(industry_values, score) for score in industry_values]
                    print(percentiles)
                    data[item] = [{"score" : industry_values[i], "percentile" : percentiles[i]} for i in range(len(industry_values))]
                    print(data)
                    # print(data[item][0]["score"])
                    # print(data[item][0]["percentile"])
            i = 0
            for rows in csv_reader:
                
                try:
                    rows["ESG_Percentile"] = round(data["ESG"][i]["percentile"],2)
                    # print(rows)
                    csv_writer.writerow(rows)
                    
                except Exception as e:
                    # csv_writer.writerow(rows)
                    print(e)
                    pass
                i = i + 1




if __name__ == '__main__':
    papoulate_data()


