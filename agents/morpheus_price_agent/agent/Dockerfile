FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ procps && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt && \
    pip install --no-cache-dir -U llama-cpp-python

# Copy the application code and necessary files
COPY src/ ./src/

# TODO, download this before copying src

# Download the model (assuming download_model.py handles the download)
RUN python3 src/download_model.py

# Expose the port your application listens on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=src/agent.py

# Run the application
CMD ["flask", "run", "--host", "0.0.0.0"]