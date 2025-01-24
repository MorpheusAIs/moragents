import logging
import json

from typing import Dict, List, Optional, Tuple
from langchain.schema import HumanMessage, SystemMessage
from src.stores import chat_manager_instance, agent_manager_instance
from src.models.service.chat_models import ChatRequest, AgentResponse, ResponseType

logger = logging.getLogger(__name__)


class Delegator:
    def __init__(self, llm, embeddings):
        self.llm = llm
        self.attempted_agents = set()  # Track attempted agents within a chat session
        self.selected_agents_for_request = []  # Track the top 3 selected agents for current request

        # Load all agents via agent manager
        agent_manager_instance.load_all_agents(llm, embeddings)
        logger.info(f"Delegator initialized with {len(agent_manager_instance.agents)} agents")

    def reset_attempted_agents(self):
        """Reset the set of attempted agents and selected agents for request"""
        self.attempted_agents = set()
        self.selected_agents_for_request = []
        logger.info("Reset attempted agents and selected agents for request")

    def get_available_unattempted_agents(self) -> List[Dict]:
        """Get all available agents that haven't been attempted yet"""
        return [
            agent_config
            for agent_config in agent_manager_instance.get_available_agents()
            if agent_config["name"] not in self.attempted_agents
            and not (agent_config["upload_required"] and not chat_manager_instance.get_uploaded_file_status())
        ]

    def get_delegator_response(self, prompt: Dict) -> List[str]:
        """
        Get top 3 most appropriate agents based on prompt, excluding previously attempted agents
        Returns a list of agent names in priority order
        """
        available_agents = self.get_available_unattempted_agents()
        logger.info(f"Available, unattempted agents: {available_agents}")

        if not available_agents:
            # If no specialized agents are available, use default agent as last resort
            if "default" not in self.attempted_agents:
                return ["default"]
            raise ValueError("No remaining agents available for current state")

        system_prompt = (
            "Your name is Morpheus. "
            "Your primary function is to analyze the user's input and select the top 3 most appropriate agents "
            "from the list of available agents, ranked in order of relevance. "
            "You MUST use the 'rank_agents' function to select the agents. "
            "Available agents and their descriptions in the format `{agent_name}: {agent_description}`\n"
            + "\n".join(f"- {agent['name']}: {agent['description']}" for agent in available_agents)
        )

        tools = [
            {
                "name": "rank_agents",
                "description": "Select and rank the top 3 most appropriate agents for the user query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agents": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [agent["name"] for agent in available_agents],
                            },
                            "maxItems": 3,
                            "description": "List of up to 3 agent names, ordered by relevance",
                        }
                    },
                    "required": ["agents"],
                },
            }
        ]

        agent_selection_llm = self.llm.bind_tools(tools, tool_choice="rank_agents")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt["content"]),
        ]

        result = agent_selection_llm.invoke(messages)
        tool_calls = result.tool_calls

        if not tool_calls:
            raise ValueError("No agents were selected by the model")

        # Parse the JSON string into a Python object
        selected_agents = tool_calls[0].get("args", {}).get("agents", [])
        if isinstance(selected_agents, str):
            try:
                selected_agents = json.loads(selected_agents)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse selected agents JSON: {selected_agents}")
                selected_agents = []

        # Store selected agents for this request
        self.selected_agents_for_request = selected_agents
        logger.info(f"Selected agents in priority order: {selected_agents}")

        return selected_agents

    async def delegate_chat(self, chat_request: ChatRequest) -> Tuple[Optional[str], AgentResponse]:
        """
        Delegate chat to agents in priority order with cascading fallback
        Returns tuple of (successful_agent_name, agent_response)
        """
        try:
            # Get ranked list of agents for this request
            ranked_agents = self.get_delegator_response(chat_request.prompt.dict())

            for agent_name in ranked_agents:
                # Add agent to attempted set before trying to use it
                self.attempted_agents.add(agent_name)
                logger.info(f"Attempting to delegate chat to agent: {agent_name}")

                agent = agent_manager_instance.get_agent(agent_name)
                if not agent:
                    logger.error(f"Agent {agent_name} is not loaded")
                    continue

                try:
                    result = await agent.chat(chat_request)
                    # If the agent returns an error response, continue to next agent
                    if result.response_type == ResponseType.ERROR:
                        logger.warning(f"Agent {agent_name} returned error response, trying next agent")
                        continue

                    logger.info(f"Chat delegation to {agent_name} completed successfully")
                    return agent_name, result
                except Exception as e:
                    logger.error(f"Error during chat delegation to {agent_name}: {str(e)}")
                    continue

            # If we've exhausted all selected agents without success
            return None, AgentResponse.error(error_message="All selected agents have been attempted without success")

        except ValueError as ve:
            # No more agents available
            logger.error(f"No available agents: {str(ve)}")
            return None, AgentResponse.error(error_message="No suitable agents available for the request")
