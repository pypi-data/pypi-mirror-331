import logging
from tqdm import tqdm
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings
from pathlib import Path
from typing import List, Optional, Tuple
from psycopg2 import Error as Psycopg2Error

# Configure logging as needed (this is just a basic config)
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
    def clean_params(params: list[tuple]) -> list[tuple]:
        return [
            tuple(int(x) if isinstance(x, np.integer) else x for x in row)
            for row in params
        ]

    def __init__(self, autocommit=False):
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

    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetchall: bool = False,
        fetchone: bool = False,
        commit: bool = False,
    ):
        if fetchall and fetchone:
            raise ValueError("Both fetchall and fetchone cannot be True")
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                result = (
                    cur.fetchall() if fetchall else cur.fetchone() if fetchone else None
                )
            if commit and self.autocommit:
                self.connection.commit()
            return result
        except Exception as e:
            error_msg = (
                f"Error executing query: {query}. Parameters: {params}. Exception: {e}"
            )
            logging.error(error_msg)
            raise Exception(error_msg) from e

    def execute_bulk_query(
        self,
        query: str,
        params: List[Tuple],
        fetchall: bool = False,
        chunk_size: int = 100,
        show_progress: bool = True,
    ) -> Optional[List]:
        """
        Execute a bulk query using the provided query string with a VALUES placeholder.
        The query is processed in chunks and all fetched results are returned.

        Args:
            query (str): A SQL query string that includes a VALUES %s placeholder.
            params (List[Tuple]): A list of tuples to be inserted into the query.
            fetchall (bool): If True, fetch all results from the query.
            chunk_size (int): Number of parameters to process per chunk. Defaults to 100.
            show_progress (bool): Whether to display a progress bar. Defaults to True.

        Returns:
            Optional[List]: Aggregated results if fetchall=True, else None. Returns [] if no params after cleaning and fetchall=True.
        """
        params = self.clean_params(params)
        if not params:
            return [] if fetchall else None

        all_results: List = []
        last_chunk = None

        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cur:
                iter_range = range(0, len(params), chunk_size)
                iterator = (
                    tqdm(iter_range, desc="Executing bulk query", unit="chunk")
                    if show_progress
                    else iter_range
                )
                for i in iterator:
                    chunk = params[i : i + chunk_size]
                    last_chunk = chunk
                    execute_values(cur, query, chunk, page_size=len(chunk))
                    if fetchall:
                        results = cur.fetchall()
                        all_results.extend(results)

                # Commit if the connection is not in autocommit mode
                if not self.connection.autocommit:
                    self.connection.commit()

            return all_results if fetchall else None

        except Psycopg2Error as e:
            error_msg = (
                f"Error executing bulk query. Query: {query}. "
                f"Last chunk processed: {last_chunk}. Exception: {e}"
            )
            logging.error(error_msg)
            # Re-raise with original exception as cause
            raise RuntimeError(error_msg) from e
