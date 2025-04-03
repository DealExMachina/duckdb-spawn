# DuckDB-Spawn CI/CD Pipeline

This document outlines the CI/CD workflows set up for the DuckDB-Spawn project.

## Overview

The project uses GitHub Actions for CI/CD with deployments to Koyeb for hosting. We have the following environments:

- **Production**: Main application deployed from the `main` branch
- **Staging**: Testing environment deployed from the `dev` branch
- **Preview**: Temporary environments for pull requests and feature development

## Workflows

### 1. CI/CD Pipeline (ci-cd.yml)

Handles continuous integration tasks including:
- Code formatting
- Linting
- Testing
- Building the Docker image

Triggered on push to `main` and `dev` branches, and on all pull requests to `main`.

### 2. Production Deployment (koyeb-deploy.yml)

Deploys the application to the production environment on Koyeb:
- Builds and pushes the Docker image
- Deploys the image to Koyeb
- Tags the image as `latest`

Triggered on push to the `main` branch.

### 3. Staging Deployment (staging-deploy.yml)

Deploys the application to the staging environment on Koyeb:
- Builds and pushes the Docker image with the `staging` tag
- Deploys the image to Koyeb staging environment

Triggered on push to the `dev` branch.

### 4. PR Preview Deployment (pr-preview.yml)

Creates temporary preview environments for pull requests:
- Builds and pushes a Docker image for the feature branch
- Deploys to a dedicated preview environment on Koyeb
- Comments on the PR with the deployment URL

Triggered on new and updated pull requests to `main` and `dev` branches.

### 5. Cleanup (cleanup.yml)

Removes temporary preview environments when branches are deleted:
- Cleans up Koyeb deployments
- Can be triggered manually for cleanup

Triggered on branch deletion events.

## Environment Setup

The following secrets need to be configured in GitHub:

- `DOCKER_HUB_USERNAME`: Your Docker Hub username
- `DOCKER_HUB_ACCESS_TOKEN`: Access token for Docker Hub
- `KOYEB_API_TOKEN`: API token for accessing Koyeb services
- `DOCKER_REPO_SECRET`: Secret for accessing private Docker repositories

## Infrastructure as Code

The `/infrastructure/pulumi` directory contains Pulumi infrastructure code for alternative deployment options:
- Docker-based local deployment
- Koyeb CLI deployment
- Koyeb native provider deployment

## Best Practices

1. **Branch Protection**: Enable branch protection for `main` and `dev` branches
2. **PR Reviews**: Require pull request reviews before merging
3. **Environment Deployment**: Use GitHub Environments for deployment approval
4. **Secrets Management**: Store all sensitive information in GitHub Secrets 