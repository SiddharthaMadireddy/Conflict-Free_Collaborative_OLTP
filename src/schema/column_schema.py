from dataclasses import dataclass

@dataclass
class ColumnSchema:
    name: str
    col_type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: str | None = None

    def validate_value(self, value):
        if value is None:
            return self.nullable
        type_map = {'str': str, 'int': int, 'float': float, 'bool': bool}
        expected = type_map.get(self.col_type)
        return True if expected is None else isinstance(value, expected)
