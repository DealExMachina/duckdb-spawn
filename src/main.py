from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import admin, operations, monitoring
from auth.jwt_handler import auth_middleware
from prometheus_fastapi_instrumentator import Instrumentator
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

app = FastAPI(title="Data Product API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Setup Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(operations.router, prefix="/ops", tags=["Operations"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Data Product API is running"} 