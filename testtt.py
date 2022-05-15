def read_how_many():
    user_input = int(input("Enter a number: "))
    return user_input

# print(read_how_many())




n = int(input("Enter a number: "))
def read_n_names(n):
    list = []
    for i in range(n):
        name = input("Enter a name: ")
        list.append(name)

    return list

# read_n_names(n)




myList = ['arstan', 'lina', 'pasha', 'marina']
def my_big_family(names):
    for name in names:
        names[names.index(name)] = name + " Churley"
    return names

# my_big_family(myList)
# print(myList)

print(my_big_family(read_n_names(read_how_many())))