def func():
    user_input = int(input("Enter the number: "))
    myList = []
    for i in range(user_input):
        input_element = int(input("Enter the element: "))
        myList.append(input_element)
    return myList

print(func())