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
    repo_root = os.path.dirname(__file__)
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")

class AgentDockerConfig:
    MACOS_APPLE_IMAGE_NAMES = [
        "lachsbagel/moragents_dockers-nginx:apple-0.1.0",
        "lachsbagel/moragents_dockers-agents:apple-0.1.0"
    ]
    MACOS_INTEL_IMAGE_NAMES = [
        "lachsbagel/moragents_dockers-nginx:amd64-0.1.0",
        "lachsbagel/moragents_dockers-agents:amd64-0.1.0"
    ]
    WINDOWS_IMAGE_NAMES = [
        "lachsbagel/moragents_dockers-nginx:amd64-0.1.0",
        "lachsbagel/moragents_dockers-agents:amd64-0.1.0"
    ]
    LINUX_IMAGE_NAMES = [  # TODO, may need linux specific tagged images
        "lachsbagel/moragents_dockers-nginx:amd64-0.1.0",
        "lachsbagel/moragents_dockers-agents:amd64-0.1.0"
    ]

    @staticmethod
    def get_current_image_names():
        if os_name == "macOS" and arch == "ARM64":
            return AgentDockerConfig.MACOS_APPLE_IMAGE_NAMES
        elif os_name == "macOS" and arch == "x86_64":
            return AgentDockerConfig.MACOS_INTEL_IMAGE_NAMES
        elif os_name == "Windows":
            return AgentDockerConfig.WINDOWS_IMAGE_NAMES
        elif os_name == "Linux":
            return AgentDockerConfig.LINUX_IMAGE_NAMES
        else:
            raise RuntimeError(f"Unsupported OS: {os_name}")

class AgentDockerConfigDeprecate:
    OLD_IMAGE_NAMES = [
        "morpheus/price_fetcher_agent:latest",
        "moragents_dockers-nginx:latest",
        "moragents_dockers-agents:latest",
        "lachsbagel/moragents_dockers-nginx:apple-0.0.9",
        "lachsbagel/moragents_dockers-agents:apple-0.0.9",
        "lachsbagel/moragents_dockers-nginx:amd64-0.0.9",
        "lachsbagel/moragents_dockers-agents:amd64-0.0.9"
    ]
