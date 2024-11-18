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

    # Initialize CDP client
    Cdp.configure('', '')

    def create_wallet(self) -> Wallet:
        """Create a new wallet"""
        try:
            wallet = Wallet.create("base-sepolia")
            print(f"Wallet successfully created: {wallet}")

            tx = self.fund_wallet(wallet, "usdc")
            logger.info(f"Funding transaction initiated: {tx}")

            # Save after funding is initiated
            success = self._save_wallet_data(wallet)
            if not success:
                logger.warning("Failed to save wallet data")

            logger.info(f"Wallet created: {wallet.default_address}")
            return wallet
        except Exception as e:
            raise ToolError(f"Failed to create wallet: {str(e)}")

    def _save_wallet_data(self, wallet: Wallet) -> bool:
        """
        Save both wallet data and seed
        """
        try:
            # Convert WalletAddress to string representation
            wallet_data = {
                'wallet_id': wallet.id,
                'address': str(wallet.default_address),
                'network': wallet.network_id,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.wallet_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            
            wallet.save_seed(self.seed_file, encrypt=True)
            
            logger.info(f"Wallet data and seed saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving wallet data: {str(e)}")
            return False

    def load_wallet(self) -> Wallet:
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

    def fund_wallet(self, wallet: Wallet, asset_id: Optional[str] = None) -> Transaction:
        """Fund Base Agent wallet from faucet"""
        try:
            if asset_id:
                tx = wallet.faucet(asset_id=asset_id)
            else:
                tx = wallet.faucet()
            logger.info(f"Faucet transaction sent for {asset_id or 'ETH'}")
            return tx
        except Exception as e:
            raise InsufficientFundsError(f"Failed to fund wallet: {str(e)}")

    def get_wallet_info(self, wallet: Wallet) -> Dict[str, Any]:
        """Get wallet information in a serializable format"""
        try:
            return {
                'wallet_id': wallet.id,
                'address': str(wallet.default_address),
                'network': wallet.network_id,
                'eth_balance': wallet.get_balance("eth"),
                'usdc_balance': wallet.get_balance("usdc")
            }
        except Exception as e:
            logger.error(f"Error getting wallet info: {str(e)}")
            return None