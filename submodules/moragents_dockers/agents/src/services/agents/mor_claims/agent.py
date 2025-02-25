import logging
from typing import Dict, Any

from src.services.agents.mor_claims import tools
from src.models.service.chat_models import ChatRequest, AgentResponse
from src.models.service.agent_core import AgentCore
from langchain.schema import HumanMessage, SystemMessage
from src.stores import agent_manager_instance

logger = logging.getLogger(__name__)


class MorClaimsAgent(AgentCore):
    """Agent for handling MOR token claims and rewards."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = tools.get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for MOR claims."""
        try:
            wallet_address = request.wallet_address
            chat_history = request.chat_history

            # Check if this is initial interaction by looking at chat history
            if not chat_history:
                agent_manager_instance.set_active_agent("mor claims")

                rewards = {
                    0: tools.get_current_user_reward(wallet_address, 0),
                    1: tools.get_current_user_reward(wallet_address, 1),
                }
                available_rewards = {pool: amount for pool, amount in rewards.items() if amount > 0}

                if available_rewards:
                    selected_pool = max(available_rewards.keys())
                    return AgentResponse.success(
                        content=f"You have {available_rewards[selected_pool]} MOR rewards available in pool {selected_pool}. Would you like to proceed with claiming these rewards?",
                        metadata={
                            "available_rewards": {selected_pool: available_rewards[selected_pool]},
                            "receiver_address": wallet_address,
                        },
                    )
                else:
                    return AgentResponse.error(
                        error_message=f"No rewards found for your wallet address {wallet_address} in either pool. Claim cannot be processed."
                    )

            # Check last message for confirmation
            last_message = chat_history[-1]
            if last_message.role == "assistant" and "Would you like to proceed" in last_message.content:
                user_input = request.prompt.content.lower()
                if any(word in user_input for word in ["yes", "proceed", "confirm", "claim"]):
                    return await self._prepare_transactions(wallet_address, last_message.metadata)
                else:
                    return AgentResponse.success(
                        content="Please confirm if you want to proceed with the claim by saying 'yes', 'proceed', 'confirm', or 'claim'."
                    )

            messages = [
                SystemMessage(
                    content=(
                        "You are a MOR claims agent that helps users claim their MOR rewards. "
                        "Ask for clarification if a request is ambiguous."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _prepare_transactions(self, wallet_address: str, metadata: Dict[str, Any]) -> AgentResponse:
        """Prepare claim transactions for the given wallet."""
        try:
            available_rewards = metadata["available_rewards"]
            receiver_address = metadata["receiver_address"]
            transactions = []

            for pool_id in available_rewards.keys():
                try:
                    tx_data = tools.prepare_claim_transaction(pool_id, receiver_address)
                    transactions.append({"pool": pool_id, "transaction": tx_data})
                except Exception as e:
                    return AgentResponse.error(
                        error_message=f"Error preparing transaction for pool {pool_id}: {str(e)}"
                    )

            return AgentResponse.action_required(
                content="Transactions prepared successfully",
                action_type="claim",
                metadata={"transactions": transactions, "claim_tx_cb": "/claim"},
            )

        except Exception as e:
            logger.error(f"Error preparing transactions: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate MOR claims tool based on function name."""
        try:
            if func_name == "get_claim_status":
                status = tools.get_claim_status(args["transaction_hash"])
                return AgentResponse.success(content=status)
            else:
                return AgentResponse.error(error_message=f"Unknown tool: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))
