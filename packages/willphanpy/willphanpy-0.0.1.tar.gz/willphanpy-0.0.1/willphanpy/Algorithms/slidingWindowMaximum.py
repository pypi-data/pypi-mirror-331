from collections import deque

def maxSlidingWindow(nums: list[int], k: int) -> list[int]:
    n = len(nums)
    result = []
    d = deque()
    i = 0 # Sliding window
    j = 0 # Slding window element

    while(i <= n - k):
        while(j <= i + k - 1):
            if(not d):
                d.append(j)
            else:
                while(d and nums[d[-1]] < nums[j]):
                    d.pop()

                d.append(j)

            j += 1
        
        result.append(nums[d[0]])
        i += 1
        if(d[0] < i):
            d.popleft()
    
    return result

r = maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3)
# r = maxSlidingWindow([1, -1], 1)
print(r)
# Expected [3, 3, 5, 5, 6, 7]
