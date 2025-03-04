"""
Содержит математические алгоритмы.
Использование:
    from math_utils import sieve_of_eratosthenes
"""

def sieve_of_eratosthenes(n):
    """Решето Эратосфена (O(n log log n)).
    Возвращает список простых чисел ≤ n.
    Пример: sieve_of_eratosthenes(20) → [2,3,5,7,11,13,17,19]
    """
    if n < 2:
        return []
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            sieve[i*i : n+1 : i] = [False]*len(sieve[i*i : n+1 : i])
    return [i for i, is_prime in enumerate(sieve) if is_prime]