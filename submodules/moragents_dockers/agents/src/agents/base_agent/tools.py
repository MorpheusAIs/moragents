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

class WalletManager:
    """Class to manage wallet operations and persistence"""
    
    def __init__(self, wallet_file: str = "wallet_data.json"):
        self.wallet_file = wallet_file
        self._client: Optional[Cdp] = None
        self._client_lock = threading.Lock()

    def get_cdp_client(self) -> Cdp:
        """Get or create CDP client singleton with thread safety"""
        with self._client_lock:
            if not self._client:
                api_key = Config.CDP_API_KEY
                api_secret = Config.CDP_API_SECRET
                
                if not api_key or not api_secret:
                    raise ConfigurationError("CDP credentials not found in config")
                
                try:
                    self._client = Cdp.configure(
                        api_key,
                        api_secret
                    )
                except Exception as e:
                    raise ConfigurationError(f"Failed to initialize CDP client: {str(e)}")
            
            return self._client

    def reset_client(self) -> None:
        """Reset the CDP client (useful when credentials change)"""
        with self._client_lock:
            self._client = None

    async def create_wallet(self) -> Wallet:
        """Create a new wallet"""
        try:
            wallet = Wallet.create()
            logger.info(f"Wallet created: {wallet.default_address}")
            return wallet
        except Exception as e:
            raise ToolError(f"Failed to create wallet: {str(e)}")

    async def save_wallet(self, wallet_data: Dict[str, Any]) -> bool:
        """
        Save wallet data to a file.
        Args:
            wallet_data: Dictionary containing wallet information
        Returns:
            bool: True if successful
        """
        try:
            with open(self.wallet_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            logger.info(f"Wallet data saved successfully to {self.wallet_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving wallet data: {str(e)}")
            return False

    async def load_wallet(self) -> Optional[Dict[str, Any]]:
        """
        Load wallet data from file.
        Returns:
            Dict containing wallet data if successful, None otherwise
        """
        try:
            if os.path.exists(self.wallet_file):
                with open(self.wallet_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading wallet data: {str(e)}")
            return None

    async def fund_wallet(self, wallet: Wallet, asset_id: Optional[str] = None) -> Transaction:
        """Fund wallet from faucet"""
        try:
            if asset_id:
                tx = wallet.faucet(asset_id=asset_id)
            else:
                tx = wallet.faucet()
            logger.info(f"Faucet transaction sent for {asset_id or 'ETH'}")
            await self._wait_for_confirmation(tx)
            return tx
        except Exception as e:
            raise InsufficientFundsError(f"Failed to fund wallet: {str(e)}")

    async def _wait_for_confirmation(self, tx: Transaction, timeout: int = 30) -> None:
        """Wait for transaction confirmation with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if tx.is_confirmed():
                return
            await time.sleep(2)
        raise ToolError("Transaction confirmation timeout")

class TransactionManager:
    """Class to manage cryptocurrency transactions"""
    
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager

    async def send_gasless_usdc_transaction(
        self,
        to_address: str,
        amount: str
    ) -> Tuple[Dict[str, Any], str]:
        """Send a gasless USDC transaction"""
        try:
            # Ensure client is configured
            self.wallet_manager.get_cdp_client()
            logger.info("CDP client configured")

            # Create and fund wallet
            wallet = await self.wallet_manager.load_wallet()
            
            # Execute transfer
            tx = wallet.default_address.transfer(
                amount=amount,
                token="usdc",
                to_address=to_address,
                gasless=True
            ).wait()
            
            logger.info(f"USDC Transfer completed: {tx.hash}")
            
            result = {
                'success': True,
                'tx_hash': tx.hash,
                'from': str(wallet.default_address),
                'to': to_address,
                'amount': amount,
                'token': 'USDC',
                'timestamp': datetime.now().isoformat()
            }
            
            await self.wallet_manager.save_wallet({
                'address': str(wallet.default_address),
                'last_transaction': result
            })
            
            return result, "gasless_usdc_transfer"

        except InsufficientFundsError as e:
            raise
        except Exception as e:
            logger.error(f"Error in gasless USDC transfer: {str(e)}")
            raise ToolError(f"Failed to send USDC: {str(e)}")

    async def send_eth_transaction(
        self,
        to_address: str,
        amount: str
    ) -> Tuple[Dict[str, Any], str]:
        """Send an ETH transaction"""
        try:
            # Ensure client is configured
            self.wallet_manager.get_cdp_client()
            logger.info("CDP client configured")

            # Load wallet
            wallet = await self.wallet_manager.load_wallet()
            
            # Execute transfer
            tx = wallet.transfer(
                amount=amount,
                token="eth",
                to_address=to_address
            ).wait()
            
            logger.info(f"ETH Transfer completed: {tx.hash}")
            
            result = {
                'success': True,
                'tx_hash': tx.hash,
                'from': str(wallet.default_address),
                'to': to_address,
                'amount': amount,
                'token': 'ETH',
                'timestamp': datetime.now().isoformat()
            }
            
            await self.wallet_manager.save_wallet({
                'address': str(wallet.default_address),
                'last_transaction': result
            })
            
            return result, "eth_transfer"

        except InsufficientFundsError as e:
            raise
        except Exception as e:
            logger.error(f"Error in ETH transfer: {str(e)}")
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
        },
        {
            "type": "function",
            "function": {
                "name": "initialize_cdp_wallet",
                "description": "Initialize CDP wallet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cdp_api_key": {
                            "type": "string",
                            "description": "CDP API key"
                        },
                        "cdp_api_secret": {
                            "type": "string",
                            "description": "CDP API secret"
                        }
                    },
                    "required": ["cdp_api_key", "cdp_api_secret"]
                }
            }
        }   
    ]
