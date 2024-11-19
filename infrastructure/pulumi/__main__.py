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

# Get the absolute path to the prometheus config file
current_dir = os.path.dirname(os.path.abspath(__file__))
prometheus_config_path = os.path.join(current_dir, "config", "prometheus.yml")

# Create image with correct build configuration
image = docker.Image("my-image",
    build={
        "context": os.path.join(current_dir, "../../"),
        "dockerfile": "../../Dockerfile",
        "platform": "linux/arm64",
        "args": {
            "DOCKER_BUILDKIT": "1"
        }
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
    ports=[
        docker.ContainerPortArgs(
            internal=8000,
            external=api_port
        )
    ],
    network_mode=network.name,
    envs=[
        f"LOG_LEVEL={log_level}",
        f"ENVIRONMENT={environment}"
    ],
    memory=536870912,
    cpu_shares=100
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
    volumes=[docker.ContainerVolumeArgs(
        host_path=prometheus_config_path,
        container_path="/etc/prometheus/prometheus.yml",
        read_only=True
    )],
    memory=536870912,
    cpu_shares=100
)

# Export the endpoints
pulumi.export("api_endpoint", f"http://localhost:{api_port}")
pulumi.export("prometheus_endpoint", f"http://localhost:{prometheus_port}")