class SecondaryIndex:
    def __init__(self, column):
        self.column = column
        self._index = {}
    def build(self, rows):
        self._index = {}
        for row in rows:
            if not row.deleted:
                self._index.setdefault(row.data.get(self.column), []).append(row.row_id)
