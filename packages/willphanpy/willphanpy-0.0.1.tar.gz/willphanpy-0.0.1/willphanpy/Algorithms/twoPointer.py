# The problem is given a sorted set of numbers and a target. Find two numbers in the set that add up to the target

def two_pointers(set, target):
    p1 = 0 # set pointer 1 to the beginning of the set
    p2 = len(set) - 1 # set pointer 2 to the end of the set

    while(p1 < p2):
        sum = set[p1] + set[p2]
        if(sum == target):
            return [set[p1], set[p2]]
        elif(sum < target):
            p1 += 1
        else:
            p2 -= 1

    return False

set = [1,3,5,10,34]
target = 8

print(two_pointers(set, target))
