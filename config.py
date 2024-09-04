import os
import sys

from utils.host_utils import get_os_and_arch


os_name, arch = get_os_and_arch()

if os_name == "macOS":
    repo_root = os.path.dirname(__file__)
elif os_name == "Windows":
    # Run as bundled executable if condition is met, else run as regular Python script
    repo_root = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
elif os_name == "Linux":
    raise RuntimeError(
        f"MORagents needs Linux support! Would you like to help?\n"
        f"https://github.com/MorpheusAIs/moragents/issues/27")


class AgentDockerConfig:
    CURRENT_IMAGE_NAMES = ["moragents_dockers-nginx:latest", "moragents_dockers-agents:latest"]
    CURRENT_IMAGE_FILENAMES = ["moragents_dockers-nginx.tar", "moragents_dockers-agents.tar"]
    CURRENT_IMAGE_PATHS = [os.path.join(repo_root, "resources", img_filename)
                           for img_filename in CURRENT_IMAGE_FILENAMES]


class AgentDockerConfigDeprecate:
    OLD_IMAGE_NAMES = ["morpheus/price_fetcher_agent:latest"]
