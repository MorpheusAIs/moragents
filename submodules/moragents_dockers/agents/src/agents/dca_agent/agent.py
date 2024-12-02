import logging
from typing import Dict, Any, Optional

from src.models.messages import ChatRequest
from langchain.schema import HumanMessage, SystemMessage
from typing import Tuple, Optional
from src.stores import wallet_manager_instance

from src.agents.dca_agent.tools import get_tools

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DCAAgent:
    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        """
        Initialize the DCAAgent for managing DCA strategies.
        """
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self.wallet_id = f"dca_agent"

        # Get tools and bind to LLM
        self.tools = get_tools()
        self.tool_bound_llm = self.llm.bind_tools(self.tools)

        # Initialize CDP client and create agent wallet
        self.initialize_agent()

    def chat(self, request: ChatRequest):
        """Handle incoming chat requests"""
        try:
            data = request.dict()
            if not data:
                return {"error": "Invalid request data"}, 400

            # Check CDP client initialization and wallet
            if not wallet_manager_instance.configure_cdp_client():
                return {
                    "error": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True,
                }, 400

            if not wallet_manager_instance.has_wallet(self.wallet_id):
                if not self.initialize_agent():
                    return {"error": "Failed to initialize agent wallet"}, 500

            if "prompt" in data:
                return {"role": "assistant", "content": "Ready to set up DCA"}

            return {"error": "Missing required parameters"}, 400

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"error": str(e)}, 500

    def handle_request(self, message: str) -> Tuple[str, str, Optional[str]]:
        """Process request and route to appropriate handler"""
        logger.info(f"Processing message: {message}")

        # System prompt that includes descriptions of available tools
        tool_descriptions = "\n".join(
            f"{tool['name']}: {tool['description']}" for tool in self.tools
        )

        messages = [
            SystemMessage(
                content=(
                    "You are a DCA (Dollar Cost Averaging) agent that helps users create and manage "
                    "cryptocurrency trading strategies. Available actions:\n"
                    f"{tool_descriptions}"
                )
            ),
            HumanMessage(content=message),
        ]

        result = self.tool_bound_llm.invoke(messages)

        try:
            if result.tool_calls:
                tool_call = result.tool_calls[0]
                func_name = tool_call.get("name")
                args = tool_call.get("args", {})

                logger.info(f"Function name: {func_name}")
                logger.info(f"Arguments: {args}")

                if not func_name:
                    return "Error: No function name provided in tool call", "assistant", None

                try:
                    available_tools = [tool["name"] for tool in self.tools]
                    if func_name not in available_tools:
                        return f"Error: Function '{func_name}' not supported.", "assistant", None

                    wallet = wallet_manager_instance.get_wallet(self.wallet_id)
                    if not wallet:
                        return "Error: Agent wallet not found", "assistant", None

                    tool_result = getattr(self.tools, func_name)(wallet, **args)
                    return f"Successfully executed {func_name}", "assistant", None

                except Exception as e:
                    logger.error(f"Error executing tool {func_name}: {str(e)}")
                    return f"Error executing {func_name}: {str(e)}", "assistant", None
            else:
                content = result.content if hasattr(result, "content") else ""
                return content, "assistant", None

        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return "Error: Unable to process the request.", "assistant", None

    def initialize_agent(self) -> bool:
        """Initialize CDP client and create agent wallet if needed"""
        try:
            if not wallet_manager_instance.configure_cdp_client():
                logger.warning("Failed to configure CDP client")
                return False

            if not wallet_manager_instance.has_wallet(self.wallet_id):
                wallet_manager_instance.create_wallet(self.wallet_id)
                logger.info(f"Created new wallet for DCA agent")

            return True

        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            return False
