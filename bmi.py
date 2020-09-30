# write python program to read weight in Kg and height in m and calculate BMI of person 
try:

	height_in_meters = float(input("Enter Heigt of person: "))
	weight_in_kg = int(input("Enter weight of person: "))
	BMI = weight_in_kg/height_in_meters**2
	print(" Body Mass Index: ",BMI)


except Exception as e:
	print(str(e))