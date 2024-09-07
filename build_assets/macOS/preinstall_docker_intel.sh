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

# Set variables
DOCKER_DMG_URL="https://desktop.docker.com/mac/main/amd64/Docker.dmg"
DOCKER_DMG="Docker.dmg"
VOLUME_NAME="Docker"
INSTALL_PATH="/Volumes/$VOLUME_NAME/Docker.app/Contents/MacOS/install"

# Download Docker
log_message "Downloading Docker for Intel Mac..."
if curl -L "$DOCKER_DMG_URL" -o "$DOCKER_DMG"; then
    log_message "Docker download completed."
else
    log_message "Error: Failed to download Docker."
    exit 1
fi

# Mount the DMG
log_message "Mounting Docker DMG..."
if hdiutil attach "$DOCKER_DMG"; then
    log_message "Docker DMG mounted successfully."
else
    log_message "Error: Failed to mount Docker DMG."
    exit 1
fi

# Run the installer
log_message "Running Docker installer..."
if "$INSTALL_PATH" --accept-license; then
    log_message "Docker installation completed."
else
    log_message "Error: Docker installation failed."
    hdiutil detach "/Volumes/$VOLUME_NAME"
    exit 1
fi

# Detach the DMG
log_message "Detaching Docker DMG..."
if hdiutil detach "/Volumes/$VOLUME_NAME"; then
    log_message "Docker DMG detached successfully."
else
    log_message "Warning: Failed to detach Docker DMG. This is not critical."
fi

# Clean up
log_message "Cleaning up..."
rm -f "$DOCKER_DMG"

log_message "Docker preinstall script completed successfully."
exit 0