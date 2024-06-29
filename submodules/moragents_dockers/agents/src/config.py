import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Configuration object
class Config:
    # Model configuration
    MODEL_NAME = "meetkai/functionary-small-v2.4-GGUF"
    MODEL_REVISION = "functionary-small-v2.4.Q4_0.gguf"
    MODEL_PATH = "model/"+MODEL_REVISION
    DOWNLOAD_DIR = "model"
    # API endpoints
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    DEFILLAMA_BASE_URL = "https://api.llama.fi"
    PRICE_SUCCESS_MESSAGE = "The price of {coin_name} is ${price:,}"
    PRICE_FAILURE_MESSAGE = "Failed to retrieve price. Please enter a valid coin name."
    FLOOR_PRICE_SUCCESS_MESSAGE = "The floor price of {nft_name} is ${floor_price:,}"
    FLOOR_PRICE_FAILURE_MESSAGE = "Failed to retrieve floor price. Please enter a valid NFT name."
    TVL_SUCCESS_MESSAGE = "The TVL of {protocol_name} is ${tvl:,}"
    TVL_FAILURE_MESSAGE = "Failed to retrieve TVL. Please enter a valid protocol name."
    FDV_SUCCESS_MESSAGE = "The fully diluted valuation of {coin_name} is ${fdv:,}"
    FDV_FAILURE_MESSAGE = "Failed to retrieve FDV. Please enter a valid coin name."
    MARKET_CAP_SUCCESS_MESSAGE = "The market cap of {coin_name} is ${market_cap:,}"
    MARKET_CAP_FAILURE_MESSAGE = "Failed to retrieve market cap. Please enter a valid coin name."
    API_ERROR_MESSAGE = "I can't seem to access the API at the moment."
    INCH_URL = "https://api.1inch.dev/token"
    QUOTE_URL = "https://api.1inch.dev/swap"
    APIBASEURL = f"https://api.1inch.dev/swap/v6.0/"
    HEADERS = { "Authorization": "Bearer WvQuxaMYpPvDiiOL5RHWUm7OzOd20nt4", "accept": "application/json" }
    WEB3RPCURL = {"56":"https://bsc-dataseed.binance.org","42161":"https://arb1.arbitrum.io/rpc","137":"https://polygon-rpc.com","1":"https://cloudflare-eth.com","10":"https://mainnet.optimism.io","8453":"https://mainnet.base.org"}
    NATIVE_TOKENS={"137":"MATIC","56":"BNB","1":"ETH","42161":"ETH","10":"ETH","8453":"ETH"}
    ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": False, "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}
    ]
    INCH_NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"