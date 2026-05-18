class PKIndex:
    def __init__(self, schema):
        self.pk_col = schema.pk_column
        self._index = {}
    def build(self, rows):
        self._index = {r.data.get(self.pk_col): r.row_id for r in rows if not r.deleted and r.data.get(self.pk_col) is not None}
    def lookup(self, pk_value):
        return self._index.get(pk_value)
