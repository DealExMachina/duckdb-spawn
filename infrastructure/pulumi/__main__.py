"""A Docker deployment for the DUCKDB-SPAWN data product"""

import pulumi
from pulumi_docker import Image, Container, Network, NetworkConfig, ContainerPortArgs

# Get configuration
config = pulumi.Config()
api_port = config.get_int("apiPort", 8000)
prometheus_port = config.get_int("prometheusPort", 9090)

# Create Docker network
network = Network("duckdb-spawn-network")

# Build and publish the API Docker image
api_image = Image("duckdb-spawn-api",
    build=pulumi.FileAsset("../../"),
    image_name="duckdb-spawn:latest",
    skip_push=True
)

# Create the API container
api_container = Container("duckdb-spawn-api",
    name="duckdb-spawn-api",
    image=api_image.base_image_name,
    ports=[ContainerPortArgs(
        internal=api_port,
        external=api_port
    )],
    networks_advanced=[NetworkConfig(
        name=network.name,
        aliases=["api"]
    )],
    envs=[
        "DATABASE_URL=/data/duckdb_spawn.db",
        "PROMETHEUS_MULTIPROC_DIR=/tmp"
    ],
    volumes=[{
        "host_path": "./data",
        "container_path": "/data"
    }, {
        "host_path": "./logs",
        "container_path": "/app/logs"
    }]
)

# Create Prometheus container
prometheus_container = Container("prometheus",
    name="duckdb-spawn-prometheus",
    image="prom/prometheus:latest",
    ports=[ContainerPortArgs(
        internal=9090,
        external=prometheus_port
    )],
    networks_advanced=[NetworkConfig(
        name=network.name,
        aliases=["prometheus"]
    )],
    volumes=[{
        "host_path": "./prometheus.yml",
        "container_path": "/etc/prometheus/prometheus.yml"
    }]
)

# Export the endpoints
pulumi.export('api_endpoint', f"http://localhost:{api_port}")
pulumi.export('prometheus_endpoint', f"http://localhost:{prometheus_port}") 