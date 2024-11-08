import logging

from src.agents.mor_rewards import tools
from src.models.messages import ChatRequest

logger = logging.getLogger(__name__)


class MorRewardsAgent:
    def __init__(self, agent_info, llm, embeddings):
        self.agent_info = agent_info
        self.llm = llm
        self.embeddings = embeddings
        self.tools_provided = tools.get_tools()

    def get_response(self, message, wallet_address):
        logger.info(f"Checking rewards for wallet address: {wallet_address}")

        try:
            rewards = {
                0: tools.get_current_user_reward(wallet_address, 0),
                1: tools.get_current_user_reward(wallet_address, 1),
            }

            response = f"Your current MOR rewards:\n"
            response += f"Capital Providers Pool (Pool 0): {rewards[0]} MOR\n"
            response += f"Code Providers Pool (Pool 1): {rewards[1]} MOR"

            logger.info(f"Rewards retrieved successfully for {wallet_address}")
            return response, "assistant", None
        except Exception as e:
            logger.error(f"Error occurred while checking rewards: {str(e)}")
            return (
                f"An error occurred while checking your rewards: {str(e)}",
                "assistant",
                None,
            )

    def chat(self, request: ChatRequest):
        try:
            data = request.dict()
            if "prompt" in data and "wallet_address" in data:
                prompt = data["prompt"]
                wallet_address = data["wallet_address"]
                response, role, next_turn_agent = self.get_response(
                    prompt, wallet_address
                )
                return {
                    "role": role,
                    "content": response,
                    "next_turn_agent": next_turn_agent,
                }
            else:
                logger.warning("Missing required parameters in request")
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"Error": str(e)}, 500
