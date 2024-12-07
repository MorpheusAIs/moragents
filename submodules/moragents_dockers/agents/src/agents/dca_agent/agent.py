import logging
from typing import Dict, Any

from src.models.messages import ChatRequest
from src.stores import wallet_manager_instance

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

    def chat(self, request: ChatRequest):
        """Handle incoming chat requests"""
        try:
            data = request.dict()
            if not data:
                return {"role": "assistant", "content": "Invalid request data"}

            # Check CDP client initialization and active wallet
            if not wallet_manager_instance.configure_cdp_client():
                return {
                    "role": "assistant",
                    "content": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True,
                }

            active_wallet = wallet_manager_instance.get_active_wallet()
            if not active_wallet:
                return {
                    "role": "assistant",
                    "content": "No active wallet selected. Please select or create a wallet first.",
                }

            if "prompt" in data:
                return {"role": "assistant", "content": "Ready to set up DCA"}

            return {"role": "assistant", "content": "Missing required parameters"}

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"role": "assistant", "content": str(e)}
