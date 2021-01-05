import json
import csv
from pymongo import MongoClient 

client = MongoClient()
db = client.assets_data

def papoulate_data():
    with open('/home/talha/Downloads/new_stocks_industries_values_with_dereived_industries.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for rows in csv_reader:
            try:
                ticker = rows["Ticker"]
                industry = rows["Industry"]
                ESG = rows["ESG"]
                ESG_Percentile = rows["ESG_Percentile"]
                Beta = 1316.30 if rows["Beta"] == "1,316.30" else rows["Beta"]
                women_percentage = float(rows["women_percentage"]) if rows["women_percentage"] != 'N/A' else rows["women_percentage"]
                Controversy = int(rows["Controversy"])
                Adult_entertainment = 0 if rows["Adult entertainment - negative"] == 'FALSE' else 1
                Firearms = 0 if rows["Firearms"] == 'FALSE' else 1
                Animal_welfare = 0 if rows["Animal welfare"] == 'FALSE' else 1
                Nuclear_power = 0 if rows["Nuclear power"] == 'FALSE' else 1
                Alcohol = 0 if rows["Alcohol"] == 'FALSE' else 1
                Tobacco = 0 if rows["Tobacco"] == 'FALSE' else 1
                Gambling = 0 if rows["Gambling"] == 'FALSE' else 1
                Palm_oil = 0 if rows["Palm oil"] == 'FALSE' else 1
                # print(Palm_oil)
                Controversial_weapon = 0 if rows["Controversial weapons"] == 'FALSE' else 1
                # print(Controversial_weapon)
                Fur_leather = 0 if rows["Fur leather"] == 'FALSE' else 1
                Gmo = 0 if rows["Gmo"] == 'FALSE' else 1
                Catholic = 0 if rows["Catholic"] == 'FALSE' else 1
                Coal = 0 if rows["Coal"] == 'FALSE' else 1
                Pesticides = 0 if rows["Pesticides"] == 'FALSE' else 1
                Military_Contract = 0 if rows["Military Contract"] == 'FALSE' else 1
                # print("###################################")

                data = {
                        "asset_class" : "stock",
                        "ticker" : ticker,
                        "industry" : industry,
                        "values" : {
                                "esg_score" : float(ESG),
                                "esg_percentile" : float(ESG_Percentile),
                                "beta" : float(Beta) if Beta != '' else 'N/A',
                                "controvercy" : Controversy,
                                "women_owned_percentage" : women_percentage,
                                "Alcohol" : Alcohol,
                                "Gambling" : Gambling,
                                "Firearms" : Firearms,
                                "Adult entertainment" : Adult_entertainment,
                                "Animal welfare" : Animal_welfare,
                                "Nuclear power" : Nuclear_power,
                                "Tobacco" : Tobacco,
                                "Palm oil" : Palm_oil,
                                "Controversial weapons" : Controversial_weapon,
                                "Fur leather" : Fur_leather,
                                "Gmo" : Gmo,
                                "Catholic" : Catholic,
                                "Coal" : Coal,
                                "Pesticides" : Pesticides,
                                "Military Contract" : Military_Contract
                        }
                }
                db.all_assets.insert_one(data)
                # print(data)
            except Exception as e:
                print(e)
                # pass




if __name__ == '__main__':
    papoulate_data()








