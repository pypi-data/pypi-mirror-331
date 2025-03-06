from .base_table import BaseTable, IDColumn
from ..enums import IDQueryTypes


class SkuTable(BaseTable):
    NAME: str = "sku_table"

    ID_COLUMN = str(IDColumn("ID"))

    PRODUCT_ID_COLUMN: str = str(IDColumn("productID"))
    STORE_ID_COLUMN: str = str(IDColumn("storeID"))

    COLUMN_NAMES: list[str] = [PRODUCT_ID_COLUMN, STORE_ID_COLUMN]

    ID_QUERY_TYPE = IDQueryTypes.BATCH