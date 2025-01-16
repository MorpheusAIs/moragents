import logging
from typing import Dict, Any

from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from src.stores import wallet_manager_instance
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class DCAAgent(AgentCore):
    """Agent for handling DCA (Dollar Cost Averaging) strategies."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        """Initialize the DCAAgent."""
        super().__init__(config, llm, embeddings)

        # TODO: Create specialized tools to pull out DCA params from user message
        # For now, we can ignore these tools

        # self.tools_provided = []  # TODO: Add DCA-specific tools
        # self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for DCA-related queries."""
        # Check CDP client initialization
        if not wallet_manager_instance.configure_cdp_client():
            # Return user-friendly error for missing credentials
            return AgentResponse.needs_info(
                content="I'm not able to help with DCA strategies right now because the CDP client is not initialized. Please set up your API credentials first."
            )

        # Check for active wallet
        active_wallet = wallet_manager_instance.get_active_wallet()
        if not active_wallet:
            # Return user-friendly error for missing wallet
            return AgentResponse.needs_info(
                content="You'll need to select or create a wallet before I can help with DCA strategies. Please set up a wallet first."
            )

        return AgentResponse.action_required(content="Ready to set up DCA", action_type="dca")
        # TODO: Create specialized tools to pull out DCA params from user message
        # For now, we can ignore these tools
        # try:
        #     messages = [
        #         SystemMessage(
        #             content=(
        #                 "You are a DCA strategy manager. "
        #                 "Help users set up and manage their DCA strategies. "
        #                 "Ask for clarification if a request is ambiguous."
        #             )
        #         ),
        #         HumanMessage(content=request.prompt.content),
        #     ]

        #     result = self.tool_bound_llm.invoke(messages)
        #     return await self._handle_llm_response(result)

        # except Exception as e:
        #     logger.error(f"Error processing request: {str(e)}", exc_info=True)
        #     return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate DCA tool based on function name."""
        try:
            # TODO: Implement DCA-specific tools
            return AgentResponse.needs_info(
                content=f"I don't know how to {func_name} yet. Please try a different action."
            )

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))
