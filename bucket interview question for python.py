filled = []
class WaterBucket:
    def __init__(self,container_size, container_filled, container_sizes):
        self.container_filled = container_filled
        self.container_size = container_size
        self.container_sizes = container_sizes

    def func(self):
        l1 = self.container_size
        l2 = self.container_filled
        print("capacity>>> ", l1)
        print("filled>>> ", l2)
        for i in range(len(l1)):
            for x in range(len(l2)):
                if l1[i] > l2[x]:
                    l1[i] = l1[i] - l2[x]
                    l2[x] = 0
                    
                elif l1[i] < l2[x]:
                    l2[x] = l2[x] - l1[i]
                    var1 = l2[x] + l1[i]
                    l1[i] = 0
                    
                elif l1[i] == l2[x]:
                    l1[i] = 0
                    l2[x] = 0

                elif l1[i] == 0:
                    print ("there is no capacity")
                x=x+1
            i=i+1
        print(" ")    
        print(".......................................................")
        print(" ")
        print("remaining capacity>>> ", l1)
        print("remaining quantity>>> ", l2)


    def fill(self):
    
    	l1 = self.container_sizes
    	l2 = self.container_size
    	zip_object = zip(l1, l2)
    	for i, x in zip_object: 
    		if i is not 0 and x is 0:
    			var = i
    			filled.append(var)
    		elif i == x:
    			filled.append(0)
    		elif i > x:
    			filled.append(i-x)
    	print("filled quantity>>>",filled)


container_sizes = []
container_size = []
container_filled = []
print("enter buckets cpacity")
n = int(input("enter range of inputs: "))  
for i in range(0, n): 
    ele = int(input()) 
    container_size.append(ele)
    container_sizes.append(ele)

print("enter buckets filled out of total capacity")  
for b in range(0, n): 
    c = int(input()) 
    container_filled.append(c)


obj = WaterBucket(container_size, container_filled, container_sizes)
obj.func()
obj.fill()