import os
import shutil
import subprocess

from utils.logger_config import setup_logger
from config import AgentDockerConfig, AgentDockerConfigDeprecate

logger = setup_logger(__name__)

def get_docker_path():
    docker_paths = ['/Applications/Docker.app/Contents/Resources/bin/docker', shutil.which('docker')]
    for docker_path in docker_paths:
        if os.path.exists(docker_path):
            return docker_path

    logger.error("Docker executable not found in PATH.")
    return None

def check_docker_installed(docker_path):
    try:
        subprocess.run([docker_path, "--version"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Docker was found at {docker_path}")
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logger.error(f"Error checking Docker installation: {str(e)}")
        return False

def delete_docker_image(docker_path, image_name):
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

def list_containers_for_image(docker_path, image_name):
    try:
        output = subprocess.check_output(
            [docker_path, "ps", "-a", "--filter", f"ancestor={image_name}", "--format", "{{.ID}}"])
        containers = output.decode().strip().split("\n")
        return [container for container in containers if container]
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list containers for image '{image_name}': {e}")
        return []

def remove_container(docker_path, container):
    try:
        subprocess.run([docker_path, "rm", "-f", container], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove container '{container}': {e}")

def docker_image_present_on_host(docker_path, image_name):
    try:
        subprocess.run([docker_path, "inspect", image_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        return False

def remove_containers_for_image(docker_path, image_name):
    containers = list_containers_for_image(docker_path, image_name)
    for container in containers:
        remove_container(docker_path, container)
        logger.info(f"Removed container '{container}' for image '{image_name}'")

def remove_containers_by_name(docker_path, container_name):
    try:
        list_command = [docker_path, "ps", "-a", "--format", "{{.Names}}"]
        output = subprocess.check_output(list_command, universal_newlines=True)
        containers = output.strip().split("\n")

        if container_name in containers:
            remove_command = [docker_path, "rm", "-f", container_name]
            subprocess.run(remove_command, check=True)
            logger.info(f"Removed container '{container_name}'")
        else:
            logger.info(f"Container '{container_name}' not found")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error removing container '{container_name}': {str(e)}")

def migration_remove_old_images(docker_path):
    for image_name in AgentDockerConfigDeprecate.OLD_IMAGE_NAMES:
        if docker_image_present_on_host(docker_path, image_name):
            delete_docker_image(docker_path, image_name)
            logger.info(f"Deleted image '{image_name} from previous release")

def pull_docker_images(docker_path):
    for image in AgentDockerConfig.get_current_image_names():
        try:
            subprocess.run([docker_path, "pull", image], check=True)
            logger.info(f"Successfully pulled image: {image}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull image {image}: {e}")
            raise

def docker_setup():
    docker_path = get_docker_path()
    logger.info(f"Docker path: {docker_path}")

    if not check_docker_installed(docker_path):
        logger.critical("Docker is not installed.")
        raise RuntimeError("Docker is not installed.")

    # Remove old images and containers
    logger.info("Checking whether old images need removal.")
    migration_remove_old_images(docker_path)

    for image_name in AgentDockerConfig.get_current_image_names():
        remove_containers_for_image(docker_path, image_name)

    remove_containers_by_name(docker_path, "agents")
    remove_containers_by_name(docker_path, "nginx")

    # Pull the latest images
    pull_docker_images(docker_path)

    # Spin up Agent container
    subprocess.run([
        docker_path, "run", "-d", "--name", "agents",
        "-p", "8080:5000", "--restart", "always",
        "-v", "/var/lib/agents", "-v", "/app/src",
        AgentDockerConfig.get_current_image_names()[1]  # agents image
    ], check=True)

    # Spin up Nginx container
    subprocess.run([
        docker_path, "run", "-d", "--name", "nginx", "-p", "3333:80",
        AgentDockerConfig.get_current_image_names()[0]  # nginx image
    ], check=True)

if __name__ == "__main__":
    docker_setup()