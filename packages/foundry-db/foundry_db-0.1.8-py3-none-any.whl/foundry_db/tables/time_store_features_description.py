from .base_table import BaseTable, IDColumn
from ..enums import IDQueryTypes


class TimeStoreFeaturesDescriptionTable(BaseTable):
    NAME: str = "time_store_features_description"

    # "ID" is the primary key
    ID_COLUMN = str(IDColumn("ID"))

    DESCRIPTION_COLUMN = "description"
    NAME_COLUMN = "name"

    COLUMN_NAMES: list[str] = [NAME_COLUMN, DESCRIPTION_COLUMN]

    ID_QUERY_TYPE = IDQueryTypes.BATCH
