from fastapi import APIRouter, HTTPException
from prometheus_client import Counter, Gauge
import psutil
import datetime
from src.utils.logging_config import setup_logging

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
logger = setup_logging()

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
        # Add basic system checks
        system_healthy = all([
            psutil.cpu_percent() < 95,  # CPU not maxed out
            psutil.virtual_memory().percent < 95,  # Memory not maxed out
            psutil.disk_usage('/').percent < 95  # Disk not full
        ])
        
        return {
            "status": "healthy" if system_healthy else "degraded",
            "service": "duckdb-spawn-api",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "checks": {
                "cpu": "ok" if psutil.cpu_percent() < 95 else "warning",
                "memory": "ok" if psutil.virtual_memory().percent < 95 else "warning",
                "disk": "ok" if psutil.disk_usage('/').percent < 95 else "warning"
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