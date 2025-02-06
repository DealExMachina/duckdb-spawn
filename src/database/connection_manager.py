import duckdb
from contextlib import contextmanager
import threading
import logging
import os
from typing import Generator, Optional
from threading import Lock

logger = logging.getLogger('data_product')

class DuckDBConnectionPool:
    def __init__(self, db_path: str = "data/data_product.db", max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections: list[duckdb.DuckDBPyConnection] = []
        self.lock = Lock()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        connection: Optional[duckdb.DuckDBPyConnection] = None
        
        with self.lock:
            if self.connections:
                connection = self.connections.pop()
            else:
                try:
                    connection = duckdb.connect(self.db_path)
                    logger.debug(f"Created new connection to {self.db_path}")
                except Exception as e:
                    logger.error(f"Failed to create database connection: {str(e)}")
                    raise
        
        if not connection:
            raise RuntimeError("Failed to get database connection")
            
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            with self.lock:
                try:
                    if len(self.connections) < self.max_connections and connection:
                        self.connections.append(connection)
                    elif connection:
                        connection.close()
                        logger.debug("Closed excess connection")
                except Exception as e:
                    logger.error(f"Error while returning connection to pool: {str(e)}")

class DuckDBConnectionManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DuckDBConnectionManager, cls).__new__(cls)
            cls._pool = DuckDBConnectionPool()
        return cls._instance

    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Get a connection from the pool."""
        with self._pool.get_connection() as conn:
            yield conn

    def close_all(self):
        """Close all connections in the pool."""
        with self._pool.lock:
            for conn in self._pool.connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {str(e)}")
            self._pool.connections.clear()