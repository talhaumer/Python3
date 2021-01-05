from pymongo import MongoClient
import collections 



client = MongoClient()
DB_ASSETS = client.assets_data
DB_VALUES = client.db_values
DB_USER = client.registered_users
values_list = ["Firearms" , "Animal welfare", "Controversial weapons","Gmo", "Military Contract" ,"Adult entertainment","Tobacco","Gambling","Alcohol"]

NAMPESPACE = "uk-DdZ0"

weights = { 'AMZN': 20.0, 'FB': 17.0, 'GOOGL': 1.0}

def drived_values(values_list, NAMPESPACE, myDictionary):
	try:
		user_data = DB_USER['user_info'].find_one({"namespace" : NAMPESPACE})
		for key,val in user_data.items():
			if key == "questionaire":
				questionaire = val
				for k, v in questionaire.items():
					if k == "data":
						print(k, v)
						dicts = v
		# print(dicts)
		question = next(item for item in dicts if item["question_id"] == "qv2")

		# print(question)
		for key,val in question.items():
			if key =="answer_id":
				answer = val

		print(answer)
		for itm in answer:
			if itm == "a":
				values_list.remove("Alcohol")
			elif itm == "b":
				values_list.remove("Tobacco")
			elif itm == "c":
				values_list.remove("Gambling")
			elif itm == "d":
					pass
			elif answer_id == "e":
				values_list.remove("Firearms")
				values_list.remove("Controversial weapons")
			elif answer_id == "f":
				values_list.remove("Adult entertainment")


		drived_values = {}
		all_derived_values = DB_VALUES["derived_values"].find_one({},{'_id': False})
		for value in values_list:
			drived_values[str(value)] = {}
			drived_values[str(value)].update(all_derived_values[str(value)])


		drived_values_list = []
		for key,val in drived_values.items():
			drived_values_list.append(val)


		counter = collections.Counter() 
		for d in drived_values_list:  
			counter.update(d) 
			  
		result = dict(counter)

		total = len(drived_values_list)

		for j in result:
			result[j] = round((float)(result[j])/total, 2)

		# print(result)

		# Finding the core values
		core_values = {'Adult entertainment': 0.0,'Alcohol': 0.0,'Animal welfare': 0.0,'Coal': 0.0,'Controversial weapons': 0.0,'Firearms': 0.0,'Fur leather': 0.0,'Gambling': 0.0, 'Gmo': 0.0,'Military Contract': 0.0,
		'Nuclear power': 0.0, 'Palm oil': 0.0,'Pesticides': 0.0,'Tobacco': 0.0}
		# print(1)
		for keys in myDictionary.keys():
			# print(2)
			data = DB_ASSETS["all_assets"].find_one({"ticker":str(keys)})
			# print(3)
			# print(data)
			if data:			
				values = data["values"]
				for key,val in values.items():
					if key in core_values:
						core_values[key] = values[key] + core_values[key]			

		total = len(myDictionary)

		for j in core_values:
			core_values[j] = round((float)(core_values[j])/total, 2)

		if core_values != None:
			# print("111111111111111111")
			result.update(core_values)

		print(result, "1")	
		return result
	except Exception as e:
		print(str(e))

if __name__ == '__main__':
	drived_values(values_list, NAMPESPACE, weights)
	