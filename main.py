import time
import logging
import webbrowser

from runtime_setup_macos import docker_setup as docker_setup_macos
from runtime_setup_windows import docker_setup as docker_setup_windows
from utils.logger_config import setup_logger
from utils.host_utils import get_os_and_arch

# Configure logging
logger = setup_logger(__name__)


if __name__ == '__main__':

    try:
        os_name, arch = get_os_and_arch()

        if os_name == "macOS":
            docker_setup_macos()
        elif os_name == "Windows":
            docker_setup_windows()
        elif os_name == "Linux":
            raise RuntimeError(
                f"MORagents needs Linux support! Would you like to help?\n"
                f"https://github.com/MorpheusAIs/moragents/issues/27")

    except Exception as e:
        logging.critical(f"Error during Docker setup: {str(e)}")
        raise

    time.sleep(7)

    url = 'http://localhost:3333/'
    webbrowser.open(url)
