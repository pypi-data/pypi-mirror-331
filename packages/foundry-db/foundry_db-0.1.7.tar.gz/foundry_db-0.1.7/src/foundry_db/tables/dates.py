from .base_table import BaseTable, IDColumn
from ..enums import IDQueryTypes


class DatesTable(BaseTable):
    NAME: str = "dates"

    ID_COLUMN = str(IDColumn("ID"))

    DATE_COLUMN: str = "date"

    COLUMN_NAMES: list[str] = [DATE_COLUMN]

    ID_QUERY_TYPE = IDQueryTypes.BATCH
