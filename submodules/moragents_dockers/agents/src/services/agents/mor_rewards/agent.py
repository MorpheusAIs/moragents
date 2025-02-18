import logging

from src.models.service.agent_core import AgentCore
from src.services.agents.mor_rewards import tools
from src.models.service.chat_models import ChatRequest, AgentResponse

logger = logging.getLogger(__name__)


class MorRewardsAgent(AgentCore):
    def __init__(self, config, llm, embeddings):
        super().__init__(config, llm, embeddings)
        self.tools_provided = tools.get_tools()

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for MOR rewards."""
        try:
            if not request.wallet_address:
                return AgentResponse.needs_info(content="Please provide a wallet address to check rewards.")

            logger.info(f"Checking rewards for wallet address: {request.wallet_address}")

            rewards = {
                0: tools.get_current_user_reward(request.wallet_address, 0),
                1: tools.get_current_user_reward(request.wallet_address, 1),
            }

            response = f"Your current MOR rewards:\n"
            response += f"Capital Providers Pool (Pool 0): {rewards[0]} MOR\n"
            response += f"Code Providers Pool (Pool 1): {rewards[1]} MOR"

            logger.info(f"Rewards retrieved successfully for {request.wallet_address}")
            return AgentResponse.success(content=response, metadata={"rewards": rewards})

        except Exception as e:
            logger.error(f"Error occurred while checking rewards: {str(e)}")
            return AgentResponse.error(error_message=f"An error occurred while checking your rewards: {str(e)}")

    async def _execute_tool(self, func_name: str, args: dict) -> AgentResponse:
        """Not implemented as this agent doesn't use tools."""
        return AgentResponse.error(error_message="This agent does not support tool execution")
