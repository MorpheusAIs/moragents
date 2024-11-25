import json
import logging
from typing import Any, Dict, Optional, Tuple

from cdp import Cdp, Wallet
from src.agents.base_agent import tools
from src.models.messages import ChatRequest
from src.stores import key_manager
from langchain.schema import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, agent_info: Dict[str, Any], llm: Any, embeddings: Any):
        """
        Initialize the BaseAgent for sending transactions on Base.
        """
        self.agent_info = agent_info
        self.llm = llm
        self.embeddings = embeddings
        self.tools_provided = tools.get_tools()
        self.client: Optional[Cdp] = None
        self.wallets: Dict[str, Wallet] = {}

        # Bind tools to LLM
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

        # Mapping of function names to handler methods
        self.function_handlers = {
            "gasless_usdc_transfer": self.handle_gasless_usdc_transfer,
            "eth_transfer": self.handle_eth_transfer,
        }

    def chat(self, request: ChatRequest) -> Dict[str, Any]:
        try:
            data = request.dict()
            logger.info(f"Received chat request: {data}")

            if not data:
                return {"error": "Invalid request data"}

            # Check CDP client initialization
            if not self.client and not self.initialize_cdp_client():
                return {
                    "error": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True,
                }

            if "prompt" in data:
                prompt = data["prompt"]
                wallet_address = data.get("wallet_address")
                chain_id = data.get("chain_id")
                response, role, next_turn_agent = self.handle_request(
                    prompt, chain_id, wallet_address
                )
                return {
                    "role": role,
                    "content": response,
                    "next_turn_agent": next_turn_agent,
                }
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {"error": "Missing required parameters"}

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}, agent: {self.agent_info['name']}")
            raise e

    def initialize_cdp_client(self) -> bool:
        """Initialize CDP client with stored credentials"""
        try:
            if not key_manager.has_coinbase_keys():
                logger.warning("CDP credentials not found")
                return False

            keys = key_manager.get_coinbase_keys()
            self.client = Cdp.configure(keys.cdp_api_key, keys.cdp_api_secret)
            return True
        except Exception as e:
            logger.error(f"CDP client initialization failed: {e}")
            return False

    def handle_request(
        self, message: str, chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        logger.info(f"Message: {message}")
        logger.info(f"Chain ID: {chain_id}")
        logger.info(f"Wallet Address: {wallet_address}")

        # System prompt that includes descriptions of available functions
        messages = [
            SystemMessage(
                content=(
                    "You are an agent that can perform various financial transactions on Base. "
                    "You have access to the following functions:\n"
                    "1. gasless_usdc_transfer(toAddress: string, amount: string): Transfer USDC to another user without gas fees.\n"
                    "2. eth_transfer(toAddress: string, amount: string): Transfer ETH to another user.\n"
                    "When you need to perform an action, use the appropriate function with the correct arguments."
                )
            ),
        ]

        if isinstance(message, dict):
            user_content = message.get("content", "")
        else:
            user_content = message

        messages.append(HumanMessage(content=user_content))

        logger.info(f"Messages: {messages}")

        result = self.tool_bound_llm.invoke(messages)

        logger.info(f"Result: {result}")

        # Process the LLM's response
        try:
            if result.tool_calls:
                tool_call = result.tool_calls[0]
                func_name = tool_call.function.name.strip().split()[-1]
                logger.info(f"Function name: {func_name}")

                # Extract arguments
                args = json.loads(tool_call.function.arguments)
                logger.info(f"Arguments: {args}")

                # Call the appropriate handler
                return self.handle_function_call(func_name, args, chain_id, wallet_address)
            else:
                # No function call; return the assistant's message
                content = result.content or ""
                return content, "assistant", None
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return "Error: Unable to process the request.", "assistant", None

    def handle_function_call(
        self,
        func_name: str,
        args: Dict[str, Any],
        chain_id: Optional[str],
        wallet_address: Optional[str],
    ) -> Tuple[str, str, Optional[str]]:
        handler = self.function_handlers.get(func_name)
        if handler:
            return handler(args, chain_id, wallet_address)
        else:
            logger.error(f"Function '{func_name}' not supported.")
            return f"Error: Function '{func_name}' not supported.", "assistant", None

    def handle_gasless_usdc_transfer(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        toAddress = args.get("toAddress")
        amount = args.get("amount")
        if not toAddress or not amount:
            logger.error("Missing 'toAddress' or 'amount' in gasless_usdc_transfer arguments.")
            return "Error: Missing 'toAddress' or 'amount'.", "assistant", None

        logger.info(f"Initiating gasless USDC transfer to {toAddress} of amount {amount}.")

        try:
            res, role = tools.send_gasless_usdc_transaction(toAddress, amount)
            logger.info(f"Transfer result: {res}")
            return (
                f"Successfully sent {amount} USDC to {toAddress} gaslessly.",
                role,
                None,
            )
        except tools.InsufficientFundsError as e:
            logger.error(f"Insufficient funds: {str(e)}")
            return str(e), "assistant", None

    def handle_eth_transfer(
        self, args: Dict[str, Any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        toAddress = args.get("toAddress")
        amount = args.get("amount")
        if not toAddress or not amount:
            logger.error("Missing 'toAddress' or 'amount' in eth_transfer arguments.")
            return "Error: Missing 'toAddress' or 'amount'.", "assistant", None

        logger.info(f"Initiating ETH transfer to {toAddress} of amount {amount}.")

        try:
            res, role = tools.send_eth_transaction(toAddress, amount)
            logger.info(f"Transfer result: {res}")
            return f"Successfully sent {amount} ETH to {toAddress}.", role, None
        except tools.InsufficientFundsError as e:
            logger.error(f"Insufficient funds: {str(e)}")
            return str(e), "assistant", None
