"""
Содержит основные алгоритмы сортировки.
Использование:
    from sorting import quicksort, merge_sort
"""

def quicksort(arr):
    """Быстрая сортировка (средняя O(n log n)).
    Подходит для общего использования.
    Пример: quicksort([3,1,4,2]) → [1,2,3,4]
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

def merge_sort(arr):
    """Сортировка слиянием (O(n log n)).
    Стабильная сортировка, хорош для связанных списков.
    Пример: merge_sort([5,2,9,1]) → [1,2,5,9]
    """
    if len(arr) <= 1:
        return arr
    mid = len(arr)//2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def _merge(left, right):
    """Вспомогательная функция для сортировки слиянием"""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
