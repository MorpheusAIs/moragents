from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Token Swap Agent."""

    # *************
    # AGENT CONFIG
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.token_swap.agent",
        class_name="TokenSwapAgent",
        description="Handles token swaps across multiple networks",
        human_readable_name="Token Swap Manager",
        command="swap",
        upload_required=False,
    )

    # *************
    # API CONFIG
    # *************

    INCH_URL = "https://api.1inch.dev/token"
    QUOTE_URL = "https://api.1inch.dev/swap"
    APIBASEURL = f"https://api.1inch.dev/swap/v6.0/"
    HEADERS = {
        "Authorization": "Bearer WvQuxaMYpPvDiiOL5RHWUm7OzOd20nt4",
        "accept": "application/json",
    }

    # *************
    # NETWORK CONFIG
    # *************

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

    # *************
    # CONTRACT CONFIG
    # *************

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
