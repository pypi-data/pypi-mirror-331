from ..tables import BaseTable

class TableIDQueryBuilder:
    """
    Builds a query to fetch IDs from a table based on attribute matching.
    """
    def __init__(self, table: BaseTable):
        self.table = table

    def build(self) -> str:
        """Constructs the SQL query for fetching IDs."""
        table_name = self.table.NAME
        id_column = self.table.ID_COLUMN
        column_names = self.table.COLUMN_NAMES
        
        columns_str = ", ".join(column_names)
        join_clause = " AND ".join([f"t.{col} = v.{col}" for col in column_names])
        
        if isinstance(id_column, (list, tuple)):
            id_columns_str = ", ".join([f"t.{col}" for col in id_column])
        else:
            id_columns_str = f"t.{id_column}"
            
        query = f"""
            SELECT {id_columns_str}
            FROM {table_name} t
            JOIN (
                VALUES %s
            ) AS v({columns_str})
            ON {join_clause}
        """

        return query