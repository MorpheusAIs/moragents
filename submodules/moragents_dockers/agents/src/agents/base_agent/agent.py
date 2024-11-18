import json
import threading
import logging
import os
import asyncio
from cdp import Cdp, Wallet
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from .config import Config
from src.agents.base_agent import tools
from src.cdp import CDPWalletManager
from src.models.messages import ChatRequest

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
        self.transaction_manager = tools.TransactionManager(CDPWalletManager())
        self.context = []

        # Mapping of function names to handler methods
        self.function_handlers = {
            "gasless_usdc_transfer": self.handle_gasless_usdc_transfer,
            "eth_transfer": self.handle_eth_transfer,
        }

    def get_response(self, message, chain_id, wallet_address) -> Tuple[str, str, Optional[str]]:
        """
        Get response from LLM and process any tool calls
        
        Returns:
            Tuple[str, str, Optional[str]]: (content, role, next_agent)
        """
        system_prompt = (
            "You are an agent that can perform various financial transactions. "
            "You have access to the following functions:\n"
            "1. gasless_usdc_transfer(toAddress: string, amount: string): Transfer USDC to another user without gas fees.\n"
            "2. eth_transfer(toAddress: string, amount: string): Transfer ETH to another user.\n"
            "When you need to perform an action, use the appropriate function with the correct arguments."
        )

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        messages.extend(message)

        logger.info("Sending request to LLM with %d messages", len(messages))

        try:
            llm_with_tools = self.llm.bind_tools(self.tools_provided)
            result = llm_with_tools.invoke(messages)
            
            logger.info(f"Result: {result}")

            if result.tool_calls:
                # Check for tool calls
                tool_call = result.tool_calls[0]
                logger.info("Selected tool: %s", tool_call)
                func_name = tool_call.get("name")
                args = tool_call.get("args")
                logger.info("LLM suggested using tool: %s", func_name)
                    
                return self.handle_function_call(func_name, args, chain_id, wallet_address)
            else:
                # No tool calls, return the content directly
                return result.content or "", "assistant", None
                    
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
            return "Error: Unable to process the request.", "assistant", None

    def generate_response(self, prompt, chain_id, wallet_address):
        self.context.append(prompt)
        response, role, next_turn_agent = self.get_response(
            self.context, chain_id, wallet_address
        )
        return response, role, next_turn_agent

    def chat(self, request: ChatRequest):
        data = request.dict()
        try:
            if "prompt" in data:
                prompt = data["prompt"]
                wallet_address = data["wallet_address"]
                chain_id = data["chain_id"]
                response, role, next_turn_agent = self.generate_response(
                    prompt, chain_id, wallet_address
                )
                return {
                    "role": role,
                    "content": response,
                    "next_turn_agent": next_turn_agent,
                }
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            return {"Error": str(e)}, 500

    def handle_function_call(self, func_name, args, chain_id, wallet_address):
        handler = self.function_handlers.get(func_name)
        if handler:
            return handler(args, chain_id, wallet_address)
        else:
            logger.error(f"Function '{func_name}' not supported.")
            return f"Error: Function '{func_name}' not supported.", "assistant", None

    def handle_gasless_usdc_transfer(self, args, chain_id, wallet_address):
        """
        Handle gasless USDC transfer with chain_id and wallet_address parameters.
        """
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
        except Exception as e:
            logger.error(f"Error in transfer: {str(e)}")
            return f"Error: {str(e)}", "assistant", None

    def handle_eth_transfer(self, args, chain_id, wallet_address):
        """
        Handle ETH transfer with chain_id and wallet_address parameters.
        """
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
        except Exception as e:
            logger.error(f"Error in transfer: {str(e)}")
            return f"Error: {str(e)}", "assistant", None