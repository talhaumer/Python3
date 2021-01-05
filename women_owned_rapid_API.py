import requests
import json
import csv
from pymongo import MongoClient 
from constant_women_owned_RAPI_API import gendr
import gender_guesser.detector as gender
detector_gender = gender.Detector()
client = MongoClient()
db = client['ticker']
 

headers = {
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
    'x-rapidapi-key': "6b1091072bmsh9684ba0675c7b7ep1f8852jsn6c5d63df5caf"
    }
url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-profile"

 



# querystring = {"symbol":"ASML"}
# response = requests.request("GET", url, headers=headers, params=querystring)
# response = json.loads(response.text)

 

# response["defaultKeyStatistics"]["beta"]["fmt"]


def papoulate_data():
    with open('/home/fintech/Ahsan/NEW_stocks_BETA_industries_values_with_dereived_industries.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('/home/fintech/Ahsan/new_1_stocks_industries_values_with_dereived_industries.csv', 'w') as new_file:
            fieldnames = ['Ticker','Industry','Derived Industry','Environment score','Social score','Governance score','Percentile','Controversy','Adult entertainment - negative','Firearms','Animal welfare','Nuclear power','Alcohol','Tobacco','Gambling','Palm oil','Controversial weapons','Fur leather','Gmo','Catholic','Coal','Pesticides','Military Contract','Vegan','Climate change','Alignment with UN SDGs','Labor rights','Diversity','Civil liberties','Water','Wind power - positive','Clean energy','Carbon emissions','Child labor','Stem cell research','Interest bearing instruments','Minority owned','Millennial owned','Gender equity','LGBTQ','Immigration','Family values','Maternity leave (rights)','Abortion','Contraceptives','Beta', "total_men", "total_women", "unpredicted_names", "all_names", "women_percentage"]


            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)


            csv_writer.writeheader()
            # for rows in csv_reader:
            #     print("------------------------------------------")
            #     print(rows)
            for rows in csv_reader:
                try:
                    # print("------------------------------------------")
                    # time.sleep(5)
                    ticker = rows["Ticker"]
                    querystring = {"symbol":str(ticker)}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    response = json.loads(response.text)
                    man = 0
                    women = 0
                    unpredicted_names = []
                    all_names = []
                    for record in response["assetProfile"]["companyOfficers"]:
                        name = record['name']
                        # print(name)
                        all_names.append(record['name'])
                        if "Mr." in name:
                            man += 1
                        elif "Ms." in name:
                            women += 1
                        else:

                            if "Dr." in name:
                                # print("in doctor")
                                # print(name)
                                name = record['name'].split("Dr. ")[1]
                                # print(name)
                                name = name.split(" ")[0]
                                # print(str(name.upper()))
                                # print(name)
                                try:
                                    gen = str(gendr[str(name.upper())])
                                    # print(gen)
                                except:
                                    gen = "unknown"
                                if gen == 'male':
                                    man += 1
                                elif gen == 'female':
                                    women += 1
                                else:
                                    if detector_gender.get_gender(str(name)) == 'male':
                                        man += 1
                                    elif detector_gender.get_gender(str(name)) == 'female':
                                        women += 1
                                    else:
                                        unpredicted_names.append(record['name'])

                            elif "Dr." not in name and "Mr." not in name and "Ms." not in name:
                                name = record['name'].split(" ")[0]
                                # print(name)
                                try:
                                    gen = str(gendr[str(name.upper())])
                                    # print(gen)
                                except:
                                    gen = "unknown"
                                if gen == 'male':
                                    man += 1
                                elif gen == 'female':
                                    women += 1
                                else:
                                    if detector_gender.get_gender(str(name)) == 'male':
                                        man += 1
                                    elif detector_gender.get_gender(str(name)) == 'female':
                                        women += 1
                                    else:
                                        unpredicted_names.append(record['name'])
                    women_owned_percentage = 0.0
                    if not unpredicted_names:
                        women_owned_percentage = (women) / (man + women)
                        women_owned_percentage = round(float(women_owned_percentage * 100) ,2)

                    if str(rows['Controversy']) == "FALSE":
                        rows['Controversy'] = 0

                    if str(rows['Beta']) == "NaN":
                        rows['Beta'] = 0

                    rows["total_men"] = man
                    rows["total_women"] = women
                    rows["unpredicted_names"] = unpredicted_names
                    rows["all_names"] = all_names
                    rows["women_percentage"] = women_owned_percentage
                    csv_writer.writerow(rows)

                    x={}
                    # print(ticker,man,women,unpredicted_names,all_names)
                    x["ticker"] = ticker
                    x["total_men"] = man
                    x["total_women"] = women
                    x["unpredicted_names"] = unpredicted_names
                    x["all_names"] = all_names
                    x["women_percentage"] = women_owned_percentage
                    db.ticker_executives_officers.insert_one(x)
                except Exception as e:
                    if str(rows['Beta']) == "NaN":
                        rows['Beta'] = 0

                    rows["total_men"] = 0
                    rows["total_women"] = 0
                    rows["unpredicted_names"] = []
                    rows["all_names"] = []
                    rows["women_percentage"] = 0.0
                    csv_writer.writerow(rows)
                    # rows["Beta"] = str(e)
                    # print("Exception in test_beta1 :",e)
                    # break
                    # csv_writer.writerow(rows)
                    pass




if __name__ == '__main__':
    papoulate_data()


