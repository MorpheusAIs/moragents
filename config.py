import os


repo_root = os.path.dirname(__file__)


class AgentDockerConfig:
    CURRENT_IMAGE_NAMES = ["moragents_dockers-nginx:latest", "moragents_dockers-agents:latest"]
    CURRENT_IMAGE_FILENAMES = ["moragents_dockers-nginx.tar", "moragents_dockers-agents.tar"]
    CURRENT_IMAGE_PATHS = [os.path.join(repo_root, "resources", img_filename)
                           for img_filename in CURRENT_IMAGE_FILENAMES]


class AgentDockerConfigDeprecate:
    OLD_IMAGE_NAMES = ["morpheus/price_fetcher_agent:latest"]
