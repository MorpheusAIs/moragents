#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Welcome to the MORagents installer for Linux${NC}"

# Install the .deb package
echo -e "${YELLOW}Installing MORagents...${NC}"
dpkg -i moragents.deb
apt-get install -f -y

# Run the setup script
echo -e "${YELLOW}Running MORagents setup...${NC}"
./moragents-setup.sh

echo -e "${GREEN}Installation complete!${NC}"
echo "You can now start MORagents from your application menu or by running 'MORagents' in the terminal."
echo -e "${YELLOW}NOTE: Please log out and log back in for Docker group changes to take effect.${NC}"