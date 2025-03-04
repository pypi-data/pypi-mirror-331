"""
Содержит реализации структур данных.
Использование:
    from data_structures import DSU, MinHeap, SegmentTree, Trie
"""
import heapq


class DSU:
    """Система непересекающихся множеств (DSU):
    - find: O(α(n)) (почти константа)
    - union: O(α(n))
    Пример:
        dsu = DSU(5)
        dsu.union(0,1)
        dsu.find(0) == dsu.find(1) → True
    """

    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [1] * size

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root != y_root:
            if self.rank[x_root] < self.rank[y_root]:
                self.parent[x_root] = y_root
            else:
                self.parent[y_root] = x_root
                if self.rank[x_root] == self.rank[y_root]:
                    self.rank[x_root] += 1


class MinHeap:
    """Min-Heap с основными операциями:
    - push: O(log n)
    - pop: O(log n)
    Пример:
        h = MinHeap()
        h.push(3), h.push(1)
        h.pop() → 1
    """

    def __init__(self):
        self.heap = []

    def push(self, val):
        heapq.heappush(self.heap, val)

    def pop(self):
        return heapq.heappop(self.heap) if self.heap else None


class SegmentTree:
    """Дерево отрезков для суммы (O(n) памяти):
    - update: O(log n)
    - query: O(log n)
    Пример:
        st = SegmentTree([1,2,3])
        st.query(0,2) → 6
        st.update(1,5)
        st.query(0,2) → 9
    """

    def __init__(self, data):
        self.n = len(data)
        self.size = 1
        while self.size < self.n:
            self.size <<= 1
        self.tree = [0] * (2 * self.size)
        self.tree[self.size:self.size + self.n] = data
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, pos, value):
        pos += self.size
        self.tree[pos] = value
        while pos > 1:
            pos >>= 1
            self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]

    def query(self, l, r):
        res = 0
        l += self.size
        r += self.size
        while l <= r:
            if l % 2 == 1:
                res += self.tree[l]
                l += 1
            if r % 2 == 0:
                res += self.tree[r]
                r -= 1
            l >>= 1
            r >>= 1
        return res


class Trie:
    """Префиксное дерево:
    - insert: O(L) (L - длина слова)
    Пример:
        t = Trie()
        t.insert("apple")
        t.search("app") → False
    """

    def __init__(self):
        self.root = {}
        self.end_symbol = '*'

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node[self.end_symbol] = True