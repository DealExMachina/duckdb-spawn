from fastapi import APIRouter, HTTPException
from prometheus_client import Counter, Gauge
import psutil
import datetime
import logging
from config.onto_server import check_onto_server_health

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = logging.getLogger('data_product')

# Define Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# System metrics gauges
cpu_usage_gauge = Gauge('cpu_usage_percent', 'CPU Usage Percentage')
memory_usage_gauge = Gauge('memory_usage_percent', 'Memory Usage Percentage')
disk_usage_gauge = Gauge('disk_usage_percent', 'Disk Usage Percentage')

@router.get("/health")
async def health_check():
    """Health check endpoint with enhanced status information"""
    try:
        # System checks
        system_healthy = all([
            psutil.cpu_percent() < 95,
            psutil.virtual_memory().percent < 95,
            psutil.disk_usage('/').percent < 95
        ])
        
        # Check onto server health
        onto_server_healthy = await check_onto_server_health()
        
        overall_status = "healthy" if (system_healthy and onto_server_healthy) else "degraded"
        
        return {
            "status": overall_status,
            "service": "duckdb-spawn-api",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "checks": {
                "cpu": "ok" if psutil.cpu_percent() < 95 else "warning",
                "memory": "ok" if psutil.virtual_memory().percent < 95 else "warning",
                "disk": "ok" if psutil.disk_usage('/').percent < 95 else "warning",
                "onto_server": "ok" if onto_server_healthy else "error"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/metrics/system")
async def system_metrics():
    """Get detailed system metrics"""
    try:
        # Collect metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Update Prometheus gauges
        cpu_usage_gauge.set(cpu_percent)
        memory_usage_gauge.set(memory.percent)
        disk_usage_gauge.set(disk.percent)
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        }
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to collect system metrics"
        ) 