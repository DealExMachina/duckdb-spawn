"""Database connection management module.

This module implements a thread-safe connection pool for DuckDB, addressing key requirements
for a self-contained data product in a data mesh architecture:

1. Performance: Connection pooling reduces overhead for concurrent requests
2. Resource Efficiency: Reuses connections instead of creating new ones for each request
3. Reliability: Proper cleanup and error handling prevent resource leaks
4. Operational Independence: DuckDB's embedded nature eliminates external database dependencies

DuckDB was chosen specifically for this data product because:
- It provides analytical database capabilities without requiring server infrastructure
- Its columnar storage is optimized for the types of queries needed in project financing analytics
- The embedded architecture simplifies deployment and reduces operational complexity
- It maintains ACID compliance while providing excellent query performance
"""

import logging
import os
from contextlib import contextmanager
from threading import Lock
from typing import Generator, Optional

import duckdb

logger = logging.getLogger("data_product")


class DuckDBConnectionPool:
    """Pool of DuckDB connections."""

    def __init__(self, db_path: str = "data/data_product.db", max_connections: int = 5):
        """Initialize the connection pool.

        Args:
            db_path: Path to the DuckDB database file
            max_connections: Maximum number of connections to keep in the pool
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections: list[duckdb.DuckDBPyConnection] = []
        self.lock = Lock()

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """Get a connection from the pool."""
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
    """Singleton manager for DuckDB connections."""

    _instance = None
    _pool = None

    def __new__(cls):
        """Create or return the singleton instance."""
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
