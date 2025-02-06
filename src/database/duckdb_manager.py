"""DuckDB database management module."""

import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from .connection_manager import DuckDBConnectionManager
from .schema import SCHEMA_DEFINITIONS

logger = logging.getLogger("data_product")


class DuckDBManager:
    """Manager for DuckDB database operations."""

    def __init__(self, db_path: str = "data_product.db"):
        """Initialize the DuckDB manager.

        Args:
            db_path: Path to the DuckDB database file
        """
        self.conn_manager = DuckDBConnectionManager()
        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize database schema."""
        for table_name, schema_sql in SCHEMA_DEFINITIONS.items():
            self.execute_query(schema_sql)
            logger.info(f"Initialized table: {table_name}")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries containing query results
        """
        try:
            with self.conn_manager.get_connection() as conn:
                result = conn.execute(query, params if params else ()).fetchall()
                columns = conn.execute(query).description
                return [
                    {columns[i][0]: value for i, value in enumerate(row)}
                    for row in result
                ]
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}", exc_info=True)
            raise

    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new project.

        Args:
            project_data: Project data dictionary

        Returns:
            Project ID
        """
        project_id = str(uuid4())
        project_data.update(
            {
                "project_id": project_id,
                "creation_date": datetime.now().date(),
                "last_updated": datetime.now(),
            }
        )

        columns = ", ".join(project_data.keys())
        placeholders = ", ".join(["?" for _ in project_data])
        query = f"INSERT INTO projects ({columns}) VALUES ({placeholders})"

        self.execute_query(query, tuple(project_data.values()))
        return project_id

    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> str:
        """Create a new portfolio.

        Args:
            portfolio_data: Portfolio data dictionary

        Returns:
            Portfolio ID
        """
        portfolio_id = str(uuid4())
        portfolio_data.update(
            {
                "portfolio_id": portfolio_id,
                "inception_date": datetime.now().date(),
                "last_updated": datetime.now(),
            }
        )

        columns = ", ".join(portfolio_data.keys())
        placeholders = ", ".join(["?" for _ in portfolio_data])
        query = f"INSERT INTO portfolios ({columns}) VALUES ({placeholders})"

        self.execute_query(query, tuple(portfolio_data.values()))
        return portfolio_id

    def add_project_to_portfolio(
        self, portfolio_id: str, project_id: str, allocation: float
    ):
        """Add a project to a portfolio.

        Args:
            portfolio_id: Portfolio ID
            project_id: Project ID
            allocation: Allocation percentage
        """
        query = """
            INSERT INTO portfolio_projects (
                portfolio_id,
                project_id,
                allocation_percentage,
                entry_date
            ) VALUES (?, ?, ?, ?)
        """
        self.execute_query(
            query, (portfolio_id, project_id, allocation, datetime.now().date())
        )
