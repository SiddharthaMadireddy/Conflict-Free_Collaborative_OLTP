from src.core.types import Row
from src.constraints.unique_index import resolve_unique_conflicts
from src.schema.table_schema import TableSchema
from src.schema.column_schema import ColumnSchema

def test_unique_username_conflict():
    schema = TableSchema('users', [
        ColumnSchema('id','str',nullable=False,primary_key=True),
        ColumnSchema('username','str',nullable=False,unique=True),
    ])
    rows = [
        Row('u1','users',{'id':'u1','username':'alice'}),
        Row('u2','users',{'id':'u2','username':'alice'}),
    ]
    resolved = resolve_unique_conflicts(rows, schema)
    assert sum(1 for r in resolved if not r.deleted) == 1
