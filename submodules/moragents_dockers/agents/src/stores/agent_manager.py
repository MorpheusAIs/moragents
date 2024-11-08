import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AgentManager:
    def __init__(self, config: Dict):
        self.active_agent: Optional[str] = None
        self.selected_agents: List[str] = []
        self.config = config

        # Initialize with first 6 agents selected
        default_agents = [agent["name"] for agent in config["agents"][:6]]
        self.set_selected_agents(default_agents)
        logger.info(
            f"AgentManager initialized with {len(default_agents)} default selected agents"
        )

    def get_active_agent(self) -> Optional[str]:
        return self.active_agent

    def set_active_agent(self, agent_name: Optional[str]) -> None:
        if agent_name is not None and agent_name not in self.selected_agents:
            raise ValueError(f"Agent {agent_name} is not selected")
        self.active_agent = agent_name

    def clear_active_agent(self) -> None:
        self.active_agent = None

    def get_available_agents(self) -> List[Dict]:
        """Get all available agents from config"""
        return self.config["agents"]

    def get_selected_agents(self) -> List[str]:
        """Get list of currently selected agent names"""
        return self.selected_agents

    def set_selected_agents(self, agent_names: List[str]) -> None:
        """Set selected agents and validate against config"""
        valid_names = {agent["name"] for agent in self.config["agents"]}
        invalid_names = [name for name in agent_names if name not in valid_names]

        if invalid_names:
            raise ValueError(f"Invalid agent names provided: {invalid_names}")

        self.selected_agents = agent_names

        # Clear active agent if it's no longer selected
        if self.active_agent not in agent_names:
            self.active_agent = None

    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """Get configuration for a specific agent"""
        for agent in self.config["agents"]:
            if agent["name"] == agent_name:
                return agent
        return None
