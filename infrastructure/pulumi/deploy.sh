#!/bin/bash
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check requirements
check_requirements() {
    echo "Checking required packages..."
    
    # Check for docker
    if ! command_exists docker; then
        echo "Docker is required but not installed"
        exit 1
    fi

    # Check for pulumi
    if ! command_exists pulumi; then
        echo "Pulumi is required but not installed"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    echo "Activating virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate

    echo "Installing Python dependencies..."
    pip install -r requirements.txt
}

# Cleanup existing containers
cleanup_containers() {
    echo "Cleaning up existing containers..."
    docker rm -f duckdb-spawn-api prometheus 2>/dev/null || true
}

# Set Docker context and platform
setup_docker() {
    echo "Setting Docker platform..."
    export DOCKER_DEFAULT_PLATFORM=linux/arm64
}

# Main deployment
deploy() {
    local STACK=$1
    if [ -z "$STACK" ]; then
        STACK="dev"
    fi

    echo "Deploying stack..."
    pulumi stack select $STACK
    pulumi up --yes
}

# Main
main() {
    check_requirements
    setup_venv
    setup_docker
    cleanup_containers
    deploy "$1"
}

main "$@"