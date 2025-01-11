import logging
import requests
from typing import Optional

from fastapi import Request
from langchain.schema import HumanMessage, SystemMessage
from dataclasses import dataclass

from src.agents.token_swap import tools
from src.models.core import ChatRequest, AgentResponse
from src.agents.agent_core.agent import AgentCore
from src.stores.key_manager import key_manager_instance

logger = logging.getLogger(__name__)


@dataclass
class TokenSwapContext:
    chain_id: Optional[str] = None
    wallet_address: Optional[str] = None


class TokenSwapAgent(AgentCore):
    """Agent for handling token swap operations."""

    def __init__(self, config, llm, embeddings):
        super().__init__(config, llm, embeddings)
        self.tools_provided = tools.get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)
        self.context = TokenSwapContext()

    def _api_request_url(self, method_name, query_params, chain_id):
        base_url = self.config.APIBASEURL + str(chain_id)
        return f"{base_url}{method_name}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"

    def _check_allowance(self, token_address, wallet_address, chain_id):
        url = self._api_request_url(
            "/approve/allowance",
            {"tokenAddress": token_address, "walletAddress": wallet_address},
            chain_id,
        )
        response = requests.get(url, headers=tools.get_headers())
        return response.json()

    def _approve_transaction(self, token_address, chain_id, amount=None):
        query_params = {"tokenAddress": token_address, "amount": amount} if amount else {"tokenAddress": token_address}
        url = self._api_request_url("/approve/transaction", query_params, chain_id)
        response = requests.get(url, headers=tools.get_headers())
        return response.json()

    def _build_tx_for_swap(self, swap_params, chain_id):
        url = self._api_request_url("/swap", swap_params, chain_id)
        response = requests.get(url, headers=tools.get_headers())
        if response.status_code != 200:
            logger.error(f"1inch API error: {response.text}")
            raise ValueError(f"1inch API error: {response.text}")
        return response.json()

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for token swaps."""
        try:
            if not key_manager_instance.has_oneinch_keys():
                return AgentResponse.needs_info(
                    content="To help you with token swaps, I need your 1inch API key. Please set it up in Settings first."
                )

            # Store request context
            self.context.chain_id = request.chain_id
            self.context.wallet_address = request.wallet_address

            messages = [
                SystemMessage(
                    content=(
                        "You are a helpful assistant that processes token swap requests. "
                        "When a user wants to swap tokens, analyze their request and provide a SINGLE tool call with complete information. "
                        "Always return a single 'swap_agent' tool call with all three required parameters: "
                        "- token1: the source token "
                        "- token2: the destination token "
                        "- value: the amount to swap "
                        "If any information is missing from the user's request, do not make a tool call. Instead, respond asking for the missing information."
                    )
                ),
                HumanMessage(content=request.prompt.content),
            ]

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: dict) -> AgentResponse:
        """Execute the appropriate swap tool based on function name."""
        try:
            if func_name == "swap_agent":
                required_args = ["token1", "token2", "value"]
                if not all(arg in args for arg in required_args):
                    return AgentResponse.needs_info(
                        content="Please provide all required parameters: source token (token1), destination token (token2), and amount to swap (value)."
                    )

                if not args["value"]:
                    return AgentResponse.needs_info(content="Please specify the amount you want to swap.")

                try:
                    swap_result, _ = tools.swap_coins(
                        args["token1"],
                        args["token2"],
                        float(args["value"]),
                        self.context.chain_id,
                        self.context.wallet_address,
                    )

                    # Return an action_required response with swap details
                    return AgentResponse.action_required(
                        content="Please review and confirm your swap transaction:",
                        action_type="swap",
                        metadata=swap_result,
                    )
                except (tools.InsufficientFundsError, tools.TokenNotFoundError, tools.SwapNotPossibleError) as e:
                    return AgentResponse.needs_info(content=str(e))
                except ValueError:
                    return AgentResponse.needs_info(
                        content="Something went wrong. Please try again and make sure your Metamask is connected."
                    )
            else:
                return AgentResponse.needs_info(
                    content=f"I don't know how to {func_name}. Please try a different action."
                )

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def get_allowance(self, token_address: str, wallet_address: str, chain_id: str) -> AgentResponse:
        """Check token allowance for a wallet."""
        try:
            result = self._check_allowance(token_address, wallet_address, chain_id)
            return AgentResponse.success(content="Allowance checked successfully", metadata=result)
        except Exception as e:
            return AgentResponse.error(error_message=str(e))

    async def approve(self, token_address: str, chain_id: str, amount: str) -> AgentResponse:
        """Approve token spending."""
        try:
            result = self._approve_transaction(token_address, chain_id, amount)
            return AgentResponse.success(content="Approval transaction created", metadata=result)
        except Exception as e:
            return AgentResponse.error(error_message=str(e))

    async def swap(self, request_data: dict) -> AgentResponse:
        """Build swap transaction."""
        try:
            if not all(k in request_data for k in ["src", "dst", "walletAddress", "amount", "slippage", "chain_id"]):
                return AgentResponse.needs_info(
                    content="Please provide all required parameters: source token, destination token, wallet address, amount, slippage, and chain ID."
                )

            swap_params = {
                "src": request_data["src"],
                "dst": request_data["dst"],
                "amount": request_data["amount"],
                "from": request_data["walletAddress"],
                "slippage": request_data["slippage"],
                "disableEstimate": False,
                "allowPartialFill": False,
            }

            result = self._build_tx_for_swap(swap_params, request_data["chain_id"])
            return AgentResponse.success(content="Swap transaction created", metadata=result)
        except Exception as e:
            return AgentResponse.error(error_message=str(e))

    async def tx_status(self, request: Request) -> AgentResponse:
        """Handle transaction status updates."""
        try:
            request_data = await request.json()
            status = request_data.get("status")
            tx_hash = request_data.get("tx_hash", "")
            tx_type = request_data.get("tx_type", "")

            response = ""
            if status == "cancelled":
                response = f"The {tx_type} transaction has been cancelled."
            elif status == "success":
                response = f"The {tx_type} transaction was successful."
            elif status == "failed":
                response = f"The {tx_type} transaction has failed."
            elif status == "initiated":
                response = "Transaction has been sent, please wait for it to be confirmed."

            if tx_hash:
                response = response + f" The transaction hash is {tx_hash}."

            if status == "success" and tx_type == "approve":
                response = response + " Please proceed with the swap transaction."
            elif status != "initiated":
                response = response + " Is there anything else I can help you with?"

            if status != "initiated":
                # Reset context for new conversation
                self.context = TokenSwapContext()

            return AgentResponse.success(content=response)

        except Exception as e:
            logger.error(f"Error processing transaction status: {str(e)}")
            return AgentResponse.error(error_message=str(e))
