from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from .utils.logging_config import setup_logging
from .routes import admin, operations, monitoring
from .database.connection_manager import DuckDBConnectionManager
import datetime

# Setup logging
logger = setup_logging()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize database connection manager
db_manager = DuckDBConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application."""
    # Startup
    await db_manager.initialize_database()
    logger.info("Database initialized")
    yield
    # Shutdown
    try:
        db_manager.close_all()
        logger.info("Gracefully closed all database connections")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Initialize FastAPI app
app = FastAPI(
    title="DuckDB Data Product API",
    description="API for managing project financing data",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "dealexmachina.com",
        "*.dealexmachina.com",
        "localhost",
        "localhost:8000",
        "test"  # Allow test host for testing
    ]
)

# Register routes
app.include_router(admin.router)
app.include_router(operations.router)
app.include_router(monitoring.router)

# Initialize Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app)


@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to DuckDB Data Product API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_manager.get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        ) 