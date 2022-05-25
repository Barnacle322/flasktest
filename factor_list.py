def find_factors(x = 1637):
    factors_list = []
    for i in range(1, x + 1):
        if x % i == 0:
            factors_list.append(i)
    return factors_list

num_1 = int(input("Enter a number: "))

list_1 = find_factors(num_1)
collection_0 = find_factors()

print(list_1)
print(tuple(collection_0))