from src.core.constants import FK_CASCADE, FK_TOMBSTONE, FK_ORPHAN, NULL_SENTINEL
from src.core.errors import PolicyError

def apply_fk_policy(parent_rows, child_rows, fk_schema, policy):
    for child_row in child_rows:
        if child_row.deleted:
            continue
        ref_id = child_row.data.get(fk_schema.child_column)
        if ref_id is None or ref_id == NULL_SENTINEL:
            continue
        parent = parent_rows.get(ref_id)
        if parent is None or parent.deleted:
            if policy == FK_CASCADE:
                child_row.deleted = True
            elif policy == FK_TOMBSTONE:
                pass
            elif policy == FK_ORPHAN:
                child_row.data[fk_schema.child_column] = NULL_SENTINEL
            else:
                raise PolicyError(f'Unknown FK policy: {policy}')
    return child_rows
