from src.constraints.primary_key import resolve_pk_conflicts
from src.constraints.unique_index import resolve_unique_conflicts
from src.constraints.foreign_keys import apply_fk_policy

class ConflictResolver:
    def __init__(self, fk_policy):
        self.fk_policy = fk_policy

    def resolve(self, table_rows, schemas, fk_defs):
        for table, rows in table_rows.items():
            if table in schemas:
                table_rows[table] = resolve_pk_conflicts(rows, schemas[table])
        for table, rows in table_rows.items():
            if table in schemas:
                table_rows[table] = resolve_unique_conflicts(rows, schemas[table])
        for fk in fk_defs:
            parent_map = {r.row_id: r for r in table_rows.get(fk.parent_table, [])}
            child_rows = table_rows.get(fk.child_table, [])
            table_rows[fk.child_table] = apply_fk_policy(parent_map, child_rows, fk, self.fk_policy)
        return table_rows
