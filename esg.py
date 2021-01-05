import requests
import json
import csv

# querystring = {"symbol":"ASML"}
# response = requests.request("GET", url, headers=headers, params=querystring)
# response = json.loads(response.text)

 

# response["defaultKeyStatistics"]["beta"]["fmt"]


def papoulate_data():
    with open('/home/talha/Downloads/abc.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with open('/home/talha/Downloads/abcd.csv', 'w') as new_file:
            fieldnames = ["Ticker", "Industry","Environment score", "Social score", "Governance score", "Percentile", "Controversy", "Adult entertainment - negative","Firearms","Animal welfare","Nuclear power","Alcohol","Tobacco","Gambling","Palm oil","Controversial weapons","Fur leather","Gmo","Catholic","Coal","Pesticides","Military contract", "Avg Volume", "EPS", "Marcket cap", "Beta", "View", "ESG"]


            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)


            csv_writer.writeheader()
            for rows in csv_reader:
                try:
                    E = float(rows["Environment score"])
                    print(E)
                    S = float(rows["Social score"])
                    print(S)
                    G = float(rows["Governance score"])
                    print(G)
                    ESG = (E + S + G)
                    print(ESG)
                    rows["ESG"] = ESG
                    # print(rows)
                    csv_writer.writerow(rows)

                    
                except Exception as e:
                    # rows["Beta"] = str(e)
                    # print("Exception in test_beta1 :",e)
                    # break
                    csv_writer.writerow(rows)
                    pass




if __name__ == '__main__':
    papoulate_data()


