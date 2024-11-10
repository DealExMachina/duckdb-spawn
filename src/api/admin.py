from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from database.duckdb_manager import DuckDBManager
from pydantic import BaseModel

router = APIRouter()
db = DuckDBManager()

class TableSchema(BaseModel):
    table_name: str
    schema: Dict[str, str]

@router.post("/create_table")
async def create_table(table_schema: TableSchema):
    try:
        db.create_table(table_schema.table_name, table_schema.schema)
        return {"message": f"Table {table_schema.table_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
async def list_tables():
    try:
        result = db.execute_query("SELECT table_name FROM information_schema.tables")
        return {"tables": [row["table_name"] for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 