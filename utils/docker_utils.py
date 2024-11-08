import os
import random
import socket
import subprocess


def find_unused_port() -> int:
    while True:
        port = random.randint(49152, 65535)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex(("localhost", port))
            if res != 0:
                return port


def build_image_if_not_present(image_name, dockerfile_path) -> None:

    context_dir = os.path.dirname(dockerfile_path)

    try:
        subprocess.run(
            f"docker inspect {image_name}",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Docker image '{image_name}' already exists.")
    except subprocess.CalledProcessError:
        print(f"Docker image '{image_name}' not found. Building the image...")
        subprocess.run(
            f"docker build -t {image_name} -f {dockerfile_path} {context_dir}",
            shell=True,
            check=True,
        )
        print(f"Docker image '{image_name}' built successfully.")


def remove_container(image_name):
    # Get the list of running containers
    output = subprocess.check_output(["docker", "ps", "--format", "{{.ID}}\t{{.Image}}"])
    containers = output.decode().strip().split("\n")

    if not any(containers):
        return False

    for container in containers:
        container_id, container_image = container.split("\t")
        if image_name in container_image:
            print(f"Stopping and removing container: {container_id}")
            stop_command = ["docker", "stop", container_id]
            subprocess.run(stop_command, check=True)
            remove_command = ["docker", "rm", container_id]
            subprocess.run(remove_command, check=True)
            return True
    return False


def launch_container(image_name, internal_port, dockerfile_path) -> int:

    remove_container(image_name)

    build_image_if_not_present(image_name, dockerfile_path)

    host_port = find_unused_port()

    docker_command = f"docker run -d -p {host_port}:{internal_port} {image_name}"
    subprocess.run(docker_command, shell=True, check=True)
    print(
        f"Docker container of image {image_name} launched with port mapping: {host_port}:{internal_port}"
    )

    return host_port
