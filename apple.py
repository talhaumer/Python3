# A basket can hold 5 apples . Write a python program that read total number of apples calculate and display the number basket need and number of apples that will be without basket 

basket = 5
total_number_of_apples = int(input("total number of apples: "))
total_basket_need = total_number_of_apples//basket
print("Total basket need: ", total_basket_need)
apples_remaining_without_basket = total_number_of_apples % basket
print("apples apples remaining without basket: ", apples_remaining_without_basket)