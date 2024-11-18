import os
import json
import requests
import logging
import time
import threading
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from cdp import Cdp, Wallet, Transaction
from src.config import Config
from src.cdp import CDPWalletManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ToolError(Exception):
    """Base exception for tool operations"""
    pass

class InsufficientFundsError(ToolError):
    """Raised when there are insufficient funds"""
    pass

class ConfigurationError(ToolError):
    """Raised when there are configuration issues"""
    pass

class TransactionManager:
    """Class to manage cryptocurrency transactions"""
    
    def __init__(self, wallet_manager: CDPWalletManager):
        self.wallet_manager = wallet_manager

    def send_gasless_usdc_transaction(
        self,
        to_address: str,
        amount: str
    ) -> Tuple[Dict[str, Any], str]:
        """Send a gasless USDC transaction"""
        try:

            wallet_manager = CDPWalletManager()
            wallet =  wallet_manager.load_wallet()

            logger.info(f"Sending gasless USDC transfer to {to_address} with amount {amount}")

            # Execute transaction
            tx = wallet.transfer(
                amount,
                "usdc",
                to_address,
                gasless=True
            )
            
            logger.info(f"Gasless USDC Transfer completed: {tx}")
            
            return "sent gasless USDC transfer", "gasless_usdc_transfer"

        except Exception as e:
            logger.error(f"Error in gasless USDC transfer: {str(e)}")
            if "insufficient funds" in str(e).lower():
                raise InsufficientFundsError(str(e))
            raise ToolError(f"Failed to send USDC: {str(e)}")

    async def send_eth_transaction(
        self,
        to_address: str,
        amount: str
    ) -> Tuple[Dict[str, Any], str]:
        """Send an ETH transaction"""
        try:

            wallet_manager = CDPWalletManager()
            wallet =  wallet_manager.load_wallet()

            # Execute transaction
            tx = wallet.transfer(
                amount,
                "eth",
                to_address
            )
            
            logger.info(f"ETH Transfer completed: {tx}")

            return "sent ETH transfer", "eth_transfer"

        except Exception as e:
            logger.error(f"Error in ETH transfer: {str(e)}")
            if "insufficient funds" in str(e).lower():
                raise InsufficientFundsError(str(e))
            raise ToolError(f"Failed to send ETH: {str(e)}")

def get_tools() -> List[Dict[str, Any]]:
    """Get available tool definitions"""
    return [
        {
            "type": "function",
            "function": {
                "name": "gasless_usdc_transfer",
                "description": "Transfer USDC to another user without gas fees",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toAddress": {
                            "type": "string",
                            "description": "Recipient's address"
                        },
                        "amount": {
                            "type": "string", 
                            "description": "Amount of USDC to transfer"
                        }
                    },
                    "required": ["toAddress", "amount"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "eth_transfer",
                "description": "Transfer ETH to another user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "toAddress": {
                            "type": "string",
                            "description": "Recipient's address"
                        },
                        "amount": {
                            "type": "string",
                            "description": "Amount of ETH to transfer"
                        }
                    },
                    "required": ["toAddress", "amount"]
                }
            }
        }
    ]