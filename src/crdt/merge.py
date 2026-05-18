from src.core.types import Row
from src.core.constants import OP_INSERT, OP_UPDATE, OP_DELETE

def merge_ops_to_rows(ops):
    col_registers = {}
    deleted_rows = {}
    insert_rows = {}
    tables = {}
    for op in sorted(ops, key=lambda o: (o.seq, o.actor_id)):
        tables[op.row_id] = op.table
        if op.op_type == OP_DELETE:
            prev = deleted_rows.get(op.row_id, ('', -1))
            if op.seq > prev[1] or (op.seq == prev[1] and op.actor_id < prev[0]):
                deleted_rows[op.row_id] = (op.actor_id, op.seq)
            continue
        if op.op_type == OP_INSERT:
            insert_rows[op.row_id] = max(insert_rows.get(op.row_id, -1), op.seq)
        if op.row_id not in col_registers:
            col_registers[op.row_id] = {}
        for col, val in op.data.items():
            prev = col_registers[op.row_id].get(col, (None, '', -1))
            if op.seq > prev[2] or (op.seq == prev[2] and op.actor_id < prev[1]):
                col_registers[op.row_id][col] = (val, op.actor_id, op.seq)
    result = {}
    for row_id in set(col_registers) | set(deleted_rows):
        data = {c: v[0] for c, v in col_registers.get(row_id, {}).items()}
        is_del = row_id in deleted_rows
        del_seq = deleted_rows[row_id][1] if is_del else None
        if is_del:
            if del_seq < insert_rows.get(row_id, -1):
                is_del = False
                del_seq = None
        result[row_id] = Row(row_id, tables.get(row_id, 'unknown'), data, is_del, del_seq)
    return result
