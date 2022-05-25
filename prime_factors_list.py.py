from factor_list import find_factors

def find_primes(myList):
    prime_list = []
    for i in myList:
        if i >= 1:
            for j in range(2, i):
                if (i % j) == 0:
                    break
            else:
                prime_list.append(i)
    return prime_list

num_1 = int(input("Enter a number: "))
list_1 = find_factors(num_1)
list_2 = find_primes(list_1)

print(f"The prime numbers for {num_1} are: {list_2}")