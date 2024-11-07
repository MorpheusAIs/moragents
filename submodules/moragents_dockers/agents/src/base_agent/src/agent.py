import json
import threading
import logging
from cdp import Cdp, Wallet
from datetime import datetime
from typing import Dict, Any
from .config import Config
from base_agent.src import tools

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_info: Dict[str, Any], llm: Any, llm_ollama: Any, embeddings: Any, flask_app):
        """
        Initialize the BaseAgent for sending transactions on Base.
        """
        self.agent_info = agent_info
        self.llm = llm
        self.llm_ollama = llm_ollama
        self.embeddings = embeddings
        self.flask_app = flask_app
        self.tools_provided = tools.get_tools()
        self.scheduled_tasks: Dict[str, threading.Thread] = {}
        self.wallets: Dict[str, Wallet] = {}

        # Mapping of function names to handler methods
        self.function_handlers = {
            "gasless_usdc_transfer": self.handle_gasless_usdc_transfer,
            "eth_transfer": self.handle_eth_transfer,
        }

    def chat(self, request):
        try:
            data = request.get_json()
            if not data:
                return {"error": "Invalid request data"}, 400

            # Check CDP client initialization
            if not self.client and not self.initialize_cdp_client():
                return {
                    "error": "CDP client not initialized. Please set API credentials.",
                    "needs_credentials": True
                }, 400

            # Handle strategy status request
            if 'strategy_id' in data:
                response, role = self.handle_get_status({"strategy_id": data['strategy_id']})
                return {"role": role, "content": response}

            # Handle chat prompt
            if 'prompt' in data:
                prompt = data['prompt']
                wallet_address = data.get('wallet_address')
                chain_id = data.get('chain_id')
                response, role, next_turn_agent = self.handle_request(prompt, chain_id, wallet_address)
                return {"role": role, "content": response, "next_turn_agent": next_turn_agent}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {"Error": str(e)}, 500

    def handle_request(self, message, chain_id, wallet_address):
        logger.info(f"Message: {message}")
        logger.info(f"Chain ID: {chain_id}")
        logger.info(f"Wallet Address: {wallet_address}")

        # System prompt that includes descriptions of available functions
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are an agent that can perform various financial transactions. "
                    "You have access to the following functions:\n"
                    "1. gasless_usdc_transfer(toAddress: string, amount: string): Transfer USDC to another user without gas fees.\n"
                    "2. eth_transfer(toAddress: string, amount: string): Transfer ETH to another user.\n"
                    "When you need to perform an action, use the appropriate function with the correct arguments."
                )
            }
        ]

        if isinstance(message, dict):
            user_content = message.get('content', '')
        else:
            user_content = message

        prompt.append({
            "role": "user",
            "content": user_content
        })

        logger.info(f"Prompt: {prompt}")

        result = self.llm.create_chat_completion(
            messages=prompt,
            tools=self.tools_provided,
            tool_choice="auto",
            temperature=0.01
        )

        logger.info(f"Result: {result}")

        # Process the LLM's response
        try:
            choice = result["choices"][0]["message"]
            if "tool_calls" in choice:
                func = choice["tool_calls"][0]['function']

                # remove the prefix from the function name
                func_name = func["name"].strip().split()[-1]
                logger.info(f"Function name: {func_name}")

                # Extract arguments
                args = json.loads(func["arguments"])
                logger.info(f"Arguments: {args}")

                # Call the appropriate handler
                return self.handle_function_call(func_name, args, chain_id, wallet_address)
            else:
                # No function call; return the assistant's message
                content = choice.get('content', '')
                return content, "assistant", None
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return "Error: Unable to process the request.", "assistant", None
        
    def initialize_cdp_client(self) -> bool:
        """Initialize CDP client with stored credentials"""
        try:
            api_key = self.flask_app.config.get("cdpApiKey")
            api_secret = self.flask_app.config.get("cdpApiSecret")
            
            if not all([api_key, api_secret]):
                logger.warning("CDP credentials not found")
                return False
                
            self.client = Cdp.configure(api_key, api_secret)
            return True
        except Exception as e:
            logger.error(f"CDP client initialization failed: {e}")
            return False


    def handle_function_call(self, func_name, args, chain_id, wallet_address):
        handler = self.function_handlers.get(func_name)
        if handler:
            return handler(args, chain_id, wallet_address)
        else:
            logger.error(f"Function '{func_name}' not supported.")
            return f"Error: Function '{func_name}' not supported.", "assistant", None

    def handle_gasless_usdc_transfer(self, args, chain_id, wallet_address):
        toAddress = args.get("toAddress")
        amount = args.get("amount")
        if not toAddress or not amount:
            logger.error("Missing 'toAddress' or 'amount' in gasless_usdc_transfer arguments.")
            return "Error: Missing 'toAddress' or 'amount'.", "assistant", None

        logger.info(f"Initiating gasless USDC transfer to {toAddress} of amount {amount}.")

        try:
            res, role = tools.send_gasless_usdc_transaction(toAddress, amount)
            logger.info(f"Transfer result: {res}")
            return f"Successfully sent {amount} USDC to {toAddress} gaslessly.", role, None
        except tools.InsufficientFundsError as e:
            logger.error(f"Insufficient funds: {str(e)}")
            return str(e), "assistant", None

    def handle_eth_transfer(self, args, chain_id, wallet_address):
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
