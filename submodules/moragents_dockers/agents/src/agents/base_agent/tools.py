import os
import json
import requests
import logging
import time
import threading
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

    async def _ensure_wallet_ready(self) -> Wallet:
        """Ensure wallet is loaded and ready for transactions"""
        wallet = await self.wallet_manager.load_wallet()
        if not wallet:
            raise ConfigurationError("Wallet not initialized. Please initialize CDP credentials first.")
        return wallet

    async def _execute_transaction(
        self,
        wallet: Wallet,
        to_address: str,
        amount: str,
        token: str,
        gasless: bool = False
    ) -> Transaction:
        """Execute a cryptocurrency transaction"""
        try:
            # Create the transfer
            if gasless and token.lower() == "usdc":
                tx = wallet.transfer(
                    amount=amount,
                    token=token.lower(),
                    to_address=to_address,
                    gasless=True
                )
            else:
                tx = wallet.transfer(
                    amount=amount,
                    token=token.lower(),
                    to_address=to_address
                )
            
            # Wait for confirmation
            confirmed_tx = tx.wait()
            
            if not confirmed_tx.is_confirmed():
                raise ToolError("Transaction failed to confirm")
                
            return confirmed_tx
            
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise ToolError(f"Transaction failed: {str(e)}")

    async def _save_transaction_result(
        self,
        wallet: Wallet,
        tx: Transaction,
        to_address: str,
        amount: str,
        token: str
    ) -> Dict[str, Any]:
        """Save transaction result and return formatted response"""
        result = {
            'success': True,
            'tx_hash': tx.hash,
            'from': str(wallet.default_address),
            'to': to_address,
            'amount': amount,
            'token': token.upper(),
            'timestamp': datetime.now().isoformat(),
            'block_number': tx.block_number,
            'confirmations': tx.confirmations
        }
        
        # Save updated wallet state
        await self._save_wallet_data(wallet, result)
        
        return result

    async def _save_wallet_data(self, wallet: Wallet, last_transaction: Dict[str, Any]) -> None:
        """Save wallet data with last transaction"""
        wallet_data = {
            'wallet_id': wallet.id,
            'address': str(wallet.default_address),
            'last_transaction': last_transaction,
            'updated_at': datetime.now().isoformat()
        }
        await self.wallet_manager._save_wallet_data(wallet)

    async def send_gasless_usdc_transaction(
        self,
        to_address: str,
        amount: str
    ) -> Tuple[Dict[str, Any], str]:
        """Send a gasless USDC transaction"""
        try:
            wallet = await self._ensure_wallet_ready()
            
            tx = await self._execute_transaction(
                wallet=wallet,
                to_address=to_address,
                amount=amount,
                token="usdc",
                gasless=True
            )
            
            logger.info(f"Gasless USDC Transfer completed: {tx.hash}")
            
            result = await self._save_transaction_result(
                wallet=wallet,
                tx=tx,
                to_address=to_address,
                amount=amount,
                token="USDC"
            )
            
            return result, "gasless_usdc_transfer"

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
            wallet = await self._ensure_wallet_ready()
            
            tx = await self._execute_transaction(
                wallet=wallet,
                to_address=to_address,
                amount=amount,
                token="eth",
                gasless=False
            )
            
            logger.info(f"ETH Transfer completed: {tx.hash}")
            
            result = await self._save_transaction_result(
                wallet=wallet,
                tx=tx,
                to_address=to_address,
                amount=amount,
                token="ETH"
            )
            
            return result, "eth_transfer"

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