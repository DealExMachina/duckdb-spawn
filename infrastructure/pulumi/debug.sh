#!/bin/bash
set -e

# Function to get container ID
get_container_id() {
    local CONTAINER_NAME=$1
    docker ps -q -f name=$CONTAINER_NAME
}

# Function to tail logs
tail_logs() {
    local CONTAINER_ID=$(get_container_id "duckdb-spawn-api")
    if [ -n "$CONTAINER_ID" ]; then
        echo "Tailing logs for duckdb-spawn-api..."
        docker logs -f $CONTAINER_ID
    else
        echo "Container duckdb-spawn-api is not running"
        exit 1
    fi
}

# Function to get a shell
get_shell() {
    local CONTAINER_ID=$(get_container_id "duckdb-spawn-api")
    if [ -n "$CONTAINER_ID" ]; then
        echo "Opening shell in duckdb-spawn-api..."
        docker exec -it $CONTAINER_ID /bin/sh
    else
        echo "Container duckdb-spawn-api is not running"
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [logs|shell]"
    exit 1
}

# Main
case "$1" in
    logs)
        tail_logs
        ;;
    shell)
        get_shell
        ;;
    *)
        usage
        ;;
esac 