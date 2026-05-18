from src.query.filters import all_rows
from src.query.joins import nested_loop_join

class QueryExecutor:
    def __init__(self, row_stores):
        self.row_stores = row_stores

    def select(self, table, where=all_rows, columns=None):
        rows = [r for r in self.row_stores.get(table, []) if not r.deleted and where(r)]
        return [{c: r.data.get(c) for c in columns} for r in rows] if columns else [dict(r.data) for r in rows]

    def join(self, left_table, right_table, left_key, right_key, where=all_rows):
        left_rows = [r for r in self.row_stores.get(left_table, []) if not r.deleted and where(r)]
        right_rows = [r for r in self.row_stores.get(right_table, []) if not r.deleted]
        return nested_loop_join(left_rows, right_rows, left_key, right_key)
