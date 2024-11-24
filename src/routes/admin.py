from fastapi import APIRouter, HTTPException
from typing import Dict, Literal
from ..utils.metrics import table_creation_counter
import logging
import duckdb  # Import DuckDB
from pydantic import BaseModel

logger = logging.getLogger('data_product')
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

class LogLevelUpdate(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

@router.post("/logging/level")
async def set_log_level(level_update: LogLevelUpdate):
    """Update the application's logging level"""
    try:
        numeric_level = getattr(logging, level_update.level)
        logger = logging.getLogger('data_product')
        logger.setLevel(numeric_level)
        
        # Update all handlers to the new level
        for handler in logger.handlers:
            handler.setLevel(numeric_level)
            
        logger.info(f"Log level changed to {level_update.level}")
        return {"message": f"Logging level set to {level_update.level}"}
    except Exception as e:
        logger.error(f"Failed to update log level: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logging/level")
async def get_log_level():
    """Get the current logging level"""
    try:
        logger = logging.getLogger('data_product')
        return {"current_level": logging.getLevelName(logger.getEffectiveLevel())}
    except Exception as e:
        logger.error(f"Failed to get log level: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 