# get stocks from file
# get industries against stock from YF
# get industries to values mapping from constant file

import sys
import getopt
import csv
import requests
import json
import pandas as pd
from os.path import isfile
from subprocess import PIPE, Popen
from scipy import stats
from constants_industry_values_formatter import *


class IndustryValuesFormatter():
	"""docstring for IndustryValuesFormatter"""
	def __init__(self, argv):
		self.argv = argv
		self.stocks_file_path = ""
		self.output_file_path = ""
		self.tickers = {}
		self.views = {}
		self.industry_values = []

	def user_input(self):
		script_path = self.argv[0]
		if len(self.argv) > 1:	
			cmd_args = self.argv[1:]
			try:
				opts, args = getopt.getopt(cmd_args,"hf:o:",["ifile=","ofile="])
			except getopt.GetoptError:
				print ("How to run: \npython3", script_path, " -f <stocks_file_path> -o <values_investing_file_path>")
				sys.exit(2)
			else:
				for opt, arg in opts:
					if opt == "-h":
						print ("How to run: \npython3", script_path, " -f <stocks_file_path> -o <values_investing_file_path>")
						sys.exit()
					elif opt in ("-f", "--ifile"):
						self.stocks_file_path = arg
					elif opt in ("-o", "--ofile"):
						self.output_file_path = arg
				
				if not self.stocks_file_path:
					print ("How to run: \npython3", script_path, " -f <stocks_file_path> -o <values_investing_file_path>")
					sys.exit()
				else:
					if isfile(self.stocks_file_path):
						print ("stocks_file_path file exist: ", self.stocks_file_path)
						# command = ''' awk -F "," '{print $1" " $2}' ''' + self.stocks_file_path
						# proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
						# out, err = proc.communicate()
						# self.tickers = out.decode().split("\n")
						reader = csv.DictReader(open(self.stocks_file_path))
						for row in reader:
							self.tickers[row['Symbol']] = row['Industry']
						
					else:
						print ("FileNotFoundError: [Errno 2] No such file or directory:", self.stocks_file_path)
						sys.exit()
		else:
			print ("How to run: \npython3", script_path, " -f <stocks_file_path> -o <values_investing_file_path>")
			sys.exit()


	def views_calculation(self):
		for ticker in self.tickers.keys():
			try:
				link='https://finance.yahoo.com/quote/{}/analysis?p={}'.format(ticker, ticker)
				df_est = pd.read_html(str(link))
				rev_est = df_est[1]
				view = (rev_est["Next Year (2022)"][5])
				if type(view) == str:
					self.views[ticker] = float(view.strip('%'))


			except:
				try:
					link='https://finance.yahoo.com/quote/{}/analysis?p={}'.format(ticker, ticker)
					df_est = pd.read_html(str(link))
					rev_est = df_est[1]
					view = (rev_est["Next Year (2021)"][5])
					if type(view) == str:
						self.views[ticker] = float(view.strip('%'))


				except:
					pass


	def find_industry(self):
		try:
			# industry = []
			error = []
			
			csvfile = open(self.output_file_path, 'w', newline='')
			csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
			csv_writer.writerow(['Ticker', 'Industry'] + VALUES)
			
			# self.tickers = []
			for ticker, industry in self.tickers.items():
				if ticker != "" and ticker != "Symbol":
					try:
						env_score, social_score, governance_score, percentile, controversy, adult, small_arms, animal_testing, nuclear, alcoholic, tobacco, gambling, palm_oil, controversial_weapons, fur_leather, gmo, catholic, coal, pesticides, military_contract, avg_volume, eps, marketcap, beta, view, esg = "","","","","","","","","","","","","","","","","","","","","","","","","",""

						querystring = {"symbol":ticker}
						response = requests.request("GET", url, headers=headers, params=querystring)
						response = json.loads(response.text)

						# if "summaryProfile" in response:
						# 	if "industry" in response["summaryProfile"]:
						# 		industry = response["summaryProfile"]["industry"]

						if "esgScores" in response:
							try:
								env_score = response["esgScores"]["environmentScore"]["fmt"]
								social_score = response["esgScores"]["socialScore"]["fmt"]
								governance_score =  response["esgScores"]["governanceScore"]["fmt"]
								percentile = response["esgScores"]["percentile"]["fmt"]
								controversy = response["esgScores"]["highestControversy"]

								# ----------------------
								# 7 values which exists in our set of values

								adult = response["esgScores"]["adult"]
								small_arms = response["esgScores"]["smallArms"]
								animal_testing = response["esgScores"]["animalTesting"]
								nuclear = response["esgScores"]["nuclear"]
								alcoholic = response["esgScores"]["alcoholic"]
								tobacco = response["esgScores"]["tobacco"]
								gambling = response["esgScores"]["gambling"]

								# ----------------------

								# 8 values which does not exist in our set of values
								palm_oil = response["esgScores"]["palmOil"]
								controversial_weapons = response["esgScores"]["controversialWeapons"]
								fur_leather = response["esgScores"]["furLeather"]
								gmo = response["esgScores"]["gmo"]
								catholic = response["esgScores"]["catholic"]
								coal = response["esgScores"]["coal"]
								pesticides = response["esgScores"]["pesticides"]
								military_contract = response["esgScores"]["militaryContract"]

								# ----------------------
							except Exception:
								pass

						# ---------- Summary Details
						avg_volume = response["summaryDetail"]["averageVolume"]["longFmt"]
						beta = response["summaryDetail"]["beta"]["fmt"]
						marketcap = response["summaryDetail"]["marketCap"]["longFmt"]
						# --------- EPS 
						eps = response["defaultKeyStatistics"]["trailingEps"]["raw"]


						# --------view of ticker
						if ticker in self.views:
							view = self.views[ticker]
						else:
							view = 0

						# --------ESG Score
						esg = float(env_score) + float(social_score) + float(governance_score)


						# ------------ ESG percentile
						self.industry_values.append(esg)
						
						# save as csv file
						csv_writer.writerow([ticker, industry, env_score, social_score, governance_score, percentile, controversy, adult, small_arms, animal_testing, nuclear, alcoholic, tobacco, gambling, palm_oil, controversial_weapons, fur_leather, gmo, catholic, coal, pesticides, military_contract, avg_volume, eps, marketcap, beta, view, esg])
					except Exception as e:
						csv_writer.writerow([ticker, ""])
						error.append({ticker:str(e)})

			csvfile.close()

		except Exception as e:
			print("Exception in find_industry: ", str(e))

	def cal_esg_percentile(self):
		data = pd.read_csv(self.output_file_path)
		col_names = list(data.columns)
		for item in col_names:
			if item == "ESG":
				percentiles = [stats.percentileofscore(self.industry_values, score) for score in self.industry_values]
				data[item] = [{"score" : self.industry_values[i], "percentile" : percentiles[i]} for i in range(len(self.industry_values))]
		i = 0
		csvfile=  open(self.output_file_path, 'r')
		csv_reader = csv.DictReader(csvfile)
		fieldnames = ["Ticker", "Industry","Environment score", "Social score", "Governance score", "Percentile", "Controversy", "Adult entertainment - negative","Firearms","Animal welfare","Nuclear power","Alcohol","Tobacco","Gambling","Palm oil","Controversial weapons","Fur leather","Gmo","Catholic","Coal","Pesticides","Military contract", "Avg Volume", "EPS", "Marcket cap", "Beta", "View", "ESG", "ESG_Percentile"]
		with open('/home/talha/Downloads/ESG_Percentile.csv', 'w') as new_file:
			csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
			csv_writer.writeheader()
			for rows in csv_reader:
				rows["ESG_Percentile"] = round(data["ESG"][i]["percentile"],2)
				csv_writer.writerow(rows)

	
	def women_owned(self):
		with open('/home/talha/Downloads/women', 'w') as new_file:
			fieldnames = ["Ticker", "Industry","Environment score", "Social score", "Governance score", "Percentile", "Controversy", "Adult entertainment - negative","Firearms","Animal welfare","Nuclear power","Alcohol","Tobacco","Gambling","Palm oil","Controversial weapons","Fur leather","Gmo","Catholic","Coal","Pesticides","Military contract", "Avg Volume", "EPS", "Marcket cap", "Beta", "View", "ESG", "ESG_Percentile", "Total Men", "Total Women", "Women Percentage"]
			csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
			csv_writer.writeheader()
			csvfile=  open('/home/talha/Downloads/ESG_Percentile.csv', 'r')
			csv_reader = csv.DictReader(csvfile)
			for rows in csv_reader:
				try:
					ticker = rows["Ticker"]
					link='https://finance.yahoo.com/quote/{}/profile?p={}'.format(ticker, ticker)
					df_est = pd.read_html(str(link))
					res = df_est[0]
					man = 0
					women = 0
					for name in res['Name']:
						if "Mr." in name:
							man += 1
						elif "Ms." in name:
							women += 1
						else:
							man += 1

					rows["Total Men"] = man
					rows["Total Women"] = women
					women_percentage = (women)/(man + women)
					women_percentage = round(float(women_percentage*100),2)
					rows["Women Percentage"] = women_percentage
					csv_writer.writerow(rows)
				except:
					rows["Total Men"] = 0
					rows["Total Women"] = 0
					rows["Women Percentage"] = 0.0
					csv_writer.writerow(rows)
					pass

if __name__ == "__main__":
	vt = IndustryValuesFormatter(sys.argv)
	vt.user_input()
	vt.views_calculation()
	vt.find_industry()
	vt.cal_esg_percentile()	 
	vt.women_owned()