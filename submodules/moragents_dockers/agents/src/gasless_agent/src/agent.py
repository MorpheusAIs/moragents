import threading
import logging
from cdp import Wallet, Cdp
from datetime import datetime
from typing import Dict, Any
from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GaslessAgent:
    def __init__(self, agent_info: Dict[str, Any], llm: Any, llm_ollama: Any, embeddings: Any, flask_app):
        """
        Initialize the GaslessAgent for sending gasless USDC transactions.

        Parameters:
        - agent_info (dict): Configuration details for the agent.
        - llm (object): The main language model instance.
        - llm_ollama (object): An additional language model instance.
        - embeddings (object): Embedding model for handling vector representations.
        - flask_app (Flask): The Flask application instance.
        """
        self.agent_info = agent_info
        self.llm = llm
        self.llm_ollama = llm_ollama
        self.embeddings = embeddings
        self.flask_app = flask_app
        self.scheduled_tasks: Dict[str, threading.Thread] = {}
        self.wallets: Dict[str, Wallet] = {}

    def chat(self, request: Dict[str, Any], user_id: str) -> tuple[str, str]:
        """
        Process a chat request and handle gasless USDC transactions.

        Parameters:
        - request (dict): The user's request containing transfer details.
        - user_id (str): The unique identifier for the user.

        Returns:
        - tuple: A response message and the next turn agent.
        """
        action = request.get('action', '').lower()
        try:
            if action == 'create_wallet':
                wallet = self.create_wallet(user_id)
                return f"Wallet created successfully. Address: {wallet.address}", self.agent_info["name"]

            elif action == 'transfer':
                return self.handle_transfer(request, user_id)

            else:
                return "Invalid action. Available actions: create_wallet, transfer", self.agent_info["name"]

        except ValueError as e:
            logger.error(f"ValueError in chat: {e}")
            return f"Error: {str(e)}", self.agent_info["name"]
        except Exception as e:
            logger.error(f"Unexpected error in chat: {e}")
            return f"An unexpected error occurred: {str(e)}", self.agent_info["name"]

    def handle_transfer(self, request: Dict[str, Any], user_id: str) -> tuple[str, str]:
        """
        Handle gasless USDC transfers.

        Parameters:
        - request (dict): The user's request containing transfer details.
        - user_id (str): The unique identifier for the user.

        Returns:
        - tuple: A response message and the next agent.
        """
        token = request.get('token', 'USDC')
        amount = float(request.get('amount', 0.00001))
        to_user_id = request.get('to_user_id')

        if not to_user_id:
            raise ValueError("Recipient user ID is required.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        task_id = self.schedule_transfer(user_id, to_user_id, token, amount)
        return f"Scheduled a gasless transfer of {amount} {token} to user {to_user_id}. Task ID: {task_id}", self.agent_info["name"]

    def set_cdp_api_key(self, request):
        """
        Set CDP API keys from the request.

        Parameters:
        - request (Flask request): Incoming request containing API keys.

        Returns:
        - dict: Success or error response.
        """
        data = request.get_json()
        required_keys = ["api_key", "api_secret"]

        if not all(key in data for key in required_keys):
            logger.warning("Missing required API credentials")
            return {"error": Config.ERROR_MISSING_API_CREDENTIALS}, 400

        for key in required_keys:
            self.flask_app.config[key] = data[key]

        return {"success": "API credentials saved successfully"}, 200

    def create_wallet(self, user_id: str) -> Wallet:
        """
        Create a new wallet for the user.

        Parameters:
        - user_id (str): The unique identifier for the user.

        Returns:
        - Wallet: The created wallet object.
        """
        try:
            # Configure CDP client (should fetch keys securely, avoid hardcoding)
            client = Cdp.configure('organizations/7281d7cc-3a36-4aea-a53f-c2c3f955139f/apiKeys/fbe1a6a8-b7e1-4572-a8cd-177f4d3a46ec', '-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIFJr0ZZWGg9nJuBzXombR1khs+h297HDu2QX9+pD1HS8oAoGCCqGSM49\nAwEHoUQDQgAELQl2Kuz5HSq6n9pf8EsUqaui26b/mSNbTExFzz6x7x1g4zGjVxyA\nTzxyxAGxP3CGrvWRzlzWwY8RWtH2BcTXdA==\n-----END EC PRIVATE KEY-----\n')
            wallet = client.Wallet.create("base-mainnet")
            self.wallets[user_id] = wallet

            logger.info(f"Wallet created for user {user_id}: {wallet.address}")
            return wallet

        except Exception as e:
            logger.error(f"Error creating wallet for user {user_id}: {str(e)}")
            raise

    def schedule_transfer(self, from_user_id: str, to_user_id: str, token: str, amount: float) -> str:
        """
        Schedule a gasless transfer.

        Parameters:
        - from_user_id (str): The sender's user ID.
        - to_user_id (str): The recipient's user ID.
        - token (str): The token to transfer.
        - amount (float): The amount to transfer.

        Returns:
        - str: The unique task ID for the scheduled transfer.
        """
        task_id = f"{from_user_id}_to_{to_user_id}_{datetime.utcnow().timestamp()}"

        def task():
            try:
                self.execute_transfer(from_user_id, to_user_id, token, amount)
            except Exception as e:
                logger.error(f"Error executing transfer: {str(e)}")

        t = threading.Thread(target=task, daemon=True)
        t.start()

        self.scheduled_tasks[task_id] = t
        return task_id

    def execute_transfer(self, from_user_id: str, to_user_id: str, token: str, amount: float):
        """
        Execute a scheduled gasless transfer.

        Parameters:
        - from_user_id (str): The sender's user ID.
        - to_user_id (str): The recipient's user ID.
        - token (str): The token to transfer.
        - amount (float): The amount to transfer.

        Raises:
        - Exception: If the transfer fails.
        """
        from_wallet = self.wallets.get(from_user_id)
        to_wallet = self.wallets.get(to_user_id)

        if not from_wallet or not to_wallet:
            raise ValueError("Both sender and recipient must have created wallets.")

        try:
            transfer = from_wallet.transfer(amount, token.lower(), to_wallet, gasless=True).wait()
            logger.info(f"Transfer completed: {amount} {token} from {from_wallet.address} to {to_wallet.address}")
        except Exception as e:
            raise Exception(f"Failed to execute transfer: {str(e)}")

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Parameters:
        - task_id (str): The unique identifier for the task to cancel.

        Returns:
        - bool: True if the task was successfully cancelled, False otherwise.
        """
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks.pop(task_id, None)
            logger.info(f"Task {task_id} cancelled.")
            return True
        logger.warning(f"Task {task_id} not found.")
        return False
