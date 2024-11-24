import duckdb
from contextlib import contextmanager
import threading
import logging
import os

logger = logging.getLogger('data_product')

class DuckDBConnectionManager:
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.db_path = os.getenv('DUCKDB_PATH', 'data_product.db')
        self._local.connection = None

    @contextmanager
    def get_connection(self):
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            try:
                # Simplified connection with just read_only=False
                self._local.connection = duckdb.connect(
                    database=self.db_path,
                    read_only=False
                )
                logger.debug(f"Created new DuckDB connection to {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to connect to DuckDB: {str(e)}")
                raise

        try:
            yield self._local.connection
            self._local.connection.commit()  # Commit after successful operation
        except Exception as e:
            logger.error(f"Error during database operation: {str(e)}")
            if self._local.connection:
                self._local.connection.rollback()  # Rollback on error
            raise
        finally:
            # Close and reopen connection to prevent locks
            if self._local.connection:
                try:
                    self._local.connection.commit()
                    self._local.connection.close()
                    self._local.connection = None
                except Exception as e:
                    logger.error(f"Error closing connection: {str(e)}")

    def close_all(self):
        """Explicitly close all connections"""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            try:
                self._local.connection.close()
                self._local.connection = None
                logger.debug("Closed DuckDB connection")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")