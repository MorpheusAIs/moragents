import json
import threading
import logging
from cdp import Cdp, Wallet
from datetime import datetime
from typing import Dict, Any
from .config import Config
from gasless_agent.src import tools

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

    def chat(self, request):
        try:
            data = request.get_json()
            if 'prompt' in data:
                prompt = data['prompt']
                wallet_address = data['wallet_address']
                chain_id = data['chain_id']
                response, role, next_turn_agent = self.handle_gasless_usdc_transfer_request(prompt, chain_id, wallet_address)
                return {"role": role, "content": response, "next_turn_agent": next_turn_agent}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def handle_gasless_usdc_transfer_request(self, message, chain_id, wallet_address) -> tuple[str, str]:

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a gasless agent that can transfer USDC to another user. You are given the amount, the recipient user ID, and the token. You need to transfer the USDC to the recipient user ID."
                )
            }
        ]

        prompt.extend(message)

        result = self.llm.create_chat_completion(
            messages=prompt,
            tools=self.tools_provided,
            tool_choice="auto",
            temperature=0.01
        )

        if "tool_calls" in result["choices"][0]["message"].keys():
            func = result["choices"][0]["message"]["tool_calls"][0]['function']
            if func["name"] == "gasless_usdc_transfer":
                args = json.loads(func["arguments"])
                toAddress = args["toAddress"]
                amount = args["amount"]
                try:
                    res, role = tools.send_gasless_usdc_transfer(toAddress, amount)

                except (tools.InsufficientFundsError) as e:
                    self.context = []
                    return str(e), "assistant", None
                
                return res, role, None
            
        self.context.append({"role": "assistant", "content": result["choices"][0]["message"]['content']})
        
        return f"Sent a gasless transfer of {amount} usdc to user {toAddress}", self.agent_info["name"]

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

    def create_wallet(self) -> Wallet:
        """
        Create a new wallet for the user.

        Returns:
        - Wallet: The created wallet object.
        """
        try:
            # Configure CDP client (should fetch keys securely, avoid hardcoding)
            client = Cdp.configure()
            
            logger.info(f"Creating wallet on base-mainnet")
            logger.info(f"CDP client: {client}")
            
            wallet1 = client.Wallet.create()
            address = wallet1.default_address

            logger.info(f"Wallet created: {address}")

            return wallet1

        except Exception as e:
            logger.error(f"Error creating wallet: {str(e)}")
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
