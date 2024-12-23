import logging
from typing import Any, Dict, Optional, Tuple

from src.agents.base_agent import tools
from src.models.messages import ChatRequest
from langchain.schema import HumanMessage, SystemMessage
from src.agents.base_agent.config import Config
from src.stores import wallet_manager_instance

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

        # Bind tools to LLM
        self.tool_bound_llm = self.llm.bind_tools(self.config.tools)

    def chat(self, request: ChatRequest) -> Dict[str, Any]:
        try:
            data = request.dict()
            logger.info(f"Received chat request: {data}")

            if not data:
                return {"role": "assistant", "content": "Invalid request data. Please try again."}

            # Check CDP client initialization
            if not wallet_manager_instance.configure_cdp_client():
                return {
                    "role": "assistant",
                    "content": "CDP client not initialized. Please set API credentials.",
                }

            # Check for active wallet
            active_wallet = wallet_manager_instance.get_active_wallet()
            if not active_wallet:
                return {
                    "role": "assistant",
                    "content": "No active wallet selected. Please select or create a wallet first.",
                }

            if "prompt" in data:
                prompt = data["prompt"]
                wallet_address = data.get("wallet_address")
                chain_id = data.get("chain_id")
                response_content = self.handle_request(prompt, chain_id, wallet_address)
                return {
                    "role": "assistant",
                    "content": response_content,
                }
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {
                    "role": "assistant",
                    "content": "Missing required parameters. Please provide a prompt.",
                }

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}, agent: {self.agent_info['name']}")
            raise e

    def handle_request(
        self, message: dict[str, any], chain_id: Optional[str], wallet_address: Optional[str]
    ) -> Dict[str, Any]:
        logger.info(f"Message: {message}")
        logger.info(f"Chain ID: {chain_id}")
        logger.info(f"Wallet Address: {wallet_address}")

        # System prompt that includes descriptions of available tools
        tool_descriptions = "\n".join(f"{tool['name']}: {tool['description']}" for tool in self.config.tools)

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
                    return {
                        "message": "Error: No function name provided in tool call",
                        "actionType": None,
                    }

                # Handle swap and transfer tools differently
                if func_name == "swap_assets":
                    return {"message": "Ready to perform swap", "actionType": "swap"}
                elif func_name == "transfer_asset":
                    return {"message": "Ready to perform transfer", "actionType": "transfer"}
                elif func_name == "get_balance":
                    # Get active wallet from wallet manager
                    wallet = wallet_manager_instance.get_active_wallet()
                    if not wallet:
                        return {"message": "Error: No active wallet found", "actionType": None}

                    try:
                        tool_result = tools.get_balance(wallet, asset_id=args.get("asset_id").lower())
                        balance = tool_result["balance"]
                        asset = tool_result["asset"]
                        address = tool_result["address"]
                        return {
                            "message": f"Your wallet {address} has a balance of {balance} {asset}",
                            "actionType": None,
                        }
                    except ValueError as e:
                        return {"message": f"Error: {str(e)}", "actionType": None}
                else:
                    return {
                        "message": f"Error: Function '{func_name}' not supported.",
                        "actionType": None,
                    }

            else:
                # No function call; return the assistant's message
                content = result.content if hasattr(result, "content") else ""
                return {"message": content, "actionType": None}

        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return {"message": "Error: Unable to process the request.", "actionType": None}
