from src.core.errors import SchemaError

class TableSchema:
    def __init__(self, name, columns, composite_unique=None):
        self.name = name
        self.columns = {c.name: c for c in columns}
        self.composite_unique = composite_unique or []
        pks = [c for c in columns if c.primary_key]
        if len(pks) != 1:
            raise SchemaError(f"Table {name} must have exactly one PK")

    @property
    def pk_column(self):
        for c in self.columns.values():
            if c.primary_key:
                return c.name

    @property
    def unique_columns(self):
        return [c.name for c in self.columns.values() if c.unique and not c.primary_key]

