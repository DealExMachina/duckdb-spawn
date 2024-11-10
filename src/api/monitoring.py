from fastapi import APIRouter, HTTPException
from database.duckdb_manager import DuckDBManager
import logging
import psutil
from datetime import datetime
from prometheus_client import (
    Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST,
    Gauge
)
from fastapi.responses import Response
from prometheus_fastapi_instrumentator import Instrumentator

router = APIRouter()
db = DuckDBManager()
logger = logging.getLogger(__name__)

# Define Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

query_duration_seconds = Histogram(
    'query_duration_seconds',
    'Time spent executing database queries',
    ['query_type']
)

db_connections = Gauge(
    'db_connections_current',
    'Current number of database connections'
)

system_memory_usage = Gauge(
    'system_memory_usage_bytes',
    'Current system memory usage in bytes'
)

@router.get("/health")
async def health_check():
    try:
        db.execute_query("SELECT 1")
        logger.info("Health check successful")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/metrics")
async def metrics():
    # Update system metrics
    system_memory_usage.set(psutil.virtual_memory().used)
    
    # Generate Prometheus metrics
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/logs")
async def get_logs(limit: int = 100):
    try:
        with query_duration_seconds.labels(query_type='logs').time():
            query = f"""
            SELECT timestamp, level, message, service
            FROM system_logs 
            ORDER BY timestamp DESC 
            LIMIT {limit}
            """
            logs = db.execute_query(query)
            logger.info(f"Retrieved {len(logs)} log entries")
            return logs
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 