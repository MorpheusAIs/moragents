import os
import shutil
import subprocess
import logging

from utils.host_utils import get_os_and_arch
from config import repo_root, AgentDockerConfig, AgentDockerConfigDeprecate


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_docker_path():
    docker_paths = ['/Applications/Docker.app/Contents/Resources/bin/docker', shutil.which('docker')]
    for docker_path in docker_paths:
        if os.path.exists(docker_path):
            return docker_path

    logging.error("Docker executable not found in PATH.")
    return None


# def get_docker_compose_path():
#     docker_paths = ['/Applications/Docker.app/Contents/Resources/bin/docker-compose', shutil.which('docker-compose')]
#     for docker_path in docker_paths:
#         if os.path.exists(docker_path):
#             return docker_path
#
#     logging.error("Docker Compose executable not found in PATH.")
#     return None
#
#
# def run_docker_compose(docker_compose_path, docker_compose_yaml_path):
#     try:
#         # Run the docker-compose command
#         subprocess.run([docker_compose_path, "-f", docker_compose_yaml_path, "up", "-d"], check=True)
#         logging.info("Docker Compose started successfully.")
#     except subprocess.CalledProcessError as e:
#         logging.error(f"Error running Docker Compose: {e}")


def check_docker_installed(docker_path):
    try:
        subprocess.run([docker_path, "--version"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info(f"Docker was found at {docker_path}")
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error checking Docker installation: {str(e)}")
        return False


def load_docker_image(docker_path, image_path):
    try:
        subprocess.run([docker_path, "load", "-i", image_path], check=True)
        logging.info(f"Docker image loaded from '{image_path}'.")
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.error(f"Error loading Docker image from '{image_path}': {str(e)}")
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
            logging.info(f"Image '{image_name}' deleted successfully.")
        else:
            pass

    except subprocess.CalledProcessError as e:
        logging.warning(f"Error deleting image: {e}")


def docker_image_present_on_host(docker_path, image_name):
    try:
        subprocess.run([docker_path, "inspect", image_name], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, TypeError) as e:
        logging.warning(f"Error checking Docker image '{image_name}': {str(e)}")
        return False


def run_agents_container(docker_path, image_name):
    try:
        # Run the agents container
        subprocess.run([
            docker_path, "run", "-d", "--rm",
            "--name", "agents",
            "-p", "8080:5000",
            "--restart", "always",
            "-v", "/var/lib/agents",
            "-v", "./agents/src:/app/src",
            image_name
        ], check=True)
        logging.info("Agents container started successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running agents container: {e}")


def run_nginx_container(docker_path, image_name):
    try:
        # Run the nginx container
        subprocess.run([
            docker_path, "run", "-d", "--rm",
            "--name", "nginx",
            "-p", "3333:80",
            image_name
        ], check=True)
        logging.info("Nginx container started successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running nginx container: {e}")


def migration_remove_old_images(docker_path):
    for image_name in AgentDockerConfigDeprecate.OLD_IMAGE_NAMES:
        if docker_image_present_on_host(docker_path, image_name):
            delete_docker_image(docker_path, image_name)
            logging.info(f"Deleted image '{image_name} from previous release")


def migration_load_current_docker_images(docker_path):
    for image_name, image_path in zip(AgentDockerConfig.CURRENT_IMAGE_NAMES, AgentDockerConfig.CURRENT_IMAGE_PATHS):
        if not docker_image_present_on_host(docker_path, image_name):

            if not os.path.exists(image_path):
                logging.critical(f"Docker image file: {image_name} was not found at path: '{image_path}'")
                raise FileNotFoundError(f"Docker image file: {image_name} was not found at path: '{image_path}'")

            load_docker_image(docker_path, image_path)
            logging.info(f"Loaded docker image '{image_name}")


def docker_setup():
    docker_path = get_docker_path()
    logging.info(f"Docker path: {docker_path}")

    # docker_compose_path = get_docker_compose_path()
    # logging.info(f"Docker compose path: {docker_compose_path}")

    if not check_docker_installed(docker_path):
        logging.critical("Docker is not installed.")
        raise RuntimeError("Docker is not installed.")

    # remove old images on user device, if present
    logging.info("Checking whether old images need removal.")
    migration_remove_old_images(docker_path)

    # ensure this release's images are present
    logging.info("Checking whether new images need to be loaded.")
    migration_load_current_docker_images(docker_path)

    # os_name, arch = get_os_and_arch()
    # compose_yaml_path = os.path.join(repo_root, "submodules/moragents_dockers/docker-compose-apple.yml") \
    #     if arch == "ARM64" else os.path.join(repo_root, "submodules/moragents_dockers/docker-compose.yml")

    # run_docker_compose(docker_compose_path, compose_yaml_path)

    # Run the containers
    nginx_image_name, agents_image_name = AgentDockerConfig.CURRENT_IMAGE_NAMES
    run_agents_container(docker_path, agents_image_name)
    run_nginx_container(docker_path, nginx_image_name)

    # FIXME
    """
    (HTTP code 500) server error - Mounts denied: 
    The path /agents/src is not shared from the host and is not known to Docker. 
    You can configure shared paths from Docker -> Preferences... -> Resources -> File Sharing. 
    See https://docs.docker.com/desktop/mac for more info.
    """


# Invoke the docker_setup() function
try:
    docker_setup()
except Exception as e:
    logging.critical(f"Error during Docker setup: {str(e)}")
    raise


if __name__ == "__main__":
    docker_setup()
