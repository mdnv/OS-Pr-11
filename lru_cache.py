"""Дополнительный вопрос уровня C: LRU-кэш, get/put за O(1).

Хеш-таблица даёт поиск; двусвязный список — перестановку без обхода.
"""


class Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity должен быть положительным целым числом")
        self.capacity = capacity
        self.nodes = {}
        self.head = Node()  # перед head стоит самая давно использованная запись
        self.tail = Node()  # перед tail — самая свежая
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append(self, node):
        last = self.tail.prev
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    def _touch(self, node):
        self._remove(node)
        self._append(node)

    def get(self, key):
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self._touch(node)
        return node.value

    def put(self, key, value):
        if key in self.nodes:
            node = self.nodes[key]
            node.value = value
            self._touch(node)
            return
        if len(self.nodes) == self.capacity:
            old = self.head.next
            self._remove(old)
            del self.nodes[old.key]
        node = Node(key, value)
        self.nodes[key] = node
        self._append(node)


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    print("get(1):", cache.get(1))  # 100
    cache.put(3, 300)  # удалит ключ 2
    print("get(2):", cache.get(2))  # -1
    print("get(3):", cache.get(3))  # 300
