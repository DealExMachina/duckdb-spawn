from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..utils.metrics import table_creation_counter
import logging
import duckdb  # Import DuckDB

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/tables")
async def create_table(table_name: str, schema: Dict[str, str]):
    """Create a new table in DuckDB"""
    try:
        # TODO: Implement DuckDB table creation
        # After successful table creation:
        table_creation_counter.labels(status='success').inc()
        logger.info(f"Table {table_name} created successfully")
        return {"message": f"Table {table_name} created successfully"}
    except Exception as e:
        table_creation_counter.labels(status='failed').inc()
        logger.error(f"Failed to create table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tables/{table_name}")
async def update_table(table_name: str, schema: Dict[str, str]):
    """Update an existing table in DuckDB"""
    try:
        # TODO: Implement DuckDB table update logic
        # After successful table update:
        table_creation_counter.labels(status='updated').inc()
        logger.info(f"Table {table_name} updated successfully")
        return {"message": f"Table {table_name} updated successfully"}
    except Exception as e:
        table_creation_counter.labels(status='update_failed').inc()
        logger.error(f"Failed to update table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tables/{table_name}")
async def delete_table(table_name: str):
    """Delete an existing table in DuckDB"""
    try:
        # TODO: Implement DuckDB table deletion logic
        # After successful table deletion:
        table_creation_counter.labels(status='deleted').inc()
        logger.info(f"Table {table_name} deleted successfully")
        return {"message": f"Table {table_name} deleted successfully"}
    except Exception as e:
        table_creation_counter.labels(status='deletion_failed').inc()
        logger.error(f"Failed to delete table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
async def list_tables():
    """List all tables in DuckDB"""
    try:
        # Connect to the DuckDB database
        conn = duckdb.connect('data_product.db')
        
        # Execute the query to list tables
        result = conn.execute("PRAGMA show_tables").fetchall()
        
        # Extract table names from the result
        tables = [row[0] for row in result]
        
        logger.info("Retrieved list of tables successfully")
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Failed to retrieve list of tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 