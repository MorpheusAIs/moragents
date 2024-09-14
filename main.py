import time
import logging
import webbrowser

from runtime_setup_macos import main as macos_setup
from runtime_setup_windows import main as windows_setup
from runtime_setup_linux import main as linux_setup
from utils.logger_config import setup_logger
from utils.host_utils import get_os_and_arch

# Configure logging
logger = setup_logger(__name__)


if __name__ == "__main__":

    try:
        os_name, arch = get_os_and_arch()

        if os_name == "macOS":
            macos_setup()
        elif os_name == "Windows":
            windows_setup()
        elif os_name == "Linux":
            linux_setup()

    except Exception as e:
        logging.critical(f"Error during Docker setup: {str(e)}")
        raise

    time.sleep(7)

    url = "http://localhost:3333/"
    webbrowser.open(url)
