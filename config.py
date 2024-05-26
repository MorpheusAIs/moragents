import os


repo_root = os.path.dirname(__file__)


# FIXME
"""
default	19:48:25.348098-0500	MORagents	Failed to execute script 'runtime_hook' due to unhandled exception: Docker image file: moragents_dockers-nginx:latest was not found at path: 'moragents_dockers-nginx:latest/morpheus_pricefetcheragent.tar'
default	19:48:25.348196-0500	MORagents	Traceback:
Traceback (most recent call last):
  File "runtime_hook.py", line 140, in <module>
  File "runtime_hook.py", line 129, in docker_setup
  File "runtime_hook.py", line 106, in migration_load_current_docker_images
FileNotFoundError: Docker image file: moragents_dockers-nginx:latest was not found at path: 'moragents_dockers-nginx:latest/morpheus_pricefetcheragent.tar'

default	19:54:13.465540-0500	MORagents	Failed to execute script 'runtime_hook' due to unhandled exception: Docker image file: moragents_dockers-nginx:latest was not found at path: '/Users/liqten/PycharmProjects/moragents/dist/MORagents.app/Contents/Frameworks/resources/moragents_dockers-nginx:latest'
default	19:54:13.465639-0500	MORagents	Traceback:
Traceback (most recent call last):
  File "runtime_hook.py", line 140, in <module>
  File "runtime_hook.py", line 129, in docker_setup
  File "runtime_hook.py", line 106, in migration_load_current_docker_images
FileNotFoundError: Docker image file: moragents_dockers-nginx:latest was not found at path: '/Users/liqten/PycharmProjects/moragents/dist/MORagents.app/Contents/Frameworks/resources/moragents_dockers-nginx:latest'

default	20:04:00.467638-0500	MORagents	Failed to execute script 'runtime_hook' due to unhandled exception: Docker image file: moragents_dockers-nginx:latest was not found at path: 'resources/moragents_dockers-nginx.tar'
default	20:04:00.467717-0500	MORagents	Traceback:
Traceback (most recent call last):
  File "runtime_hook.py", line 140, in <module>
  File "runtime_hook.py", line 129, in docker_setup
  File "runtime_hook.py", line 106, in migration_load_current_docker_images
FileNotFoundError: Docker image file: moragents_dockers-nginx:latest was not found at path: 'resources/moragents_dockers-nginx.tar'

"""


class AgentDockerConfig:
    CURRENT_IMAGE_NAMES = ["moragents_dockers-nginx:latest", "moragents_dockers-agents:latest"]
    CURRENT_IMAGE_FILENAMES = ["moragents_dockers-nginx.tar", "moragents_dockers-agents.tar"]
    CURRENT_IMAGE_PATHS = [os.path.join(repo_root, "resources", img_filename)
                           for img_filename in CURRENT_IMAGE_FILENAMES]


class AgentDockerConfigDeprecate:
    OLD_IMAGE_NAMES = ["morpheus/price_fetcher_agent:latest"]
