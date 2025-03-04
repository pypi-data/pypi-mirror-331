import logging
from tqdm import tqdm
import psycopg2
from psycopg2.extras import execute_values
import numpy as np 

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from pathlib import Path

# Configure logging as needed (this is just a basic config)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class SQLDatabase:
    @staticmethod
    def get_db_credentials():
        """
        Fetch PostgreSQL database credentials from the Kedro configuration.
        Uses `OmegaConfigLoader` to load credentials stored under `credentials.postgres`.
        Returns:
            dict: A dictionary with the database connection details (e.g., host, port, user, password, dbname).
        """
        conf_path = str(Path(settings.CONF_SOURCE))
        conf_loader = OmegaConfigLoader(conf_source=conf_path)
        db_credentials = conf_loader["credentials"]["postgres"]
        return db_credentials

    @staticmethod
    def clean_rows(rows):
        return [
            tuple(int(x) if isinstance(x, np.integer) else x for x in row[:4])
            for row in rows
        ]

    def __init__(self, autocommit=True):
        self._credentials = self.get_db_credentials()["con"]
        self.connection = None
        self.autocommit = autocommit

    def connect(self):
        if not self.connection:
            self.connection = psycopg2.connect(self._credentials)
            self.connection.autocommit = self.autocommit

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
        elif not self.autocommit:
            self.connection.commit()
        self.close()

    def execute_query(self, query: str, params: tuple = None, fetchall: bool = False,
                      fetchone: bool = False, commit: bool = False):
        if fetchall and fetchone:
            raise ValueError("Both fetchall and fetchone cannot be True")
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchall() if fetchall else cur.fetchone() if fetchone else None
            if commit and self.autocommit:
                self.connection.commit()
            return result
        except Exception as e:
            error_msg = f"Error executing query: {query}. Parameters: {params}. Exception: {e}"
            logging.error(error_msg)
            raise Exception(error_msg) from e

    def execute_bulk_query(self, query: str, rows: list[tuple]) -> list:
        """
        Execute a bulk query using the provided query string with a VALUES placeholder.
        The query is processed in chunks and all fetched results are returned.
        
        Args:
            query (str): A SQL query string that includes a VALUES %s placeholder.
            rows (list[tuple]): List of rows (tuples) to be used as values.
            
        Returns:
            list: The aggregated results from executing the bulk query.
        """
        if not rows:
            return []
        
        rows = self.clean_rows(rows)
        all_results = []
        chunk_size = 100
        
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                for i in tqdm(range(0, len(rows), chunk_size), desc="Executing bulk query", unit="chunk"):
                    chunk = rows[i:i + chunk_size]
                    execute_values(cur, query, chunk, page_size=len(chunk))
                    results = cur.fetchall()
                    all_results.extend(results)
            return all_results
        except Exception as e:
            error_msg = f"Error executing bulk query. Query: {query}. Last chunk processed: {chunk}. Exception: {e}"
            logging.error(error_msg)
            raise Exception(error_msg) from e
