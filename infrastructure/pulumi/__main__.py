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

# Create network
network = docker.Network("duckdb-spawn-network",
    name="duckdb-spawn-network",
    driver="bridge"
)

# Build the Docker image
image_name = f"{config.get('registry', 'localhost')}/duckdb-spawn:{environment}"
duckdb_spawn_image = docker.Image(
    "duckdb-spawn-image",
    build={
        "context": "../..",
        "dockerfile": "../../Dockerfile"
    },
    image_name="duckdb-spawn:latest",
    skip_push=True
)

# API Container setup
api_container = docker.Container("duckdb-spawn-api",
    name="duckdb-spawn-api",
    image=duckdb_spawn_image.base_image_name,
    ports=[docker.ContainerPortArgs(
        internal=8000,
        external=api_port
    )],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(
        name=network.name,
        aliases=["api"]
    )],
    envs=[
        f"LOG_LEVEL={log_level}",
        f"ENVIRONMENT={environment}",
        "PYTHONUNBUFFERED=1"
    ],
    memory=536870912,
    cpu_shares=100,
    opts=pulumi.ResourceOptions(depends_on=[network])
)

# Prometheus Container
prometheus_container = docker.Container("prometheus",
    name="prometheus",
    image="prom/prometheus:latest",
    ports=[docker.ContainerPortArgs(
        internal=9090,
        external=prometheus_port
    )],
    volumes=[docker.ContainerVolumeArgs(
        host_path=os.path.join(os.path.dirname(__file__), "config/prometheus.yml"),
        container_path="/etc/prometheus/prometheus.yml",
        read_only=True
    )],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(
        name=network.name,
        aliases=["prometheus"]
    )],
    opts=pulumi.ResourceOptions(depends_on=[network, api_container])
)

# Export the endpoints
pulumi.export("api_endpoint", f"http://localhost:{api_port}")
pulumi.export("prometheus_endpoint", f"http://localhost:{prometheus_port}")
pulumi.export("environment", environment)