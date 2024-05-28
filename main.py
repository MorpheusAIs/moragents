import time
import logging
import webbrowser

from runtime_setup_macos import docker_setup
from utils.logger_config import setup_logger


# Configure logging
logger = setup_logger(__name__)


if __name__ == '__main__':

    try:
        docker_setup()
    except Exception as e:
        logging.critical(f"Error during Docker setup: {str(e)}")
        raise

    time.sleep(7)

    url = 'http://localhost:3333/'
    webbrowser.open(url)
