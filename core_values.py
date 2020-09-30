from pymongo import MongoClient

client = MongoClient()
DB_ASSETS = client.assets_data



core_values = {'Adult entertainment': 0.0,'Alcohol': 0.0,'Animal welfare': 0.0,'Coal': 0.0,'Controversial weapons': 0.0,'Firearms': 0.0,'Fur leather': 0.0,'Gambling': 0.0, 'Gmo': 0.0,'Military Contract': 0.0,
 'Nuclear power': 0.0, 'Palm oil': 0.0,'Pesticides': 0.0,'Tobacco': 0.0}
myDictionary = { 'FB': 17.0, 'GOOGL': 1.0}

for keys in myDictionary.keys():
	data = DB_ASSETS["all_assets"].find_one({"ticker":str(keys)})
	# for key, val in data.items():
	# 	print(key)
	values = data["values"]
	# print(values)
	for key,val in values.items():
		if key in core_values:
			core_values[key] = values[key] + core_values[key]

total = 0

for j in core_values:
	core_values[j] = (float)(core_values[j])/total  