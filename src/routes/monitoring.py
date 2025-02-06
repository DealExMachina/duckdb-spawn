"""Monitoring routes for the application."""

from typing import Dict

import psutil
from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    generate_latest,
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Initialize Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

RESPONSE_TIME = Gauge(
    "http_response_time_seconds",
    "HTTP response time in seconds",
    ["method", "endpoint"],
)

CPU_USAGE = Gauge("system_cpu_usage", "Current CPU usage percentage")
MEMORY_USAGE = Gauge("system_memory_usage", "Current memory usage percentage")
DISK_USAGE = Gauge("system_disk_usage", "Current disk usage percentage")


@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.1"}


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/metrics/system")
async def system_metrics() -> Dict:
    """System metrics endpoint."""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    CPU_USAGE.set(cpu)
    MEMORY_USAGE.set(memory)
    DISK_USAGE.set(disk)

    return {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
    }
