from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..utils.metrics import table_creation_counter
import logging

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