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

def delete_docker_image(image_name):
    try:
        list_command = [docker_path, "images", "--format", "{{.Repository}}:{{.Tag}}"]
        output = subprocess.check_output(list_command, universal_newlines=True)
        images = output.strip().split("\n")

        if image_name in images:
            remove_command = [docker_path, "rmi", "-f", image_name]
            subprocess.run(remove_command, check=True)
            logger.info(f"Image '{image_name}' deleted successfully.")
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
    except (subprocess.CalledProcessError, TypeError):
        return False

def remove_containers_for_image(image_name):
    containers = list_containers_for_image(image_name)
    for container in containers:
        remove_container(container)
        logger.info(f"Removed container '{container}' for image '{image_name}'")

def remove_containers_by_name(container_name):
    try:
        list_command = [docker_path, "ps", "-a", "--format", "{{.Names}}"]
        output = subprocess.check_output(list_command, universal_newlines=True)
        containers = output.strip().split("\n")

        if container_name in containers:
            remove_command = [docker_path, "rm", "-f", container_name]
            subprocess.run(remove_command, check=True)
            logger.info(f"Removed container '{container_name}'")
        else:
            logger.info(f"Not removing container '{container_name}' as it was not found")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error removing container '{container_name}': {str(e)}")

def migration_remove_old_images():
    for image_name in AgentDockerConfigDeprecate.OLD_IMAGE_NAMES:
        if docker_image_present_on_host(image_name):
            delete_docker_image(image_name)
            logger.info(f"Deleted image '{image_name}' from previous release")

def pull_docker_images():
    for image_name in AgentDockerConfig.get_current_image_names():
        try:
            subprocess.run([docker_path, "pull", image_name], check=True)
            logger.info(f"Successfully pulled image: {image_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull image {image_name}: {e}")
            raise

def docker_setup():
    if not check_docker_installed():
        print("Docker is not installed. Please install Docker Desktop.")
        return

    start_docker()

    logger.info("Checking whether old images need removal.")
    migration_remove_old_images()

    pull_docker_images()

    for image_name in AgentDockerConfig.get_current_image_names():
        remove_containers_for_image(image_name)

    remove_containers_by_name("agents")
    remove_containers_by_name("nginx")

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