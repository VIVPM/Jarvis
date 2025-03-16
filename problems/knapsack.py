def knapsack(W, weights, values, n):
    dp = [[0 for x in range(W + 1)] for x in range(n + 1)]

    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                dp[i][w] = 0
            elif weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]],  dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    return dp[n][W]

values = [60, 100, 120]
weights = [10, 20, 30]
W = 50
n = len(values)
print("Maximum value:", knapsack(W, weights, values, n))

values = [10, 40, 30, 50]
weights = [5, 4, 6, 3]
W = 10
n = len(values)
print("Maximum value:", knapsack(W, weights, values, n))

values = [1, 2, 3]
weights = [4, 5, 1]
W = 4
n = len(values)
print("Maximum value:", knapsack(W, weights, values, n))

values = [4, 5, 3]
weights = [3, 1, 2]
W = 0
n = len(values)
print("Maximum value:", knapsack(W, weights, values, n))

values = [4, 5, 3]
weights = [3, 1, 2]
W = 5
n = len(values)
print("Maximum value:", knapsack(W, weights, values, n))
