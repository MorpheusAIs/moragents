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

class CDPWalletManager:
    """Class to manage Base Agent wallet operations and persistence"""
    
    def __init__(self, wallet_file: str = "wallet_data.json"):
        self.wallet_file = wallet_file
        self.seed_file = "wallet_seed.json"

    async def create_wallet(self) -> Wallet:
        """Create a new wallet"""
        try:
            wallet = Wallet.create("base-mainnet")
            await self._save_wallet_data(wallet)
            logger.info(f"Wallet created: {wallet.default_address}")
            return wallet
        except Exception as e:
            raise ToolError(f"Failed to create wallet: {str(e)}")

    async def _save_wallet_data(self, wallet: Wallet) -> bool:
        """
        Save both wallet data and seed
        """
        try:
            wallet_data = wallet.export_data().to_dict()
            with open(self.wallet_file, 'w') as f:
                json.dump({
                    'wallet_id': wallet.id,
                    'address': wallet.default_address,
                    'data': wallet_data
                }, f, indent=2)
            
            wallet.save_seed(self.seed_file, encrypt=True)
            
            logger.info(f"Wallet data and seed saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving wallet data: {str(e)}")
            return False

    async def load_wallet(self) -> Wallet:
        """
        Load and re-instantiate wallet from saved data
        """
        try:
            if not os.path.exists(self.wallet_file) or not os.path.exists(self.seed_file):
                logger.info("No existing wallet data found")
                return None

            with open(self.wallet_file, 'r') as f:
                stored_data = json.load(f)

            wallet = Wallet.fetch(stored_data['wallet_id'])
            wallet.load_seed(self.seed_file)
            
            logger.info(f"Wallet loaded successfully: {wallet.default_address}")
            return wallet
        except Exception as e:
            logger.error(f"Error loading wallet: {str(e)}")
            return None

    async def fund_wallet(self, wallet: Wallet, asset_id: Optional[str] = None) -> Transaction:
        """Fund Base Agent wallet from faucet"""
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