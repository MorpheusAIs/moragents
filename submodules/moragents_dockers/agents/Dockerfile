FROM --platform=linux/amd64 python:3.10-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ procps && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

# Chrome installation for Debian Bullseye
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    unzip \
    xvfb \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1

# Install ChromiumDriver instead of Chrome
RUN apt-get install -y chromium chromium-driver

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

COPY . .

# Expose the port your application listens on
EXPOSE 5000

# Run the application using uvicorn with auto-reload enabled
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
