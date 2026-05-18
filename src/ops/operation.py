class Op:
    def __init__(self, op_type, actor_id, seq, table, row_id, data=None, ts_ms=None):
        self.op_type = op_type
        self.actor_id = actor_id
        self.seq = seq
        self.table = table
        self.row_id = row_id
        self.data = data or {}
        self.ts_ms = ts_ms

    @property
    def op_id(self):
        return f"{self.actor_id}:{self.seq}"

    def to_dict(self):
        return {'op_type': self.op_type, 'actor_id': self.actor_id, 'seq': self.seq, 'table': self.table, 'row_id': self.row_id, 'data': self.data, 'ts_ms': self.ts_ms}

    @classmethod
    def from_dict(cls, d):
        return cls(d['op_type'], d['actor_id'], d['seq'], d['table'], d['row_id'], d.get('data', {}), d.get('ts_ms'))
