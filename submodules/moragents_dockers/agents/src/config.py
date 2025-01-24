import logging
import os
import importlib.util
from typing import List, Dict, Any

from fastapi import APIRouter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)


def load_agent_routes() -> List[APIRouter]:
    """
    Dynamically load all route modules from agent subdirectories.
    Returns a list of FastAPI router objects.
    """
    routers = []
    agents_dir = os.path.join(os.path.dirname(__file__), "agents")
    logger = logging.getLogger(__name__)

    for agent_dir in os.listdir(agents_dir):
        agent_path = os.path.join(agents_dir, agent_dir)
        routes_file = os.path.join(agent_path, "routes.py")

        # Skip non-agent directories
        if not os.path.isdir(agent_path) or agent_dir.startswith("__"):
            continue

        # Skip if no routes file exists
        if not os.path.exists(routes_file):
            continue

        try:
            module_name = f"src.agents.{agent_dir}.routes"
            spec = importlib.util.spec_from_file_location(module_name, routes_file)

            if spec is None or spec.loader is None:
                logger.error(f"Failed to load module spec for {routes_file}")
                continue

            if isinstance(spec, importlib.machinery.ModuleSpec):
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "router"):
                    routers.append(module.router)
                    logger.info(f"Successfully loaded routes from {agent_dir}")
                else:
                    logger.warning(f"No router found in {agent_dir}/routes.py")
            else:
                logger.error(f"Invalid module spec type for {routes_file}")

        except Exception as e:
            logger.error(f"Error loading routes from {agent_dir}: {str(e)}")

    return routers


def load_agent_configs() -> List[Dict[str, Any]]:
    """
    Dynamically load configurations from all agent subdirectories.
    Returns a consolidated configuration dictionary.
    """
    agents_dir = os.path.join(os.path.dirname(__file__), "agents")
    configs = []

    for agent_dir in os.listdir(agents_dir):
        agent_path = os.path.join(agents_dir, agent_dir)
        config_file = os.path.join(agent_path, "config.py")

        # Skip non-agent directories and special directories
        if not os.path.isdir(agent_path) or agent_dir.startswith("__"):
            continue

        # Skip if no config file exists
        if not os.path.exists(config_file):
            logger.warning(f"No config file found for agent: {agent_dir}")
            continue

        try:
            # Import the config module
            module_name = f"src.agents.{agent_dir}.config"
            spec = importlib.util.spec_from_file_location(module_name, config_file)

            if spec is None or spec.loader is None:
                logger.error(f"Failed to load module spec for {config_file}")
                continue

            if isinstance(spec, importlib.machinery.ModuleSpec):
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check for Config class and agent_config in the module
                if hasattr(module, "Config") and hasattr(module.Config, "agent_config"):
                    config_dict = module.Config.agent_config.model_dump()
                    config_dict["name"] = agent_dir
                    configs.append(config_dict)
                    logger.info(f"Successfully loaded config from {agent_dir}")
                else:
                    logger.warning(f"No Config class or agent_config found in {agent_dir}/config.py")

        except Exception as e:
            logger.error(f"Error loading config from {agent_dir}: {str(e)}")

    return configs


# Configuration object
class AppConfig:

    # Model configuration
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
    OLLAMA_URL = "http://host.docker.internal:11434"
    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024


# Initialize LLM and embeddings
llm = ChatOllama(
    model=AppConfig.OLLAMA_MODEL,
    base_url=AppConfig.OLLAMA_URL,
)
embeddings = OllamaEmbeddings(model=AppConfig.OLLAMA_EMBEDDING_MODEL, base_url=AppConfig.OLLAMA_URL)
