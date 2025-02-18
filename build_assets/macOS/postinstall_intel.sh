#!/bin/bash

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if running on Intel Mac
if [ "$(uname -m)" != "x86_64" ]; then
    log_message "Error: This script is for Intel-based Macs only."
    exit 1
fi

# Function to check if an application is running
is_app_running() {
    app_name=$1
    pgrep -x "$app_name" >/dev/null
}

# Function to attempt opening Docker with retries
open_docker_with_retry() {
    max_attempts=5
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        log_message "Attempt $attempt to open Docker.app"
        if [ -d "/Applications/Docker.app" ]; then
            if open -a "Docker.app" 2>/dev/null; then
                log_message "Docker.app opened successfully"
                return 0
            else
                log_message "Failed to open Docker.app, waiting before retry..."
            fi
        else
            log_message "Docker.app not found in /Applications"
        fi
        sleep 10
        attempt=$((attempt+1))
    done
    log_message "Failed to open Docker.app after $max_attempts attempts"
    return 1
}

# Main script starts here
log_message "Starting post-install script"

# Wait for a bit to ensure Docker installation is complete
log_message "Waiting for 30 seconds to ensure Docker installation is complete..."
sleep 30

# Attempt to open Docker
if ! open_docker_with_retry; then
    log_message "Warning: Could not open Docker.app. It may need to be opened manually."
fi

# Set the timeout duration (in seconds)
timeout=300  # 5 minutes

# Wait for Docker Desktop to be running
log_message "Waiting for Docker Desktop to start..."
start_time=$(date +%s)
while ! is_app_running "Docker Desktop"; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [ $elapsed_time -ge $timeout ]; then
        log_message "Warning: Docker Desktop did not start within the specified timeout."
        break
    fi

    sleep 5
done

if is_app_running "Docker Desktop"; then
    log_message "Docker Desktop is running."
else
    log_message "Warning: Docker Desktop is not running. It may need to be started manually."
fi

# Open MORAgents.app
if [ -d "/Applications/MORAgents.app" ]; then
    if open -a "MORAgents.app" 2>/dev/null; then
        log_message "MORAgents.app opened successfully"
    else
        log_message "Warning: Failed to open MORAgents.app. It may need to be opened manually."
    fi
else
    log_message "Error: MORAgents.app not found in /Applications"
fi

log_message "Post-install script completed."
exit 0
