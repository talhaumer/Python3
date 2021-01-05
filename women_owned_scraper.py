import csv, time
import pandas as pd

def papoulate_data():
    # csv_reader_ticker=[]
    with open('/home/fintech/Ahsan/NEW_stocks_BETA_industries_values_with_dereived_industries.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # print(csv_reader)
        # for rows in csv_reader:
        #     print(rows["Ticker"])

    # csv_file.close()
        with open('/home/fintech/Ahsan/new_1_stocks_industries_values_with_dereived_industries.csv', 'w') as new_file:
            fieldnames = ['Ticker','Industry','Derived Industry','Environment score','Social score','Governance score','Percentile','Controversy','Adult entertainment - negative','Firearms','Animal welfare','Nuclear power','Alcohol','Tobacco','Gambling','Palm oil','Controversial weapons','Fur leather','Gmo','Catholic','Coal','Pesticides','Military Contract','Vegan','Climate change','Alignment with UN SDGs','Labor rights','Diversity','Civil liberties','Water','Wind power - positive','Clean energy','Carbon emissions','Child labor','Stem cell research','Interest bearing instruments','Minority owned','Millennial owned','Gender equity','LGBTQ','Immigration','Family values','Maternity leave (rights)','Abortion','Contraceptives','Beta', "Total Men","Total Women","Women Percentage"]


            csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)


            csv_writer.writeheader()
            # for rows in csv_reader:
            #     print("------------------------------------------")
            #     print(rows)
            for rows in csv_reader:
                try:
                    # print("------------------------------------------")
                    # time.sleep(7)
                    ticker = rows["Ticker"]
                    # print(f'Downloading Estimates for {ticker}')
                    link='https://finance.yahoo.com/quote/{}/profile?p={}'.format(ticker, ticker)
                    df_est = pd.read_html(str(link))
                    res = df_est[0]
                    # print(res['Name'])
                    man = 0
                    women = 0
                    for name in res['Name']:
                        if "Mr." in name:
                            man += 1
                        elif "Ms." in name:
                            women += 1
                        else:
                            man += 1

                    if str(rows["Beta"]) == "NaN":
                        rows["Beta"] = 0

                    if str(rows["Controversy"]) == "FALSE":
                        rows["Controversy"] = 0

                    rows["Total Men"] = man
                    rows["Total Women"] = women
                    women_percentage = (women)/(man + women)
                    women_percentage = round(float(women_percentage*100),2)
                    rows["Women Percentage"] = women_percentage
                    csv_writer.writerow(rows)
                except:
                    if str(rows["Beta"]) == "NaN":
                        rows["Beta"] = 0
                    rows["Total Men"] = 0
                    rows["Total Women"] = 0
                    rows["Women Percentage"] = 0.0
                    # print(rows["Beta"])
                    csv_writer.writerow(rows)
                    pass




if __name__ == '__main__':
    papoulate_data()








