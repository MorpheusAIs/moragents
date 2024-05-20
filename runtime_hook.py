import os
import shutil
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_docker_path():
    docker_paths = ['/Applications/Docker.app/Contents/Resources/bin/docker', shutil.which('docker')]
    for docker_path in docker_paths:
        if os.path.exists(docker_path):
            return docker_path

    logging.error("Docker executable not found in PATH.")
    return None


def check_docker_installed(docker_path):
    try:
        subprocess.run([docker_path, "--version"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info(f"Docker was found at {docker_path}")
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error checking Docker installation: {str(e)}")
        return False


def start_docker():
    try:
        logging.info("Starting Docker...")
        subprocess.run(["open", "-a", "Docker"], check=True)
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error starting Docker: {str(e)}")
        raise

    docker_path = get_docker_path()
    while True:
        try:
            output = subprocess.check_output([docker_path, "info"], stderr=subprocess.DEVNULL)
            if "Server Version" in output.decode():
                logging.info("Docker engine is running.")
                break
        except (subprocess.CalledProcessError, TypeError) as e:
            logging.warning(f"Error checking Docker engine status: {str(e)}")

        logging.info("Waiting for Docker engine to start...")
        time.sleep(2)
        start_docker()


def check_docker_image(docker_path, image_name):
    try:
        subprocess.run([docker_path, "inspect", image_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.warning(f"Error checking Docker image '{image_name}': {str(e)}")
        return False


def load_docker_image(docker_path, image_path):
    try:
        subprocess.run([docker_path, "load", "-i", image_path], check=True)
        logging.info(f"Docker image loaded from '{image_path}'.")
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error loading Docker image from '{image_path}': {str(e)}")
        raise


def check_container_running(docker_path, image_name):
    try:
        output = subprocess.check_output([docker_path, "ps", "-f", f"ancestor={image_name}", "--format", "{{.Names}}"])
        return output.decode().strip() != ""
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.warning(f"Error checking container status for image '{image_name}': {str(e)}")
        return False


def start_container(docker_path, image_name, port_mapping):
    try:
        subprocess.run([docker_path, "run", "-d", "--rm", "-p", port_mapping, image_name], check=True)
        logging.info(f"Container started with image '{image_name}' and port mapping '{port_mapping}'.")
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error starting container with image '{image_name}' and port mapping '{port_mapping}': {str(e)}")
        raise


def docker_setup():
    docker_path = get_docker_path()
    logging.info(f"Docker path: {docker_path}")

    if not check_docker_installed(docker_path):
        logging.critical("Docker is not installed.")
        raise RuntimeError("Docker is not installed.")

    start_docker()

    image_name = "morpheus/price_fetcher_agent"
    if not check_docker_image(docker_path, image_name):
        image_path = os.path.join(os.path.dirname(__file__), "resources", "morpheus_pricefetcheragent.tar")
        if not os.path.exists(image_path):
            logging.critical(f"Docker image file '{image_path}' not found.")
            raise FileNotFoundError(f"Docker image file '{image_path}' not found.")
        load_docker_image(docker_path, image_path)

    port_mapping = "53591:5000"
    if not check_container_running(docker_path, image_name):
        start_container(docker_path, image_name, port_mapping)


# Invoke the docker_setup() function
try:
    docker_setup()
except Exception as e:
    logging.critical(f"Error during Docker setup: {str(e)}")
    raise
