def isPerfectCube(num):
    if num < 0:
        return False
    if num == 0:
        return True
    
    left, right = 1, num
    while left <= right:
        mid = (left + right) // 2
        cube = mid * mid * mid
        
        if cube == num:
            return True
        elif cube < num:
            left = mid + 1
        else:
            right = mid - 1
    
    return False

num = int(input("Enter a number: "))
if isPerfectCube(num):
    print(f"{num} is a perfect cube")
else:
    print(f"{num} is not a perfect cube")
