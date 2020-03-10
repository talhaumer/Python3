l1 = []
l2 = []
print("enter buckets cpacity")
n = int(input("enter range of inputs"))  
for i in range(0, n): 
    ele = int(input()) 
    l1.append(ele)

print("enter buckets filled out of total capacity")  
for b in range(0, n): 
    c = int(input()) 
    l2.append(c)


for i in range(len(l1)):
	for x in range(len(l2)):
		if l1[i] > l2[x]:
			print(l1[i])
			print(l2[x])
			l1[i] = l1[i] - l2[x]
			l2[x] = 0
			print(l1)
			print(l2)
			print(" ")
		elif l1[i] < l2[x]:
			print(l1[i])
			print(l2[x])
			l2[x] = l2[x] - l1[i]
			l1[i] = 0
			print("elif1 ")
			print(l1)
			print(l2)
			print(" ")
		elif l1[i] == l2[x]:
			print(l1[i])
			print(l2[x])
			l1[i] = 0
			l2[x] = 0
			print("elif2 ")
			print(l1)
			print(l2)
			print(" ")
		elif l1[i] == 0:
			print ("tiere is no capacity")
		x=x+1
	i=i+1