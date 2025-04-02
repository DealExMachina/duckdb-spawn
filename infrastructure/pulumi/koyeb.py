"""Koyeb deployment configuration using Pulumi.

This module defines the infrastructure for deploying the DuckDB-SPAWN application to Koyeb
using the Koyeb CLI through Pulumi's Command resource."""

import pulumi
from pulumi import Command, Config, ResourceOptions

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

# Install Koyeb CLI
install_cli = Command("install-koyeb-cli",
    create="curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | sh",
    update="curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | sh"
)

# Login to Koyeb
login_koyeb = Command("login-koyeb",
    create=f"koyeb login -t $KOYEB_TOKEN",
    environment={"KOYEB_TOKEN": config.require_secret("koyeb_token")},
    opts=ResourceOptions(depends_on=[install_cli])
)

# Create Koyeb app
create_app = Command("create-app",
    create=f"koyeb app create duckdb-spawn-{environment}",
    opts=ResourceOptions(depends_on=[login_koyeb])
)

# Deploy service to Koyeb
deploy_service = Command("deploy-service",
    create=f"""
        koyeb service create api \\
        --app duckdb-spawn-{environment} \\
        --docker {docker_image} \\
        --docker-private-registry-secret {registry_username}:{registry_password} \\
        --ports 8000:http \\
        --routes /:8000 \\
        --env DATABASE_URL=/data/duckdb_spawn.db \\
        --env PYTHONUNBUFFERED=1 \\
        --env LOG_LEVEL={log_level} \\
        --env ENVIRONMENT={environment} \\
        --instance-type nano \\
        --region fra \\
        --healthcheck /monitoring/health:8000
    """,
    opts=ResourceOptions(depends_on=[create_app])
)

# Export outputs
pulumi.export("app_name", f"duckdb-spawn-{environment}")
pulumi.export("service_name", "api")
pulumi.export("environment", environment)
pulumi.export("image_tag", image_tag)
pulumi.export("docker_image", docker_image) 