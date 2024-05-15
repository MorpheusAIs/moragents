import os
import subprocess
import time

def check_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_docker():
    try:
        subprocess.run(["C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"])
    except FileNotFoundError:
        print("Docker Desktop not found. Please install Docker Desktop.")
        return

    while True:
        try:
            output = subprocess.check_output(["docker", "info"], stderr=subprocess.DEVNULL)
            if "Server Version" in output.decode():
                print("Docker engine is running.")
                break
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        print("Waiting for Docker engine to start...")
        time.sleep(2)

def check_docker_image(image_name):
    try:
        subprocess.run(["docker", "inspect", image_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def load_docker_image(image_path):
    subprocess.run(["docker", "load", "-i", image_path], check=True)

def check_container_running(image_name):
    try:
        output = subprocess.check_output(["docker", "ps", "-f", f"ancestor={image_name}", "--format", "{{.Names}}"])
        return output.decode().strip() != ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_container(image_name, port_mapping):
    subprocess.run(["docker", "run", "-d", "-p", port_mapping, image_name], check=True)

def docker_setup():
    if not check_docker_installed():
        print("Docker is not installed. Please install Docker Desktop.")
        return

    start_docker()

    image_name = "morpheus/price_fetcher_agent"
    if not check_docker_image(image_name):
        image_path = os.path.join(os.path.dirname(__file__), "resources", "morpheus_pricefetcheragent.tar")
        load_docker_image(image_path)

    port_mapping = "53591:5000"
    if not check_container_running(image_name):
        start_container(image_name, port_mapping)

# Invoke the docker_setup() function
docker_setup()