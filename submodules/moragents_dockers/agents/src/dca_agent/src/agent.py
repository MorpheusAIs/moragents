import threading
import time
from datetime import datetime, timedelta

class DCAAgent:
    def __init__(self, agent_info, llm, llm_ollama, embeddings, flask_app):
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
        self.scheduled_tasks = {}

    def chat(self, request, user_id):

        # Parse user input to extract token, spend limit, and interval
        token = request.get('token', 'ETH')
        spend_limit = request.get('spend_limit', 0.01)
        interval = request.get('interval', 24)

        # Schedule the purchase
        task_id = self.schedule_purchase(user_id, token, spend_limit, interval)

        response = f"Scheduled a recurring purchase of {spend_limit} {token} every {interval} hours. Task ID: {task_id}"
        next_turn_agent = self.agent_info["name"]
        return response, next_turn_agent

    def schedule_purchase(self, user_id, token, amount, interval):
        
        task_id = f"{user_id}_{datetime.utcnow().timestamp()}"

        # Schedule the task
        def task():
            while True:
                self.execute_purchase(token, amount)
                time.sleep(interval * 3600)

        t = threading.Thread(target=task)
        t.daemon = True
        t.start()

        self.scheduled_tasks[task_id] = t

        return task_id

    def execute_purchase(self, token, amount):

        # TODO: Implement the logic to execute the purchase
        pass
