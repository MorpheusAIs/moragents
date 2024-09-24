import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from cdp import Wallet, Cdp

class DCAAgent:
    def __init__(self, agent_info: Dict[str, Any], llm: Any, llm_ollama: Any, embeddings: Any, flask_app):
        """
        Initialize the DCAAgent.

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
        self.cdp = Cdp(self.config.CDP_API_KEY, self.config.CDP_API_SECRET)

    def chat(self, request: Dict[str, Any], user_id: str) -> tuple[str, str]:
        """
        Process a chat request and schedule a purchase.

        Parameters:
        - request (dict): The user's request containing purchase details.
        - user_id (str): The unique identifier for the user.

        Returns:
        - tuple: A response message and the next turn agent.
        """
        try:
            token = request.get('token', 'ETH')
            spend_limit = float(request.get('spend_limit', 0.01))
            interval = int(request.get('interval', 24))

            if spend_limit <= 0 or interval <= 0:
                raise ValueError("Spend limit and interval must be positive numbers.")

            task_id = self.schedule_purchase(user_id, token, spend_limit, interval)

            response = f"Scheduled a recurring purchase of {spend_limit} {token} every {interval} hours. Task ID: {task_id}"
            next_turn_agent = self.agent_info["name"]
            return response, next_turn_agent
        except ValueError as e:
            return f"Error: {str(e)}", self.agent_info["name"]
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}", self.agent_info["name"]

    def schedule_purchase(self, user_id: str, token: str, amount: float, interval: int) -> str:
        """
        Schedule a recurring purchase task.

        Parameters:
        - user_id (str): The unique identifier for the user.
        - token (str): The token to purchase.
        - amount (float): The amount to spend on each purchase.
        - interval (int): The time interval between purchases in hours.

        Returns:
        - str: The unique task ID for the scheduled purchase.
        """
        task_id = f"{user_id}_{datetime.utcnow().timestamp()}"

        def task():
            while True:
                try:
                    self.execute_purchase(token, amount)
                except Exception as e:
                    print(f"Error executing purchase: {str(e)}")
                time.sleep(interval * 3600)

        t = threading.Thread(target=task, daemon=True)
        t.start()

        self.scheduled_tasks[task_id] = t

        return task_id

    def execute_purchase(self, token: str, amount: float) -> None:
        """
        Execute a single purchase transaction.

        Parameters:
        - token (str): The token to purchase.
        - amount (float): The amount to spend on the purchase.

        Raises:
        - Exception: If the trade fails or an error occurs.
        """
        try:
            wallet = Wallet.create("base-mainnet")
            trade = wallet.trade(amount, "eth", token.lower()).wait()
            print(f"Trade successfully completed: {trade}")
        except Exception as e:
            raise Exception(f"Failed to execute purchase: {str(e)}")

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.

        Parameters:
        - task_id (str): The unique identifier for the task to cancel.

        Returns:
        - bool: True if the task was successfully cancelled, False otherwise.
        """
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            return True
        return False