import random
def random_list(length, a, b):
    list=[]
    count = 0
    while (count<length):
        number=random.randint(a,b)
        list.append(number)
        count = count + 1
    return list