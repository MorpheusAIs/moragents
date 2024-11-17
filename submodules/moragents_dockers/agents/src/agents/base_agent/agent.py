import json
import threading
import logging
import os
from cdp import Cdp, Wallet
from datetime import datetime
from typing import Dict, Any
from .config import Config
from src.agents.base_agent import tools

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, config, llm, embeddings):
        """
        Initialize the BaseAgent for sending transactions on Base.
        """
        self.config = config
        self.llm = llm
        self.embeddings = embeddings    
        self.tools_provided = tools.get_tools()
        self.scheduled_tasks: Dict[str, threading.Thread] = {}
        self.wallets: Dict[str, Wallet] = {}
        self.wallet_manager = tools.WalletManager()
        self.transaction_manager = tools.TransactionManager(self.wallet_manager)
        self.wallet_file = "wallet.txt"

        # Mapping of function names to handler methods
        self.function_handlers = {
            "gasless_usdc_transfer": self.handle_gasless_usdc_transfer,
            "eth_transfer": self.handle_eth_transfer,
            "initialize_cdp_wallet": self.initialize_cdp_wallet
        }

    def chat(self, request):
        try:
            data = request.get_json()
            if not data:
                return {"error": "Invalid request data"}, 400

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


    def handle_function_call(self, func_name, args, chain_id, wallet_address):
        handler = self.function_handlers.get(func_name)
        if handler:
            return handler(args, chain_id, wallet_address)
        else:
            logger.error(f"Function '{func_name}' not supported.")
            return f"Error: Function '{func_name}' not supported.", "assistant", None

    def handle_gasless_usdc_transfer(self, args):
        toAddress = args.get("toAddress")
        amount = args.get("amount")
        if not toAddress or not amount:
            logger.error("Missing 'toAddress' or 'amount' in gasless_usdc_transfer arguments.")
            return "Error: Missing 'toAddress' or 'amount'.", "assistant", None

        logger.info(f"Initiating gasless USDC transfer to {toAddress} of amount {amount}.")

        try:
            res, role = self.transaction_manager.send_gasless_usdc_transaction(toAddress, amount)
            logger.info(f"Transfer result: {res}")
            return f"Successfully sent {amount} USDC to {toAddress} gaslessly.", role, None
        except tools.InsufficientFundsError as e:
            logger.error(f"Insufficient funds: {str(e)}")
            return str(e), "assistant", None

    def handle_eth_transfer(self, args):
        toAddress = args.get("toAddress")
        amount = args.get("amount")
        if not toAddress or not amount:
            logger.error("Missing 'toAddress' or 'amount' in eth_transfer arguments.")
            return "Error: Missing 'toAddress' or 'amount'.", "assistant", None

        logger.info(f"Initiating ETH transfer to {toAddress} of amount {amount}.")

        try:
            res, role = self.transaction_manager.send_eth_transaction(toAddress, amount)
            logger.info(f"Transfer result: {res}")
            return f"Successfully sent {amount} ETH to {toAddress}.", role, None
        except tools.InsufficientFundsError as e:
            logger.error(f"Insufficient funds: {str(e)}")
            return str(e), "assistant", None
        
    def initialize_cdp_wallet(self, request):
        """ 
        Set CDP credentials and save wallet data
        """
        data = request.get_json()

        cdp_api_key = data.get("cdp_api_key")
        cdp_api_secret = data.get("cdp_api_secret")

        if not cdp_api_key or not cdp_api_secret:
            return {"error": "CDP credentials not found"}, 400
        
        try:
            # Initialize CDP client
            self.client = Cdp.configure(cdp_api_key, cdp_api_secret)

            existing_wallet = self.wallet_manager.load_wallet()
            if existing_wallet:
                wallet.load_seed(existing_wallet)
                return {"message": "CDP credentials set and wallet loaded successfully"}, 200
            
            else:
                # Create a new wallet and save its data
                wallet = self.wallet_manager.create_wallet()

                # Fund the wallet
                self.wallet_manager.fund_wallet(wallet, asset_id="eth")
                self.wallet_manager.fund_wallet(wallet, asset_id="usdc")
            
            # Save the wallet data
            if self.wallet_manager.save_wallet(wallet):
                return {"message": "CDP credentials set and wallet saved successfully"}, 200
            else:
                return {"error": "Failed to save wallet data"}, 500
                
        except Exception as e:
            logger.error(f"Error in initialize_cdp_credentials: {str(e)}")
            return {"error": f"Failed to set CDP credentials: {str(e)}"}, 500
