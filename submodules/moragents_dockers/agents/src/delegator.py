import importlib
import logging
from typing import Dict, Optional, Tuple, Any, List

from langchain.schema import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class Delegator:
    def __init__(self, agent_manager, llm, embeddings):
        self.agent_manager = agent_manager
        self.llm = llm
        self.embeddings = embeddings
        self.agents = {}  # Empty dict initially

        # Load initial agents
        self._load_selected_agents()
        logger.info(f"Delegator initialized with {len(self.agents)} agents")

    def _load_selected_agents(self) -> None:
        """Load all currently selected agents"""
        selected_agents = self.agent_manager.get_selected_agents()

        # Remove agents that are no longer selected
        self.agents = {
            name: agent
            for name, agent in self.agents.items()
            if name in selected_agents
        }

        # Load new agents
        for agent_name in selected_agents:
            if agent_name not in self.agents:
                agent_config = self.agent_manager.get_agent_config(agent_name)
                if agent_config:
                    self._load_agent(agent_config)

    def _load_agent(self, agent_config: Dict) -> bool:
        """Load a single agent"""
        try:
            module = importlib.import_module(agent_config["path"])
            agent_class = getattr(module, agent_config["class"])
            agent_instance = agent_class(
                agent_config,
                self.llm,
                self.embeddings,
            )
            self.agents[agent_config["name"]] = agent_instance
            logger.info("Loaded agent: %s", agent_config["name"])
            return True
        except Exception as e:
            logger.error("Failed to load agent %s: %s", agent_config["name"], str(e))
            return False

    def update_selected_agents(self, agent_names: List[str]) -> None:
        """Update loaded agents based on new selection"""
        self.agent_manager.set_selected_agents(agent_names)
        self._load_selected_agents()

    def get_delegator_response(
        self, prompt: Dict, upload_state: bool
    ) -> Dict[str, str]:
        """Get appropriate agent based on prompt"""
        available_agents = [
            agent_config
            for agent_config in self.agent_manager.get_available_agents()
            if agent_config["name"] in self.agent_manager.get_selected_agents()
            and not (agent_config["upload_required"] and not upload_state)
        ]

        if not available_agents:
            raise ValueError("No agents available for current state")

        system_prompt = (
            "Your name is Morpheus. "
            "Your primary function is to select the correct agent based on the user's input. "
            "You MUST use the 'select_agent' function to select an agent. "
            "Available agents and their descriptions:\n"
            + "\n".join(
                f"- {agent['name']}: {agent['description']}"
                for agent in available_agents
            )
        )

        tools = [
            {
                "name": "select_agent",
                "description": "Choose which agent should be used to respond to the user query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "string",
                            "enum": [agent["name"] for agent in available_agents],
                            "description": "The name of the agent to be used",
                        }
                    },
                    "required": ["agent"],
                },
            }
        ]

        agent_selection_llm = self.llm.bind_tools(tools)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt["content"]),
        ]

        result = agent_selection_llm.invoke(messages)
        tool_calls = result.tool_calls

        if not tool_calls:
            raise ValueError("No agent was selected by the model")

        selected_agent = tool_calls[0]
        selected_agent_name = selected_agent.get("args", {}).get("agent")

        return {"agent": selected_agent_name}

    def delegate_chat(self, agent_name: str, request: Any) -> Tuple[Optional[str], Any]:
        """Delegate chat to specific agent"""
        logger.info(f"Attempting to delegate chat to agent: {agent_name}")

        if agent_name not in self.agent_manager.get_selected_agents():
            logger.warning(f"Attempted to delegate to unselected agent: {agent_name}")
            return None, {"error": f"Agent {agent_name} is not selected"}, 400

        agent = self.agents.get(agent_name)
        if not agent:
            logger.error(f"Agent {agent_name} is selected but not loaded")
            return None, {"error": "Agent failed to load"}, 500

        try:
            result = agent.chat(request)
            logger.info(f"Chat delegation to {agent_name} completed successfully")
            return agent_name, result
        except Exception as e:
            logger.error(f"Error during chat delegation to {agent_name}: {str(e)}")
            return None, {"error": f"Chat delegation failed: {str(e)}"}, 500

    def delegate_route(
        self, agent_name: str, request: Any, method_name: str
    ) -> Tuple[Any, int]:
        agent = self.agents.get(agent_name)
        if agent:
            if hasattr(agent, method_name):
                logger.info("Delegating %s to agent: %s", method_name, agent_name)
                method = getattr(agent, method_name)
                return method(request)
            else:
                logger.warning(
                    "Method %s not found in agent %s", method_name, agent_name
                )
                return {
                    "error": f"No such method '{method_name}' in agent '{agent_name}'"
                }, 400
        logger.warning("Attempted to delegate to non-existent agent: %s", agent_name)
        return {"error": "No such agent registered"}, 400
