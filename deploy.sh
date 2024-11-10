#!/bin/bash

# Create necessary directories
mkdir -p data logs

# Initialize Pulumi stack if not exists
pulumi stack init dev

# Deploy the stack
pulumi up --yes

# Wait for containers to be ready
sleep 5

# Test the API health
curl $(pulumi stack output api_endpoint)/monitoring/health

echo "Deployment complete! Access points:"
echo "API: $(pulumi stack output api_endpoint)"
echo "Prometheus: $(pulumi stack output prometheus_endpoint)" 