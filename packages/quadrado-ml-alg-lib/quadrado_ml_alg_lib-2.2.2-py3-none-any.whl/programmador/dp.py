"""
Содержит примеры динамического программирования.
Использование:
    from dp import fibonacci, knapsack
"""

def fibonacci(n):
    """Динамическое программирование для чисел Фибоначчи (O(n)).
    Пример: fibonacci(10) → 55
    """
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

def knapsack(weights, values, capacity):
    """Рюкзак 0-1 (O(nW)).
    Пример: knapsack([2,3,4], [3,4,5], 5) → 7
    """
    n = len(weights)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for w in range(1, capacity+1):
            if weights[i-1] > w:
                dp[i][w] = dp[i-1][w]
            else:
                dp[i][w] = max(dp[i-1][w], values[i-1] + dp[i-1][w-weights[i-1]])
    return dp[n][capacity]
