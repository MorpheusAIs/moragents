import logging
import os
import sys
import importlib.util

from typing import List, Dict, Any, Optional

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
    agents_dir = os.path.join(os.path.dirname(__file__), "services/agents")
    logger.info(f"Loading agents from {agents_dir}")

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
            module_name = f"src.services.agents.{agent_dir}.routes"
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


def load_agent_config(agent_name: str) -> Optional[Dict[str, Any]]:
    """
    Load configuration for a specific agent by name.

    Args:
        agent_name (str): Name of the agent to load config for

    Returns:
        Optional[Dict[str, Any]]: Agent configuration if found and loaded successfully, None otherwise
    """
    agents_dir = os.path.join(os.path.dirname(__file__), "services/agents")
    agent_path = os.path.join(agents_dir, agent_name)
    config_file = os.path.join(agent_path, "config.py")

    # Verify agent directory exists and is valid
    if not os.path.isdir(agent_path) or agent_name.startswith("__"):
        logger.error(f"Invalid agent directory: {agent_name}")
        return None

    # Check config file exists
    if not os.path.exists(config_file):
        logger.warning(f"No config file found for agent: {agent_name}")
        return None

    try:
        # Import the config module
        module_name = f"src.services.agents.{agent_name}.config"
        spec = importlib.util.spec_from_file_location(module_name, config_file)

        if spec is None or spec.loader is None:
            logger.error(f"Failed to load module spec for {config_file}")
            return None

        if isinstance(spec, importlib.machinery.ModuleSpec):
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for Config class and agent_config
            if hasattr(module, "Config") and hasattr(module.Config, "agent_config"):
                config_dict = module.Config.agent_config.model_dump()
                config_dict["name"] = agent_name
                logger.info(f"Successfully loaded config for {agent_name}")
                return config_dict
            else:
                logger.warning(f"No Config class or agent_config found in {agent_name}/config.py")
                return None

    except Exception as e:
        logger.error(f"Error loading config for {agent_name}: {str(e)}")
        return None


def load_agent_configs() -> List[Dict[str, Any]]:
    """
    Dynamically load configurations from all agent subdirectories.
    Returns a consolidated configuration dictionary.
    Skips special directories like __init__.py, __pycache__, and README.md.
    """
    agents_dir = os.path.join(os.path.dirname(__file__), "services/agents")
    logger.info(f"Loading agents from {agents_dir}")
    configs = []

    for agent_dir in os.listdir(agents_dir):
        # Skip special directories and files
        if agent_dir.startswith("__") or agent_dir.startswith(".") or "." in agent_dir:
            continue

        config = load_agent_config(agent_dir)
        if config:
            configs.append(config)

    return configs


def setup_logging():
    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Setup file handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    root_logger.handlers = []

    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger


# Configuration object
class AppConfig:

    # Model configuration
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
    OLLAMA_URL = "http://host.docker.internal:11434"
    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024

    # Together AI configuration
    TOGETHER_API_KEY = "4d96d40ca55afa5a8867867e751b99aba12eb2a09bfad1c70235d084f637a053"
    TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"  # Or your preferred model
    TOGETHER_EMBEDDING_MODEL = "TogetherComputer/m2-bert-80M-8k-retrieval"


from langchain_together import ChatTogether


LLM = ChatTogether(
    model=AppConfig.TOGETHER_MODEL,
    together_api_key=AppConfig.TOGETHER_API_KEY,
    temperature=0.7,
)
# EMBEDDINGS = Together(
#     model=AppConfig.TOGETHER_EMBEDDING_MODEL,
#     together_api_key=AppConfig.TOGETHER_API_KEY,
# ).get_embeddings()

# Initialize LLM and embeddings
# LLM = ChatOllama(
#     model=AppConfig.OLLAMA_MODEL,
#     base_url=AppConfig.OLLAMA_URL,
# )
EMBEDDINGS = OllamaEmbeddings(model=AppConfig.OLLAMA_EMBEDDING_MODEL, base_url=AppConfig.OLLAMA_URL)
