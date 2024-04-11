# Use an official Ubuntu 22.04 base image
FROM ubuntu:jammy

# Set the working directory in the container
WORKDIR /app


# Install Python and Pip
RUN apt-get update && \
    apt-get install -y curl python3-pip python3-dev && \
    pip3 install --upgrade pip


# Open local port for REST API access
EXPOSE 5555

# Copy the current directory contents into the container at /app
COPY . .
# Install Python deps
RUN pip3 install --no-cache-dir -r requirements.txt
# Install local codebase
RUN pip3 install -e .

RUN chmod +x ./entrypoint.sh && chmod +x app.py

ENTRYPOINT ["./entrypoint.sh"]

# docker run -d -p 5555:5555 morpheus/simple_eth_agent
