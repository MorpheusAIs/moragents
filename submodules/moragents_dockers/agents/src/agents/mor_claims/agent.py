import logging
from typing import Dict, Any

from src.agents.mor_claims import tools
from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from langchain.schema import HumanMessage, SystemMessage
from src.stores import agent_manager_instance

logger = logging.getLogger(__name__)


class MorClaimsAgent(AgentCore):
    """Agent for handling MOR token claims and rewards."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = tools.get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
        self.conversation_state = {}

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for MOR claims."""
        try:
            wallet_address = request.wallet_address

            if wallet_address not in self.conversation_state:
                self.conversation_state[wallet_address] = {"state": "initial"}

            state = self.conversation_state[wallet_address]["state"]

            if state == "initial":
                agent_manager_instance.set_active_agent("mor claims")

                rewards = {
                    0: tools.get_current_user_reward(wallet_address, 0),
                    1: tools.get_current_user_reward(wallet_address, 1),
                }
                available_rewards = {pool: amount for pool, amount in rewards.items() if amount > 0}

                if available_rewards:
                    selected_pool = max(available_rewards, key=available_rewards.get)
                    self.conversation_state[wallet_address]["available_rewards"] = {
                        selected_pool: available_rewards[selected_pool]
                    }
                    self.conversation_state[wallet_address]["receiver_address"] = wallet_address
                    self.conversation_state[wallet_address]["state"] = "awaiting_confirmation"
                    return AgentResponse.success(
                        content=f"You have {available_rewards[selected_pool]} MOR rewards available in pool {selected_pool}. Would you like to proceed with claiming these rewards?"
                    )
                else:
                    return AgentResponse.error(
                        error_message=f"No rewards found for your wallet address {wallet_address} in either pool. Claim cannot be processed."
                    )

            elif state == "awaiting_confirmation":
                user_input = request.prompt.content.lower()
                if any(word in user_input for word in ["yes", "proceed", "confirm", "claim"]):
                    return await self._prepare_transactions(wallet_address)
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

    async def _prepare_transactions(self, wallet_address: str) -> AgentResponse:
        """Prepare claim transactions for the given wallet."""
        try:
            available_rewards = self.conversation_state[wallet_address]["available_rewards"]
            receiver_address = self.conversation_state[wallet_address]["receiver_address"]
            transactions = []

            for pool_id in available_rewards.keys():
                try:
                    tx_data = tools.prepare_claim_transaction(pool_id, receiver_address)
                    transactions.append({"pool": pool_id, "transaction": tx_data})
                except Exception as e:
                    return AgentResponse.error(
                        error_message=f"Error preparing transaction for pool {pool_id}: {str(e)}"
                    )

            self.conversation_state[wallet_address]["transactions"] = transactions

            return AgentResponse.action_required(
                content={"transactions": transactions, "claim_tx_cb": "/claim"}, action_type="claim"
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
