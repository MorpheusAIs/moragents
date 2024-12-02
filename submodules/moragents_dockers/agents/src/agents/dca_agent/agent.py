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
                return {"error": "Invalid request data"}, 400

            # Check CDP client initialization and active wallet
            if not wallet_manager_instance.configure_cdp_client():
                return {
                    "error": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True,
                }, 400

            active_wallet = wallet_manager_instance.get_active_wallet()
            if not active_wallet:
                return {
                    "error": "No active wallet selected. Please select or create a wallet first."
                }, 400

            if "prompt" in data:
                return {"role": "assistant", "content": "Ready to set up DCA"}

            return {"error": "Missing required parameters"}, 400

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"error": str(e)}, 500
