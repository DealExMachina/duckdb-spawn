"""A Docker deployment for the DUCKDB-SPAWN data product"""

import pulumi
from pulumi import Config
import pulumi_docker as docker
import os

# Get configuration
config = Config("duckdb-spawn")
api_port = config.require_int("apiPort")
prometheus_port = config.require_int("prometheusPort")
environment = config.require("environment")
log_level = config.require("logLevel")
resource_limits = config.require_object("resourceLimits")
container_registry = "registry"

# Create image - moved to top, before containers
image = docker.Image("my-image",
    build={
        "context": "../../",
        "dockerfile": "../../Dockerfile"
    },
    image_name=f"{container_registry}/duckdb-spawn-api:latest",
    skip_push=True
)

# Create network
network = docker.Network("duckdb-spawn-network",
    name="registry",
    driver="bridge"
)

# Create API container
api_container = docker.Container("duckdb-spawn-api",
    image=image.image_name,  # Reference the built image
    name="duckdb-spawn-api",
    ports=[{
        "internal": api_port,
        "external": api_port
    }],
    networks_advanced=[{
        "name": network.name
    }],
    envs=[
        f"LOG_LEVEL={log_level}",
        f"ENVIRONMENT={environment}"
    ],
    host_config={
        "cpus": float(resource_limits["cpus"]),
        "memory": resource_limits["memory"]
    }
)

# Create Prometheus container
prometheus_container = docker.Container("prometheus",
    image="prom/prometheus:latest",
    name="prometheus",
    ports=[{
        "internal": prometheus_port,
        "external": prometheus_port
    }],
    networks_advanced=[{
        "name": network.name
    }],
    volumes=[{
        "host_path": "./config/prometheus.yml",
        "container_path": "/etc/prometheus/prometheus.yml",
        "read_only": True
    }],
    host_config={
        "cpus": float(resource_limits["cpus"]),
        "memory": resource_limits["memory"]
    }
)

# Export the endpoints
pulumi.export("api_endpoint", f"http://localhost:{api_port}")
pulumi.export("prometheus_endpoint", f"http://localhost:{prometheus_port}")