#!/bin/bash

# Function to check if an application is running
is_app_running() {
    app_name=$1
    pgrep -x "$app_name" >/dev/null
}

# Open Docker Desktop
open -a "Docker.app"

# Set the timeout duration (in seconds)
timeout=300  # 5 minutes

# Wait for Docker Desktop to be running
echo "Waiting for Docker Desktop to start..."
start_time=$(date +%s)
while ! is_app_running "Docker Desktop"; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    
    if [ $elapsed_time -ge $timeout ]; then
        echo "Error: Docker Desktop did not start within the specified timeout."
        exit 1
    fi
    
    sleep 1
done
echo "Docker Desktop is running."

# Open MORAgents.app
open -a "MORAgents.app"

echo "Post-install script completed."
exit 0
