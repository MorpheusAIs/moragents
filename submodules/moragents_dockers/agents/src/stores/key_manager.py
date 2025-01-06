import logging
from typing import Dict, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)  # Fixed name reference


class Service(Enum):
    """Supported API service types"""

    X = "x"
    COINBASE = "coinbase"
    ONEINCH = "oneinch"


class BaseKeys:
    """
    Base class for API keys to ensure proper initialization.

    This class serves as a parent class for specific API key implementations,
    providing a consistent interface for key management.
    """

    def __init__(self):
        pass


class XKeys(BaseKeys):
    """
    Container for X (formerly Twitter) API authentication credentials.

    Stores and manages the various keys and tokens required for X API access:
    - API key and secret for application authentication
    - Access token and secret for user authentication
    - Bearer token for application-only authentication
    """

    def __init__(self):
        super().__init__()
        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.access_token: Optional[str] = None
        self.access_token_secret: Optional[str] = None
        self.bearer_token: Optional[str] = None

    def is_complete(self) -> bool:
        """
        Check if all required X API credentials are set.

        Returns:
            bool: True if all required keys are present, False otherwise
        """
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
    """
    Container for Coinbase API authentication credentials.

    Stores and manages the CDP API key and secret required for Coinbase API access.
    CDP (Coinbase Developer Platform) credentials are used for accessing Coinbase's
    trading and account management features.
    """

    def __init__(self):
        super().__init__()
        self.cdp_api_key: Optional[str] = None
        self.cdp_api_secret: Optional[str] = None

    def is_complete(self) -> bool:
        """
        Check if all required Coinbase API credentials are set.

        Returns:
            bool: True if both CDP API key and secret are present, False otherwise
        """
        return all([self.cdp_api_key, self.cdp_api_secret])


class OneInchKeys(BaseKeys):
    """
    Container for 1inch API authentication credentials.

    Stores and manages the API key required for 1inch API access.
    """

    def __init__(self):
        super().__init__()
        self.api_key: Optional[str] = None

    def is_complete(self) -> bool:
        """
        Check if the required 1inch API key is set.

        Returns:
            bool: True if the API key is present, False otherwise
        """
        return bool(self.api_key)


KeysType = Union[XKeys, CoinbaseKeys, OneInchKeys]


class KeyManager:
    """
    Manages API keys and authentication credentials for multiple services.

    This class provides a centralized way to store, retrieve, and manage API keys
    for different services (X and Coinbase). It implements a singleton pattern
    to ensure consistent key management across the application.

    Features:
    - Secure storage of API keys and tokens
    - Service-specific key validation
    - Key presence checking
    - Key clearing functionality

    Attributes:
        keys (Dict[Service, KeysType]): Dictionary mapping services to their respective key containers

    Example:
        >>> manager = KeyManager()
        >>> manager.set_x_keys(api_key="key", api_secret="secret", ...)
        >>> if manager.has_x_keys():
        >>>     x_keys = manager.get_x_keys()
    """

    def __init__(self):
        self.keys: Dict[Service, KeysType] = {
            Service.X: XKeys(),
            Service.COINBASE: CoinbaseKeys(),
            Service.ONEINCH: OneInchKeys(),
        }

    def set_x_keys(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: str,
    ) -> None:
        """
        Set all X API keys.

        Args:
            api_key (str): Application API key
            api_secret (str): Application API secret
            access_token (str): User access token
            access_token_secret (str): User access token secret
            bearer_token (str): Application-only authentication token
        """
        x_keys = XKeys()
        x_keys.api_key = api_key
        x_keys.api_secret = api_secret
        x_keys.access_token = access_token
        x_keys.access_token_secret = access_token_secret
        x_keys.bearer_token = bearer_token
        self.keys[Service.X] = x_keys
        logger.info("Updated X API keys")

    def set_coinbase_keys(self, cdp_api_key: str, cdp_api_secret: str) -> None:
        """
        Set Coinbase API keys.

        Args:
            cdp_api_key (str): Coinbase Developer Platform API key
            cdp_api_secret (str): Coinbase Developer Platform API secret
        """
        coinbase_keys = CoinbaseKeys()
        coinbase_keys.cdp_api_key = cdp_api_key
        # Handle newline replacement when setting the key
        coinbase_keys.cdp_api_secret = cdp_api_secret.replace("\\n", "\n") if cdp_api_secret else None
        self.keys[Service.COINBASE] = coinbase_keys
        logger.info("Updated Coinbase API keys")

    def set_oneinch_keys(self, api_key: str) -> None:
        """
        Set 1inch API key.

        Args:
            api_key (str): 1inch API key
        """
        oneinch_keys = OneInchKeys()
        oneinch_keys.api_key = api_key
        self.keys[Service.ONEINCH] = oneinch_keys
        logger.info("Updated 1inch API key")

    def get_x_keys(self) -> XKeys:
        """
        Get X API keys.

        Returns:
            XKeys: Container with X API credentials
        """
        keys = self.keys[Service.X]
        assert isinstance(keys, XKeys)
        return keys

    def get_coinbase_keys(self) -> CoinbaseKeys:
        """
        Get Coinbase API keys.

        Returns:
            CoinbaseKeys: Container with Coinbase API credentials
        """
        keys = self.keys[Service.COINBASE]
        assert isinstance(keys, CoinbaseKeys)
        return keys

    def get_oneinch_keys(self) -> OneInchKeys:
        """
        Get 1inch API key.

        Returns:
            OneInchKeys: Container with 1inch API credentials
        """
        keys = self.keys[Service.ONEINCH]
        assert isinstance(keys, OneInchKeys)
        return keys

    def has_x_keys(self) -> bool:
        """
        Check if all required X keys are set.

        Returns:
            bool: True if all required X API credentials are present and valid
        """
        return isinstance(self.keys[Service.X], XKeys) and self.keys[Service.X].is_complete()

    def has_coinbase_keys(self) -> bool:
        """
        Check if all required Coinbase keys are set.

        Returns:
            bool: True if all required Coinbase API credentials are present and valid
        """
        return isinstance(self.keys[Service.COINBASE], CoinbaseKeys) and self.keys[Service.COINBASE].is_complete()

    def has_oneinch_keys(self) -> bool:
        """
        Check if 1inch API key is set.

        Returns:
            bool: True if 1inch API key is present and valid
        """
        return isinstance(self.keys[Service.ONEINCH], OneInchKeys) and self.keys[Service.ONEINCH].is_complete()

    def clear_keys(self, service: Optional[Service] = None) -> None:
        """
        Clear keys for specified service or all if none specified.

        Args:
            service (Optional[Service]): Specific service to clear keys for.
                                       If None, clears all services' keys.
        """
        if service == Service.X or service is None:
            self.keys[Service.X] = XKeys()
            logger.info("Cleared X API keys")

        if service == Service.COINBASE or service is None:
            self.keys[Service.COINBASE] = CoinbaseKeys()
            logger.info("Cleared Coinbase API keys")

        if service == Service.ONEINCH or service is None:
            self.keys[Service.ONEINCH] = OneInchKeys()
            logger.info("Cleared 1inch API key")

    def has_any_keys(self) -> bool:
        """
        Check if any API keys are stored.

        Returns:
            bool: True if any service has valid API credentials set
        """
        return any([self.has_x_keys(), self.has_coinbase_keys(), self.has_oneinch_keys()])


# Create an instance to act as a singleton store
key_manager_instance = KeyManager()
