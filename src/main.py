from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .utils.logging_config import setup_logging
from .routes import admin, operations, monitoring

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="DuckDB Data Product API",
    description="API for managing project financing data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(admin.router)
app.include_router(operations.router)
app.include_router(monitoring.router)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to DuckDB Data Product API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    } 