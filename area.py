# write python program that calculate and display area  of the given shape 

try:
	value = input("Enter the triangle or rectangle: ")
	if value == "triangle":
		height = int(input("height of the triangle: "))
		base = int(input("base of the triangle: "))
		area = (height * base)/2
		print("Area of triangle is: ", area)
	elif value == "rectangle":
		height_rec = int(input("height of rectangle: "))
		width = int(input("Width of triangle: "))
		area_of_rectangle = height_rec * width
		print("print area of rectangle: ", area_of_rectangle)
	else:
		pass

except Exception as e:
	print(str(e))