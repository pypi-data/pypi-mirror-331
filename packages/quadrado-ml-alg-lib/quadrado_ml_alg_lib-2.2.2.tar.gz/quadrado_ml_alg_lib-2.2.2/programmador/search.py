"""
Содержит алгоритмы поиска и обхода графов.
Использование:
    from search import binary_search, bfs
"""

def binary_search(arr, target):
    """Бинарный поиск (O(log n)). Требуется отсортированный массив.
    Пример: binary_search([1,3,5,7], 5) → 2
    """
    left, right = 0, len(arr)-1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def bfs(graph, start):
    """Поиск в ширину (O(V+E)). Возвращает достижимые вершины.
    Пример: bfs({0:[1,2], 1:[3], 2:[4]}, 0) → {0,1,2,3,4}
    """
    visited = set()
    queue = [start]
    while queue:
        vertex = queue.pop(0)
        if vertex not in visited:
            visited.add(vertex)
            queue.extend(n for n in graph[vertex] if n not in visited)
    return visited