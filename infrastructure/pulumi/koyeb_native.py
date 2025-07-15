"""Koyeb deployment configuration using Pulumi with native Koyeb provider.

This module defines the infrastructure for deploying the DuckDB-SPAWN application to Koyeb
using the native Pulumi Koyeb provider instead of CLI commands."""

import pulumi
from pulumi import Config
import pulumi_koyeb as koyeb

# Get configuration
config = Config("duckdb-spawn")
environment = config.require("environment")
log_level = config.require("logLevel")
image_tag = config.get("imageTag", "latest")

# Docker registry configuration
registry_config = Config("registry")
registry_username = registry_config.require("username")
registry_password = registry_config.require_secret("password")

# Define the Docker image
docker_image = f"docker.io/{registry_username}/duckdb-spawn:{environment}-{image_tag}"

# Create Koyeb Provider
koyeb_provider = koyeb.Provider("koyeb-provider",
    token=config.require_secret("koyeb_token"),
)

# Create Koyeb app
app = koyeb.App("duckdb-spawn-app",
    name=f"duckdb-spawn-{environment}",
    opts=pulumi.ResourceOptions(provider=koyeb_provider)
)

# Create Koyeb Service
service = koyeb.Service("duckdb-spawn-service",
    app_name=app.name,
    name="api",
    definition=koyeb.ServiceDefinitionArgs(
        instance=koyeb.ServiceDefinitionInstanceArgs(
            type="nano",
            region="fra",
        ),
        ports=[koyeb.ServiceDefinitionPortArgs(
            port=8000,
            protocol="http",
        )],
        routes=[koyeb.ServiceDefinitionRouteArgs(
            path="/",
            port=8000,
        )],
        health_check=koyeb.ServiceDefinitionHealthCheckArgs(
            port=8000,
            path="/monitoring/health",
            protocol="http",
            initial_delay_seconds=20,
            timeout_seconds=10,
            period_seconds=30,
            success_threshold=1,
            failure_threshold=3,
        ),
        env_vars=[
            koyeb.ServiceDefinitionEnvVarArgs(
                key="DATABASE_URL",
                value="/data/duckdb_spawn.db",
            ),
            koyeb.ServiceDefinitionEnvVarArgs(
                key="PYTHONUNBUFFERED",
                value="1",
            ),
            koyeb.ServiceDefinitionEnvVarArgs(
                key="LOG_LEVEL",
                value=log_level,
            ),
            koyeb.ServiceDefinitionEnvVarArgs(
                key="ENVIRONMENT",
                value=environment,
            ),
        ],
        deployments=[koyeb.ServiceDefinitionDeploymentArgs(
            docker=koyeb.ServiceDefinitionDeploymentDockerArgs(
                image=docker_image,
                registry_auth=koyeb.ServiceDefinitionDeploymentDockerRegistryAuthArgs(
                    username=registry_username,
                    password=registry_password,
                ),
            ),
        )],
    ),
    opts=pulumi.ResourceOptions(provider=koyeb_provider, depends_on=[app])
)

# Export outputs
pulumi.export("app_name", app.name)
pulumi.export("service_name", service.name)
pulumi.export("environment", environment)
pulumi.export("image_tag", image_tag)
pulumi.export("docker_image", docker_image) 