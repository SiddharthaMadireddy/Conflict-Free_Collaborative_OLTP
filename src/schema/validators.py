from src.core.errors import SchemaError

def validate_row_data(table_schema, data, partial=False):
    for name, col in table_schema.columns.items():
        if name not in data:
            if not partial and not col.nullable and col.default is None:
                raise SchemaError(f"Missing NOT NULL column {name}")
            continue
        if not col.validate_value(data[name]):
            raise SchemaError(f"Invalid type for column {name}")
