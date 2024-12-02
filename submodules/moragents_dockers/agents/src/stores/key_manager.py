import logging
from typing import Dict, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)  # Fixed name reference


class Service(Enum):
    X = "x"
    COINBASE = "coinbase"


class BaseKeys:
    """Base class for API keys to ensure proper initialization"""

    def __init__(self):
        pass


class XKeys(BaseKeys):
    def __init__(self):
        super().__init__()
        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.access_token: Optional[str] = None
        self.access_token_secret: Optional[str] = None
        self.bearer_token: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if all required keys are set"""
        return all(
            [
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret,
                self.bearer_token,
            ]
        )


class CoinbaseKeys(BaseKeys):
    def __init__(self):
        super().__init__()
        self.cdp_api_key: Optional[str] = None
        self.cdp_api_secret: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if all required keys are set"""
        return all([self.cdp_api_key, self.cdp_api_secret])


KeysType = Union[XKeys, CoinbaseKeys]


class KeyManager:
    def __init__(self):
        self.keys: Dict[Service, KeysType] = {
            Service.X: XKeys(),
            Service.COINBASE: CoinbaseKeys(),
        }

    def set_x_keys(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: str,
    ) -> None:
        """Set all X API keys"""
        x_keys = XKeys()
        x_keys.api_key = api_key
        x_keys.api_secret = api_secret
        x_keys.access_token = access_token
        x_keys.access_token_secret = access_token_secret
        x_keys.bearer_token = bearer_token
        self.keys[Service.X] = x_keys
        logger.info("Updated X API keys")

    def set_coinbase_keys(self, cdp_api_key: str, cdp_api_secret: str) -> None:
        """Set Coinbase API keys"""
        coinbase_keys = CoinbaseKeys()
        coinbase_keys.cdp_api_key = cdp_api_key
        # Handle newline replacement when setting the key
        coinbase_keys.cdp_api_secret = (
            cdp_api_secret.replace("\\n", "\n") if cdp_api_secret else None
        )
        self.keys[Service.COINBASE] = coinbase_keys
        logger.info("Updated Coinbase API keys")

    def get_x_keys(self) -> XKeys:
        """Get X API keys"""
        keys = self.keys[Service.X]
        assert isinstance(keys, XKeys)
        return keys

    def get_coinbase_keys(self) -> CoinbaseKeys:
        """Get Coinbase API keys"""
        keys = self.keys[Service.COINBASE]
        assert isinstance(keys, CoinbaseKeys)
        return keys

    def has_x_keys(self) -> bool:
        """Check if all required X keys are set"""
        return isinstance(self.keys[Service.X], XKeys) and self.keys[Service.X].is_complete()

    def has_coinbase_keys(self) -> bool:
        """Check if all required Coinbase keys are set"""
        return (
            isinstance(self.keys[Service.COINBASE], CoinbaseKeys)
            and self.keys[Service.COINBASE].is_complete()
        )

    def clear_keys(self, service: Optional[Service] = None) -> None:
        """Clear keys for specified service or all if none specified"""
        if service == Service.X or service is None:
            self.keys[Service.X] = XKeys()
            logger.info("Cleared X API keys")

        if service == Service.COINBASE or service is None:
            self.keys[Service.COINBASE] = CoinbaseKeys()
            logger.info("Cleared Coinbase API keys")

    def has_any_keys(self) -> bool:
        """Check if any API keys are stored"""
        return any([self.has_x_keys(), self.has_coinbase_keys()])


# Create an instance to act as a singleton store
key_manager_instance = KeyManager()
