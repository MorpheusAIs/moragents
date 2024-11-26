import json
import logging
from typing import Dict, Optional
from cdp import Wallet
from pathlib import Path

logger = logging.getLogger(__name__)


class WalletManager:
    def __init__(self):
        """Initialize the WalletManager"""
        self.wallets: Dict[str, Wallet] = {}
        self.wallet_data: Dict[str, dict] = {}

    def create_wallet(self, wallet_id: str, network_id: Optional[str] = None) -> Wallet:
        """Create a new CDP wallet and store it"""
        try:
            wallet = Wallet.create(network_id=network_id)
            self.wallets[wallet_id] = wallet

            # Export and store wallet data
            wallet_data = wallet.export_data()
            self.wallet_data[wallet_id] = wallet_data.to_dict()

            logger.info(f"Created new wallet with ID: {wallet_id}")
            return wallet

        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            raise

    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """Get a wallet by ID"""
        return self.wallets.get(wallet_id)

    def save_wallet(self, wallet_id: str, filepath: str) -> bool:
        """Save wallet data to file"""
        try:
            if wallet_id not in self.wallet_data:
                logger.error(f"No wallet data found for ID: {wallet_id}")
                return False

            # Create directory if it doesn't exist
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w") as f:
                json.dump(self.wallet_data[wallet_id], f)

            logger.info(f"Saved wallet {wallet_id} to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save wallet: {str(e)}")
            return False

    def load_wallet(self, wallet_id: str, filepath: str) -> Optional[Wallet]:
        """Load wallet from saved data"""
        try:
            with open(filepath, "r") as f:
                wallet_data = json.load(f)

            # Import wallet from data
            wallet = Wallet.import_data(wallet_data)

            # Store in memory
            self.wallets[wallet_id] = wallet
            self.wallet_data[wallet_id] = wallet_data

            logger.info(f"Loaded wallet {wallet_id} from {filepath}")
            return wallet

        except Exception as e:
            logger.error(f"Failed to load wallet: {str(e)}")
            return None

    def remove_wallet(self, wallet_id: str):
        """Remove a wallet from memory"""
        if wallet_id in self.wallets:
            del self.wallets[wallet_id]
        if wallet_id in self.wallet_data:
            del self.wallet_data[wallet_id]
        logger.info(f"Removed wallet {wallet_id}")

    def has_wallet(self, wallet_id: str) -> bool:
        """Check if wallet exists"""
        return wallet_id in self.wallets

    def list_wallets(self) -> list[dict]:
        """Get list of wallets with their data"""
        return [
            {"wallet_id": wallet_id, "network_id": wallet.network_id}
            for wallet_id, wallet in self.wallets.items()
        ]

    def export_wallet(self, wallet_id: str) -> Optional[dict]:
        """Export wallet data to dictionary format"""
        try:
            if not self.has_wallet(wallet_id):
                logger.error(f"Wallet {wallet_id} not found")
                return None

            wallet = self.wallets[wallet_id]
            wallet_data = wallet.export_data()

            logger.info(f"Exported wallet {wallet_id}")
            return wallet_data.to_dict()

        except Exception as e:
            logger.error(f"Failed to export wallet: {str(e)}")
            return None
