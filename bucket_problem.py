class WaterBucket:
    def __init__(self,container_size, container_filled ):
        self.container_filled = container_filled
        self.container_size = container_size


    def func(self):
        l1 = self.container_size
        l2 = self.container_filled
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
        print("remaining capacity>>>", l1)
        print("remaining quantity>>>", l2)


        
container_size = []
container_filled = []
print("enter buckets cpacity")
n = int(input("enter range of inputs: "))  
for i in range(0, n): 
    ele = int(input()) 
    container_size.append(ele)

print("enter buckets filled out of total capacity")  
for b in range(0, n): 
    c = int(input()) 
    container_filled.append(c)


obj = WaterBucket(container_size, container_filled)
obj.func()
