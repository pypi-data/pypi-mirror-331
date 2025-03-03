# Сортировка
from sorting import quicksort
print(quicksort([3,1,4,2]))  # [1,2,3,4]

# Поиск
from search import binary_search
print(binary_search([1,3,5,7], 5))  # 2

# Графы
from graphs import dijkstra
graph = {'A': {'B':2,'C':1}, 'B': {'D':5}, 'C': {'D':3}}
print(dijkstra(graph, 'A'))  # {'A':0, 'B':2, 'C':1, 'D':4}

# DSU
from data_structures import DSU
dsu = DSU(5)
dsu.union(0,1)
print(dsu.find(0) == dsu.find(1))  # True

# Решето Эратосфена
from math_utils import sieve_of_eratosthenes
print(sieve_of_eratosthenes(20))  # [2,3,5,7,11,13,17,19]

# Дерево отрезков
from data_structures import SegmentTree
st = SegmentTree([1,3,5])
st.update(1, 5)
print(st.query(0,2))  # 1+5+5=11