import duckdb
from typing import List, Dict, Any
import logging
from uuid import uuid4
from datetime import datetime
from .schema import SCHEMA_DEFINITIONS

class DuckDBManager:
    def __init__(self, db_path: str = "data_product.db"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._initialize_schema()
        
    def _initialize_schema(self):
        for table_name, schema_sql in SCHEMA_DEFINITIONS.items():
            self.execute_query(schema_sql)
            logging.info(f"Initialized table: {table_name}")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        try:
            result = self.conn.execute(query, params if params else ()).fetchall()
            columns = self.conn.execute(query).description
            return [
                {columns[i][0]: value for i, value in enumerate(row)}
                for row in result
            ]
        except Exception as e:
            logging.error(f"Query execution error: {str(e)}")
            raise

    def create_project(self, project_data: Dict[str, Any]) -> str:
        project_id = str(uuid4())
        project_data.update({
            'project_id': project_id,
            'creation_date': datetime.now().date(),
            'last_updated': datetime.now()
        })
        
        columns = ', '.join(project_data.keys())
        placeholders = ', '.join(['?' for _ in project_data])
        query = f"INSERT INTO projects ({columns}) VALUES ({placeholders})"
        
        self.execute_query(query, tuple(project_data.values()))
        return project_id

    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> str:
        portfolio_id = str(uuid4())
        portfolio_data.update({
            'portfolio_id': portfolio_id,
            'inception_date': datetime.now().date(),
            'last_updated': datetime.now()
        })
        
        columns = ', '.join(portfolio_data.keys())
        placeholders = ', '.join(['?' for _ in portfolio_data])
        query = f"INSERT INTO portfolios ({columns}) VALUES ({placeholders})"
        
        self.execute_query(query, tuple(portfolio_data.values()))
        return portfolio_id

    def add_project_to_portfolio(self, portfolio_id: str, project_id: str, allocation: float):
        query = """
            INSERT INTO portfolio_projects (portfolio_id, project_id, allocation_percentage, entry_date)
            VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (portfolio_id, project_id, allocation, datetime.now().date()))