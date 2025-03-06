from ..tables import (
    BaseTable,
)
from ..enums import IDQueryTypes


class TableIDQueryBuilder:
    """
    Constructs SQL queries to retrieve record IDs from a table by matching attributes.
    Supports both single-row lookups and batch operations for multiple rows.
    """

    def __init__(self, table: BaseTable):

        self._table = table

        self.table_name = table.NAME
        self.id_column = table.ID_COLUMN
        self.column_names = table.COLUMN_NAMES
        self.query_type = table.ID_QUERY_TYPE

    def _build_single_row_query(self) -> str:
        """
        Builds a parameterized query for single-row ID retrieval using
        WHERE clause equality checks.

        Returns:
            SQL query string with placeholders for column values.
        """
        # Handle composite primary keys
        if isinstance(self.id_column, (list, tuple)):
            selected_ids = ", ".join(self.id_column)
        else:
            selected_ids = self.id_column

        where_clause = " AND ".join(f"{col} = %s" for col in self.column_names)
        return f"SELECT {selected_ids} FROM {self.table_name} WHERE {where_clause}"

    def _build_batch_query(self) -> str:
        """
        Builds a parameterized batch query using a JOIN with a VALUES clause to match
        multiple records efficiently in a single operation.

        Returns:
            SQL query string with placeholders for batch values.
        """
        columns_str = ", ".join(self.column_names)
        join_conditions = " AND ".join(
            [f"t.{col} = v.{col}" for col in self.column_names]
        )

        # Handle composite primary keys
        if isinstance(self.id_column, (list, tuple)):
            selected_ids = ", ".join(f"t.{col}" for col in self.id_column)
        else:
            selected_ids = f"t.{self.id_column}"

        return f"""
            SELECT {selected_ids}
            FROM {self.table_name} t
            JOIN (VALUES %s) AS v({columns_str})
            ON {join_conditions}
        """

    def build(self) -> str:
        """
        Constructs the appropriate SQL query based on the table's configured query type.

        Returns:
            Complete SQL query string ready for parameter binding.

        Raises:
            ValueError: If an unknown query type is specified.
        """

        if self.query_type == IDQueryTypes.SINGLE:
            return self._build_single_row_query()
        elif self.query_type == IDQueryTypes.BATCH:
            return self._build_batch_query()
        else:
            raise ValueError(f"Unsupported query type: {self.query_type}")
