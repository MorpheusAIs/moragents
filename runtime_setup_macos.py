import os
import shutil
import subprocess

from utils.host_utils import get_os_and_arch
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


# def get_docker_compose_path():
#     docker_paths = ['/Applications/Docker.app/Contents/Resources/bin/docker-compose', shutil.which('docker-compose')]
#     for docker_path in docker_paths:
#         if os.path.exists(docker_path):
#             return docker_path
#
#     logger.error("Docker Compose executable not found in PATH.")
#     return None


def run_docker_compose(docker_compose_path, docker_compose_yaml_path):
    try:
        # Run the docker-compose command
        subprocess.run(f"{docker_compose_path} -f {docker_compose_yaml_path} up -d", check=True)
        logger.info("Docker Compose started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Docker Compose: {e}")


def check_docker_installed(docker_path):
    try:
        subprocess.run([docker_path, "--version"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Docker was found at {docker_path}")
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logger.error(f"Error checking Docker installation: {str(e)}")
        return False


def load_docker_image(docker_path, image_path):
    try:
        subprocess.run([docker_path, "load", "-i", image_path], check=True)
        logger.info(f"Docker image loaded from '{image_path}'.")
    except (subprocess.CalledProcessError, TypeError) as e:
        logger.error(f"Error loading Docker image from '{image_path}': {str(e)}")
        raise


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


# def start_container(docker_path, image_name, port_mapping):
#     try:
#         subprocess.run([docker_path, "run", "-d", "--rm", "-p", port_mapping, image_name], check=True)
#         logger.info(f"Container started with image '{image_name}' and port mapping '{port_mapping}'.")
#     except (subprocess.CalledProcessError, TypeError) as e:
#         logger.error(f"Error starting container with image '{image_name}' and port mapping '{port_mapping}': {str(e)}")
#         raise


def docker_image_present_on_host(docker_path, image_name):
    try:
        subprocess.run([docker_path, "inspect", image_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        return False


def remove_containers_for_image(docker_path, image_name):
    # List containers using the specified image
    containers = list_containers_for_image(docker_path, image_name)

    # Remove each container
    for container in containers:
        remove_container(docker_path, container)
        logger.info(f"Removed container '{container}' for image '{image_name}'")


def remove_containers_by_name(docker_path, container_name):
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


def migration_load_current_docker_images(docker_path):
    for image_name, image_path in zip(AgentDockerConfig.CURRENT_IMAGE_NAMES, AgentDockerConfig.CURRENT_IMAGE_PATHS):
        if docker_image_present_on_host(docker_path, image_name):
            # Remove containers corresponding to the image
            remove_containers_for_image(docker_path, image_name)

            # Remove the existing image
            delete_docker_image(docker_path, image_name)
            logger.info(f"Removed existing docker image '{image_name}'")

        if not os.path.exists(image_path):
            logger.critical(f"Docker image file: {image_name} was not found at path: '{image_path}'")
            raise FileNotFoundError(f"Docker image file: {image_name} was not found at path: '{image_path}'")

        load_docker_image(docker_path, image_path)
        logger.info(f"Loaded docker image '{image_name}'")


def migration_remove_old_images(docker_path):
    for image_name in AgentDockerConfigDeprecate.OLD_IMAGE_NAMES:
        if docker_image_present_on_host(docker_path, image_name):
            delete_docker_image(docker_path, image_name)
            logger.info(f"Deleted image '{image_name} from previous release")


def docker_setup():
    docker_path = get_docker_path()
    logger.info(f"Docker path: {docker_path}")

    # docker_compose_path = get_docker_compose_path()
    # logger.info(f"Docker compose path: {docker_compose_path}")

    if not check_docker_installed(docker_path):
        logger.critical("Docker is not installed.")
        raise RuntimeError("Docker is not installed.")

    # remove old images on user device, if present
    logger.info("Checking whether old images need removal.")
    migration_remove_old_images(docker_path)

    # FIXME, uncomment
    # # ensure this release's images are present
    # logger.info("Checking whether new images need to be loaded.")
    # migration_load_current_docker_images(docker_path)

    # os_name, arch = get_os_and_arch()
    # compose_yaml_path = os.path.join(repo_root, "submodules/moragents_dockers/docker-compose-apple.yml") \
    #     if arch == "ARM64" else os.path.join(repo_root, "submodules/moragents_dockers/docker-compose.yml")
    # run_docker_compose(docker_compose_path, compose_yaml_path)

    remove_containers_for_image(docker_path, "moragents_dockers-agents:latest")
    remove_containers_for_image(docker_path, "moragents_dockers-nginx:latest")

    remove_containers_by_name(docker_path, "agents")
    remove_containers_by_name(docker_path, "nginx")

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


# Invoke the docker_setup() function
try:
    docker_setup()
except Exception as e:
    logger.critical(f"Error during Docker setup: {str(e)}")
    raise


if __name__ == "__main__":
    docker_setup()
