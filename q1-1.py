items_1 = int(input("price of an item 1: "))
items_2 = int(input("price of an item 2: "))

calculate_total = items_1 + items_2

print("total calculate values: ",calculate_total)

vat = 0.5

total = calculate_total * vat
print("vat total",total)