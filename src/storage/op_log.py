import json, os
from src.ops.operation import Op

class OpLog:
    def __init__(self, path):
        self.path = path
        self.wm_path = path + '.wm'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, 'w').close()
        if not os.path.exists(self.wm_path):
            with open(self.wm_path, 'w') as f:
                json.dump({}, f)

    def append(self, op):
        with open(self.path, 'a') as f:
            f.write(json.dumps(op.to_dict()) + '\n')
            
        wm = self.watermark()
        wm[op.actor_id] = max(wm.get(op.actor_id, 0), op.seq)
        with open(self.wm_path, 'w') as f:
            json.dump(wm, f)

    def all_ops(self):
        out = []
        if not os.path.exists(self.path):
            return out
        try:
            with open(self.path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        out.append(Op.from_dict(json.loads(line)))
        except Exception:
            pass
        return out

    def watermark(self):
        if not os.path.exists(self.wm_path):
            return {}
        try:
            with open(self.wm_path, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception:
            pass
        return {}

    def next_seq(self, actor_id):
        wm = self.watermark()
        return max(wm.values() if wm else [0]) + 1

    def ops_not_seen_by(self, peer_watermark):
        return [op for op in self.all_ops() if op.seq > peer_watermark.get(op.actor_id, 0)]

    def clear(self):
        open(self.path, 'w').close()

    def bulk_append(self, ops):
        if not ops: return
        with open(self.path, 'a') as f:
            for op in ops:
                f.write(json.dumps(op.to_dict()) + '\n')
        
        wm = self.watermark()
        for op in ops:
            wm[op.actor_id] = max(wm.get(op.actor_id, 0), op.seq)
        with open(self.wm_path, 'w') as f:
            json.dump(wm, f)

    def compact(self):
        ops = self.all_ops()
        col_registers = {}
        deleted_rows = {}
        insert_rows = {}
        from src.core.constants import OP_DELETE, OP_INSERT
        
        for op in sorted(ops, key=lambda o: (o.seq, o.actor_id)):
            if op.op_type == OP_DELETE:
                prev = deleted_rows.get(op.row_id, ('', -1))
                if op.seq > prev[1] or (op.seq == prev[1] and op.actor_id < prev[0]):
                    deleted_rows[op.row_id] = (op.actor_id, op.seq, op)
                continue
            if op.op_type == OP_INSERT:
                prev = insert_rows.get(op.row_id, ('', -1))
                if op.seq > prev[1] or (op.seq == prev[1] and op.actor_id < prev[0]):
                    insert_rows[op.row_id] = (op.actor_id, op.seq, op)
            if op.row_id not in col_registers:
                col_registers[op.row_id] = {}
            for col, val in op.data.items():
                prev = col_registers[op.row_id].get(col, (None, '', -1, None))
                if op.seq > prev[2] or (op.seq == prev[2] and op.actor_id < prev[1]):
                    col_registers[op.row_id][col] = (val, op.actor_id, op.seq, op)

        winning_ops = set()
        for row_id, del_tuple in deleted_rows.items():
            winning_ops.add(del_tuple[2].op_id)
        for row_id, ins_tuple in insert_rows.items():
            winning_ops.add(ins_tuple[2].op_id)
            
        for row_id, cols in col_registers.items():
            for col, val_tuple in cols.items():
                winning_ops.add(val_tuple[3].op_id)
                
        compacted = [op for op in ops if op.op_id in winning_ops]
        self.clear()
        self.bulk_append(compacted)
