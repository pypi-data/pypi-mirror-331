from abc import ABC
from ..enums import IDQueryTypes


class BaseTable(ABC):
    NAME: str  # Table name
    ID_COLUMN: str  # ID column name
    COLUMN_NAMES: list[str]  # List of column names

    ID_QUERY_TYPE: IDQueryTypes


class IDColumn:

    def __init__(self, col_name: str):
        self.value = f'"{col_name}"'

    def __str__(self):
        return self.value
