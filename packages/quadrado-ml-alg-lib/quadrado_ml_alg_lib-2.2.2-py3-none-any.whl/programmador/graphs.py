"""
Содержит алгоритмы работы с графами.
Использование:
    from graphs import dijkstra, topological_sort
"""
import heapq


def dijkstra(graph, start):
    """Алгоритм Дейкстры (O(E log V)). Возвращает кратчайшие пути.
    Формат графа: {узел: {сосед: вес}}
    Пример: dijkstra({'A':{'B':2,'C':1}}, 'A') → {'A':0,'B':2,'C':1}
    """
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    heap = [(0, start)]

    while heap:
        current_dist, current_node = heapq.heappop(heap)
        if current_dist > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    return distances


def topological_sort(graph):
    """Топологическая сортировка (O(V+E)). Для DAG.
    Пример: topological_sort({0:[1,2], 1:[3]}) → [0,1,2,3]
    """
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = [u for u in graph if in_degree[u] == 0]
    result = []
    while queue:
        u = queue.pop(0)
        result.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return result if len(result) == len(graph) else []