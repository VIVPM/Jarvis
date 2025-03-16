def twoSum(nums, target):
    numMap = {}
    n = len(nums)

    for i in range(n):
        complement = target - nums[i]
        if complement in numMap:
            return [numMap[complement], i]
        numMap[nums[i]] = i
    return []

n = int(input("Enter the size of the array: "))
nums = []
print("Enter the elements of the array:")
for i in range(n):
    nums.append(int(input()))

target = int(input("Enter the target value: "))

result = twoSum(nums, target)
print(result)
