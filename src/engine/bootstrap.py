from src.schema.table_schema import TableSchema
from src.schema.column_schema import ColumnSchema
from src.schema.fk_schema import FKSchema

def load_schemas_and_fks():
    users = TableSchema('users', [
        ColumnSchema('id', 'str', nullable=False, primary_key=True),
        ColumnSchema('username', 'str', nullable=False, unique=True),
        ColumnSchema('name', 'str', nullable=True),
    ])
    posts = TableSchema('posts', [
        ColumnSchema('id', 'str', nullable=False, primary_key=True),
        ColumnSchema('user_id', 'str', nullable=True),
        ColumnSchema('title', 'str', nullable=False),
        ColumnSchema('body', 'str', nullable=True),
    ])
    schemas = {'users': users, 'posts': posts}
    fk_defs = [FKSchema('posts', 'user_id', 'users', 'id')]
    return schemas, fk_defs
