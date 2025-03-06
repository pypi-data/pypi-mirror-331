from .base_table import BaseTable, IDColumn
from ..enums import IDQueryTypes


class ProductsTable(BaseTable):
    NAME: str = "products"

    ID_COLUMN = str(IDColumn("ID"))

    NAME_COLUMN: str = "name"

    COLUMN_NAMES: list[str] = [NAME_COLUMN]

    ID_QUERY_TYPE = IDQueryTypes.BATCH
