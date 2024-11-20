#!/bin/bash

# Create necessary directories
mkdir -p logs data

# Run FastAPI application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug 