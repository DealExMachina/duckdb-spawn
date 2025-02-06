FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy only the application requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and config
COPY src/ src/
COPY config/ config/

# Create directories for data and logs with proper permissions
RUN mkdir -p /data /app/logs && chmod 777 /data /app/logs

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app /data
USER appuser

# Expose the port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=/app/data/duckdb_spawn.db

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]