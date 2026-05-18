from typing import Any, Dict, Literal, Optional

RowId = str
ReplicaId = str
TableName = str
ColName = str
RowData = Dict[ColName, Any]
FKPolicy = Literal['cascade', 'tombstone', 'orphan']

class Row:
    def __init__(self, row_id: RowId, table: TableName, data: RowData, deleted: bool=False, delete_op_seq: Optional[int]=None):
        self.row_id = row_id
        self.table = table
        self.data = data
        self.deleted = deleted
        self.delete_op_seq = delete_op_seq

    def to_dict(self):
        return {'row_id': self.row_id, 'table': self.table, 'data': self.data, 'deleted': self.deleted, 'delete_op_seq': self.delete_op_seq}

    @classmethod
    def from_dict(cls, d):
        return cls(d['row_id'], d['table'], d['data'], d.get('deleted', False), d.get('delete_op_seq'))
