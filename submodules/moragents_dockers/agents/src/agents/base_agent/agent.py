import json
import logging
from typing import Any, Dict, Optional, Tuple

from cdp import Cdp, Wallet
from src.agents.base_agent import tools
from src.models.messages import ChatRequest
from src.stores import key_manager
from langchain.schema import HumanMessage, SystemMessage
from src.agents.base_agent.config import Config

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
        self.config = Config()
        self.client: Optional[Cdp] = None
        self.wallets: Dict[str, Wallet] = {}

        # Bind tools to LLM
        self.tool_bound_llm = self.llm.bind_tools(self.config.tools)

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
        """Initialize CDP client and wallet with stored credentials"""
        try:
            if not key_manager.has_coinbase_keys():
                logger.warning("CDP credentials not found")
                return False

            keys = key_manager.get_coinbase_keys()

            # Configure CDP with credentials
            self.client = Cdp.configure(
                keys.CDP_API_KEY,
                keys.CDP_API_SECRET,
            )

            # Create wallet for agent
            self.wallets["default"] = Wallet.create()

            return True
        except Exception as e:
            logger.error(f"CDP client/wallet initialization failed: {e}")
            return False

    def handle_request(
        self, message: dict[str, any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Tuple[str, str, Optional[str]]:
        logger.info(f"Message: {message}")
        logger.info(f"Chain ID: {chain_id}")
        logger.info(f"Wallet Address: {wallet_address}")

        # System prompt that includes descriptions of available tools
        tool_descriptions = "\n".join(
            f"{tool['name']}: {tool['description']}" for tool in self.config.tools
        )

        messages = [
            SystemMessage(
                content=(
                    "You are an agent that can perform various financial transactions on Base. "
                    f"You have access to the following functions:\n{tool_descriptions}\n"
                    "When you need to perform an action, use the appropriate function with the correct arguments."
                )
            ),
        ]

        messages.append(HumanMessage(content=message.get("content")))

        logger.info(f"Messages: {messages}")

        result = self.tool_bound_llm.invoke(messages)

        logger.info(f"Result: {result}")

        # Process the LLM's response
        try:
            if result.tool_calls:
                # Get first tool call
                tool_call = result.tool_calls[0]

                # Extract function name and args from the tool call dict
                func_name = tool_call.get("name")
                args = tool_call.get("args", {})

                logger.info(f"Function name: {func_name}")
                logger.info(f"Arguments: {args}")

                if not func_name:
                    return "Error: No function name provided in tool call", "assistant", None

                # Execute the tool
                try:
                    # Check if function exists in tools by comparing against tool names
                    available_tools = [tool["name"] for tool in self.config.tools]
                    if func_name not in available_tools:
                        return f"Error: Function '{func_name}' not supported.", "assistant", None

                    tool_result, role = getattr(tools, func_name)(self.wallets["default"], **args)

                    success_msg = f"Successfully executed {func_name}"
                    if isinstance(tool_result, dict) and "tx_hash" in tool_result:
                        success_msg += f" (tx: {tool_result['tx_hash']})"

                    return success_msg, role, None

                except Exception as e:
                    logger.error(f"Error executing tool {func_name}: {str(e)}")
                    return f"Error executing {func_name}: {str(e)}", "assistant", None
            else:
                # No function call; return the assistant's message
                content = result.content if hasattr(result, "content") else ""
                return content, "assistant", None

        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return "Error: Unable to process the request.", "assistant", None
