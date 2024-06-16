import os
import sys
import subprocess
import time

from utils.logger_config import setup_logger
from config import AgentDockerConfig, AgentDockerConfigDeprecate

logger = setup_logger(__name__)


docker_path = "docker"


def check_docker_installed():
    try:
        subprocess.run([docker_path, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def start_docker():
    try:
        subprocess.run(["C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"])
    except FileNotFoundError:
        logger.error("Docker Desktop not found. Please install Docker Desktop.")
        raise

    while True:
        try:
            output = subprocess.check_output(["docker", "info"], stderr=subprocess.PIPE)
            if "Server Version" in output.decode():
                print("Docker engine is running.")
                break
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        logger.info("Waiting for Docker engine to start...")
        time.sleep(2)


def load_docker_image(image_path):
    print(f"Loading Docker image {image_path}. This will take about 5-10 minutes, please wait...")
    try:
        result = subprocess.run(["docker", "load", "-i", image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, timeout=300)
        print(f"Docker image loaded successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error loading Docker image: {e}")
        print(f"Command: {e.cmd}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")


def delete_docker_image(image_name):
    try:
        # List all images
        list_command = [docker_path, "images", "--format", "{{.Repository}}:{{.Tag}}"]
        output = subprocess.check_output(list_command, universal_newlines=True)
        images = output.strip().split("\n")

        # Find the image with the specified name
        if image_name in images:
            # Remove the image
            remove_command = [docker_path, "rmi", "-f", image_name]
            subprocess.run(remove_command, check=True)
            logger.info(f"Image '{image_name}' deleted successfully.")
        else:
            pass

    except subprocess.CalledProcessError as e:
        logger.warning(f"Error deleting image: {e}")


def list_containers_for_image(image_name):
    try:
        output = subprocess.check_output(
            [docker_path, "ps", "-a", "--filter", f"ancestor={image_name}", "--format", "{{.ID}}"])
        containers = output.decode().strip().split("\n")
        return [container for container in containers if container]
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list containers for image '{image_name}': {e}")
        return []


def remove_container(container):
    try:
        subprocess.run([docker_path, "rm", "-f", container], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove container '{container}': {e}")


def docker_image_present_on_host(image_name):
    try:
        subprocess.run([docker_path, "inspect", image_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        return False


def remove_containers_for_image(image_name):
    # List containers using the specified image
    containers = list_containers_for_image(image_name)

    # Remove each container
    for container in containers:
        remove_container(container)
        logger.info(f"Removed container '{container}' for image '{image_name}'")


def remove_containers_by_name(container_name):
    try:
        # List containers with the specified name
        list_command = [docker_path, "ps", "-a", "--format", "{{.Names}}"]
        output = subprocess.check_output(list_command, universal_newlines=True)
        containers = output.strip().split("\n")

        # Check if the specified container name exists
        if container_name in containers:
            # Remove the container
            remove_command = [docker_path, "rm", "-f", container_name]
            subprocess.run(remove_command, check=True)
            logger.info(f"Removed container '{container_name}'")
        else:
            logger.info(f"Container '{container_name}' not found")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error removing container '{container_name}': {str(e)}")


def migration_load_current_docker_images():
    for image_name, image_path in zip(AgentDockerConfig.CURRENT_IMAGE_NAMES, AgentDockerConfig.CURRENT_IMAGE_PATHS):

        # FIXME, this is temporary
        if getattr(sys, 'frozen', False):
            image_path = os.path.join(sys._MEIPASS, "resources", os.path.basename(image_path))
        else:
            image_path = os.path.join(os.path.dirname(__file__), "resources", os.path.basename(image_path))

        if docker_image_present_on_host(image_name):
            logger.info(f"Docker image '{image_name}' is already present, skipping loading")
            continue

        if not os.path.exists(image_path):
            logger.critical(f"Docker image file: {image_name} was not found at path: '{image_path}'")
            raise FileNotFoundError(f"Docker image file: {image_name} was not found at path: '{image_path}'")

        load_docker_image(image_path)
        logger.info(f"Loaded docker image '{image_name}'")


def check_container_running(image_name):
    try:
        output = subprocess.check_output(["docker", "ps", "-f", f"ancestor={image_name}", "--format", "{{.Names}}"])
        if not output:
            return False
        return output.decode().strip() != ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def start_container(image_name, port_mapping):
    subprocess.run(["docker", "run", "-d", "-p", port_mapping, image_name], check=True)


def migration_remove_old_images():
    for image_name in AgentDockerConfigDeprecate.OLD_IMAGE_NAMES:
        if docker_image_present_on_host(image_name):
            delete_docker_image(image_name)
            logger.info(f"Deleted image '{image_name} from previous release")


def docker_setup():
    if not check_docker_installed():
        print("Docker is not installed. Please install Docker Desktop.")
        return

    start_docker()

    # remove old images on user device, if present
    logger.info("Checking whether old images need removal.")
    migration_remove_old_images()

    migration_load_current_docker_images()

    remove_containers_for_image("moragents_dockers-agents:latest")
    remove_containers_for_image("moragents_dockers-nginx:latest")

    remove_containers_by_name("agents")
    remove_containers_by_name("nginx")

    # Spin up Agent container
    subprocess.run([
        docker_path, "run", "-d", "--name", "agents",
        "-p", "8080:5000", "--restart", "always",
        "-v", "/var/lib/agents", "-v", "/app/src",
        "moragents_dockers-agents:latest"
    ], check=True)

    # Spin up Nginx container
    subprocess.run([
        docker_path, "run", "-d", "--name", "nginx", "-p", "3333:80",
        "moragents_dockers-nginx:latest"
    ], check=True)


if __name__ == "__main__":
    docker_setup()
