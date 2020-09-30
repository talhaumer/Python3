from pymongo import MongoClient
import collections 



client = MongoClient()
DB_ASSETS = client.assets_data

DB_USER = client.registered_users


values_list = ["Firearms" , "Animal welfare", "Controversial weapons","Gmo", "Military Contract" ,"Adult","Tobacco","Gambling","Alcohol"]
user_data = DB_USER['user_info'].find_one({"namespace" : "bst-Fy9a"})

if question_id == "qv2":
	if answer_id == 1:
		values_list.remove(Alcohol)
	elif answer_id == 2:
		values_list.remove(Tobacco)
	elif answer_id == 3:
		values_list.remove(Gambling)
	elif answer_id == 4:
		pass
	elif answer_id == 5:
		values_list.remove(Firearms)
		# values_list.remove(Controversial weapons)
	elif answer_id == 6:
		# values_list.remove(Adult entertainment)




drived_values = {}
all_derived_values = DB_VALUES["derived_values"].find_one({},{'_id': False})
for value in values_list:
	drived_values[str(value)] = {}
	drived_values[str(value)].update(all_derived_values[str(value)])


drived_values_list = []
for key,val in drived_values.items():
	drived_values_list.append(val)
u
counter = collections.Counter() 
for d in drived_values_list:  
	counter.update(d) 
	  
result = dict(counter)

total = len(drived_values_list)

for j in result:
	result[j] = (float)(result[j])/total  