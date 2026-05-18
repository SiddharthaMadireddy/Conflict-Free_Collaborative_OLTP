class AddWinsSet:
    def __init__(self):
        self._added = set()
        self._removed = set()

    def add(self, element):
        self._added.add(element)
        self._removed.discard(element)

    def remove(self, element):
        if element in self._added:
            self._removed.add(element)

    def contains(self, element):
        return element in self._added and element not in self._removed
