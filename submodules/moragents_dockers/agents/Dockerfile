FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ procps && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt
    
COPY download_model.py .

COPY model_config.py .

RUN python3 download_model.py

copy . .

# Expose the port your application listens on
EXPOSE 5000


# Set the environment variable for Flask
ENV FLASK_APP=src/app.py

# Run the application
CMD ["flask", "run", "--host", "0.0.0.0"]