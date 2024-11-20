#!/bin/bash

echo "Checking container status..."
docker ps -a | grep duckdb-spawn

echo -e "\nChecking container logs..."
docker logs duckdb-spawn-api

echo -e "\nChecking API health..."
curl -f http://localhost:8000/monitoring/health || echo "API health check failed"

echo -e "\nChecking Prometheus metrics..."
curl -f http://localhost:8000/metrics || echo "Metrics endpoint failed"

echo -e "\nChecking directory permissions..."
ls -la data logs

echo -e "\nChecking if ports are in use..."
netstat -tulpn | grep -E '8000|9090' 