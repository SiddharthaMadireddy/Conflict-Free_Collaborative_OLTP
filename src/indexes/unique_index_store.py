class UniqueIndexStore:
    def __init__(self):
        self._index = {}
    def add(self, column, value, row_id):
        self._index.setdefault(column, {})[value] = row_id
    def lookup(self, column, value):
        return self._index.get(column, {}).get(value)
