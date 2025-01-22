import logging
from typing import Dict, Any

from src.models.service.chat_models import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from src.stores import agent_manager_instance
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class DefaultAgent(AgentCore):
    """Agent for handling general conversation and providing information about Morpheus agents."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for general conversation."""
        try:
            # Get currently selected agents for system prompt
            available_agents = agent_manager_instance.get_available_agents()
            selected_agent_names = agent_manager_instance.get_selected_agents()

            # Build list of human readable names for selected agents
            selected_agents_info = []
            for agent in available_agents:
                if agent["name"] in selected_agent_names and agent["name"] != "default":
                    human_name = agent.get("human_readable_name", agent["name"])
                    selected_agents_info.append(f"- {human_name}: {agent['description']}")

            system_prompt = (
                "You are a helpful assistant that can engage in general conversation and provide information about Morpheus agents when specifically asked.\n"
                "For general questions, respond naturally without mentioning Morpheus or its agents.\n"
                "Only when explicitly asked about Morpheus or its capabilities, use this list of available agents:\n"
                f"{chr(10).join(selected_agents_info)}\n"
                "Remember: Only mention Morpheus agents if directly asked about them. Otherwise, simply answer questions normally as a helpful assistant."
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.llm.invoke(messages)
            return AgentResponse.success(content=result.content.strip())

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Default agent doesn't use any tools."""
        return AgentResponse.error(error_message=f"Unknown tool: {func_name}")
