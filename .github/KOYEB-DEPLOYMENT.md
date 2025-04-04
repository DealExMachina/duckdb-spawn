# Koyeb Deployment Troubleshooting Guide

This document provides detailed information about deploying to Koyeb and troubleshooting common issues, particularly related to Docker image access.

## Common Deployment Errors

### "Error while checking the validity of the docker image"

This error typically occurs when Koyeb cannot access the Docker image specified in the deployment configuration. This could be due to:

1. **The Docker image doesn't exist**
   - The image tag might be incorrect
   - The repository might not exist
   - The image might not have been pushed successfully

2. **Authentication issues**
   - The Docker registry secret might be incorrectly configured
   - The credentials might be incorrect or expired
   - The secret might not be properly associated with the deployment

3. **Registry path issues**
   - The image path might be incorrectly formatted
   - The registry domain might be missing or incorrect

## Troubleshooting Steps

### 1. Verify Docker Image Existence

```bash
# Check if the image exists locally
docker images | grep duckdb-spawn

# Try to pull the image to verify it's accessible
docker pull your-dockerhub-username/duckdb-spawn:your-tag

# List tags in your Docker Hub repository
curl -s "https://registry.hub.docker.com/v2/repositories/your-dockerhub-username/duckdb-spawn/tags?page_size=100" | jq
```

### 2. Check Koyeb Secret Configuration

```bash
# List existing secrets
koyeb secret list

# Get details about the Docker registry secret
koyeb secret get DOCKER_REPO_SECRET

# Delete and recreate the secret if needed
koyeb secret delete DOCKER_REPO_SECRET
koyeb secret create DOCKER_REPO_SECRET \
  --docker-registry-auth=username:password \
  --docker-registry-server=docker.io \
  --type=registry
```

### 3. Direct CLI Deployment

If the GitHub Action is failing, try deploying directly with the CLI:

```bash
# Create app if it doesn't exist
koyeb app create duckdb-spawn

# Create service with explicit image reference
koyeb service create api \
  --app duckdb-spawn \
  --docker docker.io/username/duckdb-spawn:tag \
  --docker-private-registry-secret DOCKER_REPO_SECRET \
  --ports 8000:http \
  --routes /:8000 \
  --env "DATABASE_URL=/data/duckdb_spawn.db PYTHONUNBUFFERED=1" \
  --instance-type nano \
  --regions fra

# Update existing service
koyeb service update api \
  --app duckdb-spawn \
  --docker docker.io/username/duckdb-spawn:tag \
  --docker-private-registry-secret DOCKER_REPO_SECRET
```

## Important Notes

### Docker Hub Rate Limits

Docker Hub has rate limits for image pulls:
- Anonymous: 100 pulls / 6 hours
- Free accounts: 200 pulls / 6 hours
- Pro accounts: Higher limits

If you're hitting rate limits, consider:
- Authenticating all pull requests
- Using a Pro account
- Implementing a container registry cache

### Docker Registry Credentials

Best practices for Docker Hub credentials:
1. Use access tokens instead of passwords
2. Create tokens with limited scope (read-only if possible)
3. Rotate tokens regularly
4. Store tokens securely in GitHub Secrets

### Koyeb Deployment Workflow

The updated workflow in this repository:
1. First tries to deploy using the GitHub Action
2. If that fails, falls back to direct CLI deployment
3. If that fails, attempts to update an existing service

This provides multiple paths to success with detailed error information at each stage.

## Reference Documentation

- [Koyeb Docker Deployment Documentation](https://www.koyeb.com/docs/docker-deploy)
- [GitHub Actions for Koyeb](https://www.koyeb.com/docs/deploy-with-github-actions)
- [Koyeb CLI Documentation](https://www.koyeb.com/docs/cli/installation-cli)
- [Docker Hub Authentication](https://docs.docker.com/docker-hub/access-tokens/) 