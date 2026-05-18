from dataclasses import dataclass

@dataclass
class FKSchema:
    child_table: str
    child_column: str
    parent_table: str
    parent_column: str
