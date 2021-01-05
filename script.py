import csv
import pandas as pd
import yfinance as yf
from pymongo import MongoClient
import json

# column_names = ["Symbols"]
# df = pd.read_csv("tickers.csv", names=column_names)
# Symbols = df.Symbols.to_list()
# print(Symbols)

client  = MongoClient()
Symbols = [ 'RTRX', 'RUTH', 'RVNC', 'RVSB', 'RYAAY', 'SABR', 'SAFM', 'SAFT', 'SAGE', 'SAL', 'SALM', 'SAMG', 'SANM', 'SASR', 'SATS', 'SAVA', 'SBAC', 'SBBP', 'SBBX', 'SBCF', 'SBFG', 'SBGI', 'SBNY', 'SBPH', 'SBSI', 'SBUX', 'SCHN', 'SCKT', 'SCON', 'SCSC', 'SCVL', 'SCWX', 'SCYX', 'SEAC', 'SEEL', 'SEIC', 'SELB', 'SENEA', 'SENEB', 'SESN', 'SFBC', 'SFBS', 'SFNC', 'SFST', 'SGA', 'SGEN', 'SGH', 'SGLB', 'SGMA', 'SGMO', 'SGOC', 'SGRP', 'SHBI', 'SHEN', 'SHLO', 'SHSP', 'SIEB', 'SIFY', 'SIGA', 'SIGI', 'SILC', 'SIMO', 'SINA', 'SINO', 'SIRI', 'SITO', 'SIVB', 'SKYW', 'SLAB', 'SLCT', 'SLM', 'SLMBP', 'SLNO', 'SLP', 'SLRC', 'SLRX', 'SLS', 'SMBC', 'SMBK', 'SMCI', 'SMED', 'SMIT', 'SMMF', 'SMMT', 'SMRT', 'SMSI', 'SMTC', 'SMTX', 'SNCR', 'SNDE', 'SNDX', 'SNFCA', 'SNGX', 'SNLN', 'SNOA', 'SNPS', 'SNSS', 'SNY', 'SOHO', 'SOHOB', 'SOHU', 'SONA', 'SP', 'SPKE', 'SPKEP', 'SPLK', 'SPNS', 'SPOK', 'SPPI', 'SPRT', 'SPSC', 'SPWH', 'SRCE', 'SRCL', 'SRDX', 'SREV', 'SRNE', 'SRPT', 'SRRA', 'SSB', 'SSBI', 'SSNC', 'SSNT', 'SSP', 'SSSS', 'SSTI', 'SSYS', 'STAA', 'STAF', 'STAY', 'STBA', 'STCN', 'STFC', 'STKL', 'STKS', 'STLD', 'STMP', 'STND', 'STRM', 'STRT', 'STX', 'SUMR', 'SUNS', 'SUPN', 'SVBI', 'SVC', 'SVRA', 'SVVC', 'SWIR', 'SWKH', 'SWKS', 'SYBT', 'SYBX', 'SYKE', 'SYNA', 'SYNC', 'SYNH', 'SYNL', 'SYPR', 'SYRS', 'TA', 'TACO', 'TACT', 'TAIT', 'TANH', 'TAOP', 'TARA', 'TAST', 'TAYD', 'TBBK', 'TBK', 'TBNK', 'TBPH', 'TCBI', 'TCBIP', 'TCBK', 'TCCO', 'TCF', 'TCFC', 'TCOM', 'TCON', 'TCPC', 'TCRD', 'TCX', 'TEAM', 'TECD', 'TECH', 'TELL', 'TENX', 'TER', 'TESS', 'TEUM', 'TFSL', 'TGA', 'TGTX', 'THFF', 'THRM', 'THTX', 'TITN', 'TLF', 'TLGT', 'TLND', 'TMUS', 'TNAV', 'TNXP', 'TOUR', 'TOWN', 'TPIC', 'TRCH', 'TRHC', 'TRIB', 'TRIL', 'TRIP', 'TRMB', 'TRMK', 'TRNS', 'TROW', 'TRPX', 'TRS', 'TRST', 'TRVG', 'TRVN', 'TSBK', 'TSC', 'TSCO', 'TSEM', 'TSLA', 'TSRI', 'TTD', 'TTEC', 'TTGT', 'TTMI', 'TTNP', 'TTOO', 'TTWO', 'TURN', 'TWIN', 'TWMC', 'TWNK', 'TXMD', 'TXN', 'TXRH', 'TYHT', 'TYME', 'TZOO', 'UAL', 'UBCP', 'UBFO', 'UBOH', 'UBSI', 'UCBI', 'UCTT', 'UEPS', 'UFCS', 'UG', 'UHAL', 'UIHC', 'ULBI', 'ULTA', 'UMBF', 'UMPQ', 'UNAM', 'UNB', 'UNIT', 'UNTY', 'UONE', 'UONEK', 'UPLD', 'URBN', 'URGN', 'USAP', 'USEG', 'USIO', 'UTHR', 'UTMD', 'UTSI', 'UVSP', 'VALU', 'VBFC', 'VBIV', 'VBLT', 'VBTX', 'VC', 'VCEL', 'VCYT', 'VECO', 'VEON', 'VERB', 'VERI', 'VERU', 'VG', 'VIAV', 'VICR', 'VIRT', 'VISL', 'VIVO', 'VKTX', 'VLY', 'VNDA', 'VNET', 'VOD', 'VRNA', 'VRNS', 'VRNT', 'VRSK', 'VRSN', 'VRTS', 'VRTU', 'VRTX', 'VSAT', 'VSTM', 'VTGN', 'VTVT', 'VVUS', 'VXRT', 'VYGR', 'WABC', 'WAFD', 'WASH', 'WATT', 'WB', 'WBA', 'WDAY', 'WDC', 'WEN', 'WETF', 'WHF', 'WHLM', 'WHLR', 'WHLRP', 'WIFI', 'WINA', 'WING', 'WINS', 'WIX', 'WKHS', 'WLFC', 'WLTW', 'WNEB', 'WORX', 'WPRT', 'WRLD', 'WSBC', 'WSBF', 'WSC', 'WSFS', 'WSTG', 'WSTL', 'WTBA', 'WTER', 'WTFC', 'WTFCM', 'WTRH', 'WVE', 'WVFC', 'WYNN', 'XBIO', 'XBIT', 'XEL', 'XELA', 'XENE', 'XLNX', 'XLRN', 'XNCR', 'XOMA', 'XONE', 'XPER', 'XRAY', 'XTLB', 'YGYI', 'YIN', 'YNDX', 'YTRA', 'YVR', 'YY', 'Z', 'ZAGG', 'ZBRA', 'ZEUS', 'ZG', 'ZGNX', 'ZION', 'ZIOP', 'ZIXI', 'ZN', 'ZNGA', 'ZSAN', 'ZUMZ', 'ZYNE', 'A', 'AA', 'AAL']

companies = []
rows = {}
for i in Symbols:
	try:
		companies = []
		data = yf.Ticker(i)
		d = data.info['longName']
		rows["ticker"] = i
		rows["company_name"] = d
		print(rows)
		json.dump(rows, open('1.json', 'w'))
		
	except:
		pass


# # print(companies)
# # client = MongoClient()
# # db = client.company_names
# db.companies.insert_many(companies)