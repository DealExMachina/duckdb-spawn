"""A Docker deployment for the DUCKDB-SPAWN data product.

This module defines the infrastructure for both the API and Prometheus monitoring
using Docker containers with persistent volumes and networking.

The deployment includes:
- API container with DuckDB backend
- Prometheus monitoring container
- Persistent volumes for data storage
- Docker network for container communication"""

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
image_tag = config.get("imageTag", "latest")

# Docker registry configuration
registry_config = Config("registry")
registry_username = registry_config.require("username")
registry_password = registry_config.require("password")

# Docker provider configuration
provider = docker.Provider("docker",
    host="unix:///var/run/docker.sock",
    registry_auth=[{
        "username": registry_username,
        "password": registry_password,
        "address": "docker.io"
    }]
)

# Docker image configuration
image_name = f"jeanbapt/duckdb-spawn:{image_tag}"

# Create network
network = docker.Network("duckdb-spawn-network",
    name="duckdb-spawn-network",
    driver="bridge",
    options={
        "com.docker.network.bridge.name": "duckdb-spawn",
        "com.docker.network.bridge.enable_icc": "true"
    },
    opts=pulumi.ResourceOptions(provider=provider)
)

# Create persistent volumes
db_volume = docker.Volume("duckdb-data",
    name="duckdb-data",
    driver="local",
    driver_opts={
        "type": "none",
        "device": os.path.join(os.path.dirname(__file__), "../../data"),
        "o": "bind"
    },
    opts=pulumi.ResourceOptions(provider=provider)
)

prometheus_volume = docker.Volume("prometheus-data",
    name="prometheus-data",
    driver="local",
    opts=pulumi.ResourceOptions(provider=provider)
)

# API Container setup
api_container = docker.Container("duckdb-spawn-api",
    name="duckdb-spawn-api",
    image=image_name,
    ports=[docker.ContainerPortArgs(
        internal=8000,
        external=api_port
    )],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(
        name=network.name,
        aliases=["api"]
    )],
    volumes=[docker.ContainerVolumeArgs(
        volume_name=db_volume.name,
        container_path="/app/data"
    )],
    envs=[
        f"LOG_LEVEL={log_level}",
        f"ENVIRONMENT={environment}",
        "PYTHONUNBUFFERED=1",
        "DATABASE_URL=/app/data/duckdb_spawn.db"  # Match Koyeb configuration
    ],
    healthcheck=docker.ContainerHealthcheckArgs(
        tests=["CMD", "curl", "-f", "http://localhost:8000/health"],
        interval="30s",
        timeout="10s",
        retries=3,
        start_period="20s"
    ),
    restart="unless-stopped",
    memory=536870912,  # 512MB in bytes
    cpu_shares=100,
    opts=pulumi.ResourceOptions(depends_on=[network, db_volume], provider=provider)
)

# Prometheus Container
prometheus_container = docker.Container("prometheus",
    name="prometheus",
    image="prom/prometheus:latest",
    ports=[docker.ContainerPortArgs(
        internal=9090,
        external=prometheus_port
    )],
    volumes=[
        docker.ContainerVolumeArgs(
            host_path=os.path.join(os.path.dirname(__file__), "config/prometheus.yml"),
            container_path="/etc/prometheus/prometheus.yml",
            read_only=True
        ),
        docker.ContainerVolumeArgs(
            volume_name=prometheus_volume.name,
            container_path="/prometheus"
        )
    ],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(
        name=network.name,
        aliases=["prometheus"]
    )],
    healthcheck=docker.ContainerHealthcheckArgs(
        tests=["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"],
        interval="30s",
        timeout="10s",
        retries=3,
        start_period="20s"
    ),
    restart="unless-stopped",
    memory=268435456,  # 256MB in bytes
    cpu_shares=50,
    opts=pulumi.ResourceOptions(depends_on=[network, prometheus_volume, api_container], provider=provider)
)

# Export the endpoints
pulumi.export("api_endpoint", f"http://localhost:{api_port}")
pulumi.export("prometheus_endpoint", f"http://localhost:{prometheus_port}")
pulumi.export("environment", environment)
pulumi.export("image_tag", image_tag)
pulumi.export("volumes", {
    "db_data": db_volume.name,
    "prometheus_data": prometheus_volume.name
})