class FKIndex:
    def __init__(self, fk_schema):
        self.fk_schema = fk_schema
        self._index = {}
    def build(self, child_rows):
        self._index = {}
        for row in child_rows:
            if not row.deleted:
                ref = row.data.get(self.fk_schema.child_column)
                if ref:
                    self._index.setdefault(ref, []).append(row.row_id)
    def children_of(self, parent_id):
        return self._index.get(parent_id, [])
