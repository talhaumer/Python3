import psycopg2
from pymongo import MongoClient
from datetime import datetime
import time, json


client = MongoClient()
db = client['geo_location']


connection = psycopg2.connect(user = "semper",
							  password = "Cyt3x@310",
							  host = "127.0.0.1",
							  port = "5432",
							  database = "temp_dns_traffic")

def get_user():
	# users = db_users.distinct("namespace") 
	users = ['semp1']
	# for user in users:
	#     semp1.append(user)
	return users


def get_semp1_domain_ip_data(interval, namespace):

	try:
		table = "_".join([namespace, 'domain_ip_data'])
		query = '''
		SELECT ip,domain,category, COUNT(*) AS count
		FROM {}
		where eve_sec > now() - interval '{}' 
		GROUP BY ip, domain, category
		'''.format(table, interval)
		ip_data = None

		try:
			cursor = connection.cursor()
			cursor.execute(query)
			ip_data = cursor.fetchall()
			connection.commit()
			cursor.close()
		except Exception as e:
			print("Exception in ts: ", str(e))
			connection.commit()
			cursor.close()

		# category = []
		# for cat in ip_data:
		# 	if cat[2] not in category:
		# 		category.append(cat[2])
			
		# print(category)
		return ip_data
				  
	except Exception as e:
		print("Exception in fetch_traffic_data.py (fetch_traffic_cat_data method): ", str(e))
		return []


def get_ip_detail(ip_data, namespace, interval):
	res = {}
	try:
		table =  'ip_details'
		ips = ip_data
		# print(ips)
		for ip in ips:
			query = '''
			SELECT *
			FROM {}
			where ip = '{}' 
			limit '1' 
			-- GROUP BY ip
			'''.format(table, ip[0])
			ip_details = None
			try:
				cursor = connection.cursor()
				cursor.execute(query)
				ip_details = cursor.fetchall()
				connection.commit()
				cursor.close()
			except Exception as e:
				print("Exception in ts: ", str(e))
				connection.commit()
				cursor.close()
			if ip_details:
				
				ip_data = ip_details[0]
				
				country = ip_data[2]
				
				city = ip_data[3]
				
				domain = ip[1]

				category = ip[2]

				if category not in res.keys():
					res[category] = {}
					
				if country not in res[category].keys():
					res[category][country] = {}
					
				if city not in res[category][country].keys():
					res[category][country][city] = {}

				if domain not in res[category][country][city].keys():
					res[category][country][city][domain] = []

				res[category][country][city][domain].append({
					'ip': ip[0],
					'latitude':ip_data[4],
					'longitude': ip_data[5],
					'count': ip[3]
					})
				
		collection = db[".".join([namespace, interval])]
		categories = ['NETWORK', 'SOCIAL MEDIA', 'DATA', 'ADULT', 'ADWARE', 'MALWARE', 'PHISHING', 'E COMMERCE', 'CLOUD SERVICE', 'FINANCE', 'GAMING']
		for cat in categories:
			if cat in res.keys():
				data = res[cat]
			else:
				data = {}

		collection.insert({'category': cat, 'data': json.dumps(data)})
				
		# return ip_details

	except Exception as e:
		print("Exception in fetch_ip_detail.py (get_ip_detail_function): ", str(e))
		return []


if __name__ == '__main__':
	namespace = 'semp1'

	eve_secs = ["15 minutes","1 hour", "12 hours","1 day","7 days", "1 month"]
	for eve_sec in eve_secs:
		ip_data = get_semp1_domain_ip_data(eve_sec, namespace)
		ip = ip_data
		get_ip_detail(ip, namespace, eve_sec.replace(" ", "_"))
		print('\n -------------\n--------------\n')