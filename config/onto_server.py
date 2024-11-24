import os
from typing import List, Optional
from pydantic import BaseModel
import httpx
from enum import Enum
import logging
from functools import lru_cache
from .mock_onto_responses import get_mock_response

logger = logging.getLogger('data_product')

# Configuration
ONTO_SERVER_URL = os.getenv('ONTO_SERVER_URL', 'http://localhost:8001')
ONTO_SERVER_TIMEOUT = int(os.getenv('ONTO_SERVER_TIMEOUT', '5'))  # seconds
USE_MOCK = os.getenv('USE_MOCK_ONTO_SERVER', 'true').lower() == 'true'

class ProjectStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

class SchemaColumn(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True

class ProjectSchema(BaseModel):
    name: str = "projects"
    columns: List[SchemaColumn]
    description: Optional[str] = None

# Cache for the schema
_schema_cache = None

async def fetch_schema_from_server(schema_id: str) -> dict:
    """Fetch schema from the onto server"""
    if USE_MOCK:
        logger.debug(f"Using mock response for schema: {schema_id}")
        return get_mock_response(schema_id)
        
    try:
        async with httpx.AsyncClient(timeout=ONTO_SERVER_TIMEOUT) as client:
            response = await client.get(f"{ONTO_SERVER_URL}/schemas/{schema_id}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch schema from onto server: {str(e)}")
        return get_mock_response(schema_id)  # Fallback to mock
    except Exception as e:
        logger.error(f"Unexpected error fetching schema: {str(e)}")
        return get_mock_response(schema_id)  # Fallback to mock

async def get_project_schema_jsonld() -> ProjectSchema:
    """Get the project schema definition with DuckDB compatible types"""
    global _schema_cache
    
    if _schema_cache is None:
        try:
            schema_data = await fetch_schema_from_server("project_schema")
            _schema_cache = ProjectSchema(**schema_data)
        except Exception as e:
            logger.error(f"Error getting project schema: {str(e)}")
            _schema_cache = ProjectSchema(**get_mock_response("project_schema"))
    
    return _schema_cache

def get_schema_columns() -> List[str]:
    """Helper function to get list of column names"""
    schema = get_mock_response("project_schema")
    return [col["name"] for col in schema["columns"]]

def get_required_columns() -> List[str]:
    """Helper function to get list of required column names"""
    schema = get_mock_response("project_schema")
    return [col["name"] for col in schema["columns"] if col["required"]]

# Health check for onto server
async def check_onto_server_health() -> bool:
    """Check if the onto server is available"""
    if USE_MOCK:
        return True
        
    try:
        async with httpx.AsyncClient(timeout=ONTO_SERVER_TIMEOUT) as client:
            response = await client.get(f"{ONTO_SERVER_URL}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Onto server health check failed: {str(e)}")
        return False
