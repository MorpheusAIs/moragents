import importlib
import logging

from typing import Any, Dict, List, Optional, Tuple
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

from src.config import Config

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the loading, selection and activation of agents in the system.

    Attributes:
        active_agent (Optional[str]): Currently active agent name
        selected_agents (List[str]): List of selected agent names
        config (Dict): Configuration dictionary for agents
        agents (Dict[str, Any]): Dictionary of loaded agent instances
        llm (ChatOllama): Language model instance
        embeddings (OllamaEmbeddings): Embeddings model instance
    """

    def __init__(self, config: Dict) -> None:
        """
        Initialize the AgentManager.

        Args:
            config (Dict): Configuration dictionary containing agent definitions
        """
        self.active_agent: Optional[str] = None
        self.selected_agents: List[str] = []
        self.config = config
        self.agents: Dict[str, Any] = {}
        self.llm: Optional[ChatOllama] = None
        self.embeddings: Optional[OllamaEmbeddings] = None

        # Select first 6 agents by default
        self.set_selected_agents([agent["name"] for agent in config["agents"][:6]])
        logger.info(f"AgentManager initialized with {len(self.selected_agents)} default agents")

    def _load_agent(self, agent_config: Dict) -> bool:
        """
        Load a single agent from its configuration.

        Args:
            agent_config (Dict): Configuration for the agent to load

        Returns:
            bool: True if agent loaded successfully, False otherwise
        """
        try:
            module = importlib.import_module(agent_config["path"])
            agent_class = getattr(module, agent_config["class"])
            self.agents[agent_config["name"]] = agent_class(agent_config, self.llm, self.embeddings)
            logger.info(f"Loaded agent: {agent_config['name']}")
            return True
        except Exception as e:
            logger.error(f"Failed to load agent {agent_config['name']}: {str(e)}")
            return False

    def load_all_agents(self, llm: ChatOllama, embeddings: OllamaEmbeddings) -> None:
        """
        Load all available agents with the given language and embedding models.

        Args:
            llm (ChatOllama): Language model instance
            embeddings (OllamaEmbeddings): Embeddings model instance
        """
        self.llm = llm
        self.embeddings = embeddings
        for agent_config in self.get_available_agents():
            self._load_agent(agent_config)
        logger.info(f"Loaded {len(self.agents)} agents")

    def get_active_agent(self) -> Optional[str]:
        """
        Get the name of the currently active agent.

        Returns:
            Optional[str]: Name of active agent or None if no agent is active
        """
        return self.active_agent

    def set_active_agent(self, agent_name: Optional[str]) -> None:
        """
        Set the active agent.

        Args:
            agent_name (Optional[str]): Name of agent to activate

        Raises:
            ValueError: If agent_name is not in selected_agents
        """
        self.active_agent = agent_name

    def clear_active_agent(self) -> None:
        """Clear the currently active agent."""
        self.active_agent = None

    def get_available_agents(self) -> List[Dict]:
        """
        Get list of all available agents from config.

        Returns:
            List[Dict]: List of agent configurations
        """
        return self.config["agents"]

    def get_selected_agents(self) -> List[str]:
        """
        Get list of currently selected agent names.

        Returns:
            List[str]: List of selected agent names
        """
        return self.selected_agents

    def set_selected_agents(self, agent_names: List[str]) -> None:
        """
        Set the list of selected agents.

        Args:
            agent_names (List[str]): Names of agents to select

        Raises:
            ValueError: If any agent name is invalid
        """
        valid_names = {agent["name"] for agent in self.config["agents"]}
        invalid_names = [name for name in agent_names if name not in valid_names]

        if invalid_names:
            raise ValueError(f"Invalid agent names provided: {invalid_names}")

        self.selected_agents = agent_names

        if self.active_agent not in agent_names:
            self.clear_active_agent()

    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific agent.

        Args:
            agent_name (str): Name of agent

        Returns:
            Optional[Dict]: Agent configuration if found, None otherwise
        """
        return next((agent for agent in self.config["agents"] if agent["name"] == agent_name), None)

    def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get agent instance by name.

        Args:
            agent_name (str): Name of agent

        Returns:
            Optional[Any]: Agent instance if found, None otherwise
        """
        return self.agents.get(agent_name)

    def get_agent_by_command(self, command: str) -> Optional[str]:
        """
        Get agent name by command.

        Args:
            command (str): Command to look up

        Returns:
            Optional[str]: Agent name if found, None otherwise
        """
        for agent in self.config["agents"]:
            if agent["command"] == command:
                return agent["name"]
        return None

    def parse_command(self, message: str) -> Tuple[Optional[str], str]:
        """
        Parse a message for commands.

        Args:
            message (str): Message to parse

        Returns:
            Tuple[Optional[str], str]: Tuple of (agent_name, message_without_command)
        """
        if not message.startswith("/"):
            return None, message

        parts = message[1:].split(maxsplit=1)
        command = parts[0]
        remaining_message = parts[1] if len(parts) > 1 else ""

        agent_name = self.get_agent_by_command(command)
        return agent_name, remaining_message


# Create an instance to act as a singleton store
agent_manager_instance = AgentManager(Config.AGENTS_CONFIG)
