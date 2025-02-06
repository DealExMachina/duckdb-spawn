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

# Configure CORS with specific allowed origins
allowed_origins = [
    "https://dealexmachina.com",
    "https://data-product-101.dealexmachina.com",
    # Include development URLs if needed
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
    expose_headers=[
        "Content-Length",
        "Content-Range"
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
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