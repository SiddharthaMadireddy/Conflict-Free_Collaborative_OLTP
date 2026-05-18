from src.crdt.merge import merge_ops_to_rows
from src.constraints.conflict_resolver import ConflictResolver

class MaterializedView:
    def __init__(self, schemas, fk_defs, fk_policy):
        self.schemas = schemas
        self.fk_defs = fk_defs
        self.resolver = ConflictResolver(fk_policy)

    def build(self, ops):
        all_rows = merge_ops_to_rows(ops)
        table_rows = {}
        for row in all_rows.values():
            table_rows.setdefault(row.table, []).append(row)
        return self.resolver.resolve(table_rows, self.schemas, self.fk_defs)
