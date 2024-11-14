import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:

    # API endpoints
    INCH_URL = "https://api.1inch.dev/token"
    QUOTE_URL = "https://api.1inch.dev/swap"
    APIBASEURL = f"https://api.1inch.dev/swap/v6.0/"
    WEB3RPCURL = {
        "56": "https://bsc-dataseed.binance.org",
        "42161": "https://arb1.arbitrum.io/rpc",
        "137": "https://polygon-rpc.com",
        "1": "https://eth.llamarpc.com/",
        "10": "https://mainnet.optimism.io",
        "8453": "https://mainnet.base.org",
    }
    NATIVE_TOKENS = {
        "137": "MATIC",
        "56": "BNB",
        "1": "ETH",
        "42161": "ETH",
        "10": "ETH",
        "8453": "ETH",
    }
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
    ]
    INCH_NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    _instance = None
    _inch_api_key = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def inch_api_key(self):
        return self._inch_api_key

    @inch_api_key.setter
    def inch_api_key(self, value):
        self._inch_api_key = value
