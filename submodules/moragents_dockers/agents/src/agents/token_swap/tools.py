import requests
import logging
import time
from web3 import Web3

from src.agents.token_swap.config import Config
logger = logging.getLogger(__name__)



class InsufficientFundsError(Exception):
    pass


class TokenNotFoundError(Exception):
    pass


class SwapNotPossibleError(Exception):
    pass


def get_headers(api_key: str | None = None) -> dict[str, str]:
    """Get headers for 1inch API requests with optional API key override"""
    config = Config.get_instance()
    headers = {
        "Authorization": f"Bearer {api_key or config.inch_api_key or ''}",
        "accept": "application/json",
    }
    return headers


def search_tokens(
    query: str, 
    chain_id: int, 
    limit: int = 1, 
    ignore_listed: str = "false", 
    inch_api_key: str | None = None
) -> dict | None:
    logger.info(f"Searching tokens - Query: {query}, Chain ID: {chain_id}")
    endpoint = f"/v1.2/{chain_id}/search"
    params = {"query": query, "limit": limit, "ignore_listed": ignore_listed}
    
    response = requests.get(
        Config.INCH_URL + endpoint,
        params=params,
        headers=get_headers(inch_api_key)
    )
    logger.info(f"Search tokens response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Found tokens: {result}")
        return result
    else:
        logger.error(f"Failed to search tokens. Status code: {response.status_code}, Response: {response.text}")
        return None


def get_token_balance(
    web3: Web3, wallet_address: str, token_address: str, abi: list
) -> int:
    """Get the balance of an ERC-20 token for a given wallet address."""
    if (
        not token_address
    ):  # If no token address is provided, assume checking ETH or native token balance
        return web3.eth.get_balance(web3.to_checksum_address(wallet_address))
    else:
        contract = web3.eth.contract(
            address=web3.to_checksum_address(token_address), abi=abi
        )
        return contract.functions.balanceOf(
            web3.to_checksum_address(wallet_address)
        ).call()


def eth_to_wei(amount_in_eth: float) -> int:
    """Convert an amount in ETH to wei."""
    return int(amount_in_eth * 10**18)


def validate_swap(web3: Web3, token1, token2, chain_id, amount, wallet_address):
    native = Config.NATIVE_TOKENS

    #  token1 is the native token
    if token1.lower() == native[str(chain_id)].lower():
        t1 = [
            {
                "symbol": native[str(chain_id)],
                "address": Config.INCH_NATIVE_TOKEN_ADDRESS,
            }
        ]
        t1_bal = get_token_balance(web3, wallet_address, "", Config.ERC20_ABI)
        smallest_amount = eth_to_wei(amount)

    #  token1 is an erc20 token
    else:
        t1 = search_tokens(token1, chain_id)
        time.sleep(2)
        if not t1:
            raise TokenNotFoundError(f"Token {token1} not found.")
        t1_bal = get_token_balance(
            web3, wallet_address, t1[0]["address"], Config.ERC20_ABI
        )
        smallest_amount = convert_to_smallest_unit(web3, amount, t1[0]["address"])

    # Check if token2 is the native token
    if token2.lower() == native[str(chain_id)].lower():
        t2 = [
            {
                "symbol": native[str(chain_id)],
                "address": Config.INCH_NATIVE_TOKEN_ADDRESS,
            }
        ]
    else:
        t2 = search_tokens(token2, chain_id)
        time.sleep(2)
        if not t2:
            raise TokenNotFoundError(f"Token {token2} not found.")

    # Check if the user has sufficient balance for the swap
    if t1_bal < smallest_amount:
        raise InsufficientFundsError(f"Insufficient funds to perform the swap.")

    return t1[0]["address"], t1[0]["symbol"], t2[0]["address"], t2[0]["symbol"]


def get_quote(token1, token2, amount_in_wei, chain_id, inch_api_key=None):
    logger.info(f"Getting quote - Token1: {token1}, Token2: {token2}, Amount: {amount_in_wei}, Chain ID: {chain_id}")
    endpoint = f"/v6.0/{chain_id}/quote"
    params = {"src": token1, "dst": token2, "amount": int(amount_in_wei)}
    logger.debug(f"Quote request - URL: {Config.QUOTE_URL + endpoint}, Params: {params}")
    
    response = requests.get(
        Config.QUOTE_URL + endpoint,
        params=params,
        headers=get_headers(inch_api_key)
    )
    logger.info(f"Quote response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Quote received: {result}")
        return result
    else:
        logger.error(f"Failed to get quote. Status code: {response.status_code}, Response: {response.text}")
        return None


def get_token_decimals(web3: Web3, token_address: str) -> int:
    if not token_address:
        return 18  # Assuming 18 decimals for the native gas token
    else:
        contract = web3.eth.contract(
            address=Web3.to_checksum_address(token_address), abi=Config.ERC20_ABI
        )
        return contract.functions.decimals().call()


def convert_to_smallest_unit(web3: Web3, amount: float, token_address: str) -> int:
    decimals = get_token_decimals(web3, token_address)
    return int(amount * (10**decimals))


def convert_to_readable_unit(
    web3: Web3, smallest_unit_amount: int, token_address: str
) -> float:
    decimals = get_token_decimals(web3, token_address)
    return smallest_unit_amount / (10**decimals)


def swap_coins(token1: str, token2: str, amount: str | float, chain_id: int, wallet_address: str) -> tuple[str, str]:
    """Swap two tokens"""
    logger.info(f"Attempting swap: {token1} -> {token2}, amount: {amount}")
    
    # Validate amount first
    if not amount or (isinstance(amount, str) and not amount.strip()):
        return {
            "error": "Please specify the amount you want to swap"
        }, "assistant"
        
    try:
        amount = float(amount)
    except ValueError:
        return {
            "error": f"Invalid amount format: {amount}. Please provide a valid number."
        }, "assistant"

    if amount <= 0:
        return {
            "error": "Amount must be greater than 0"
        }, "assistant"

    # Normalize token symbols
    token1 = token1.strip().upper()
    token2 = token2.strip().upper()
    
    web3 = Web3(Web3.HTTPProvider(Config.WEB3RPCURL[str(chain_id)]))
    t1_a, t1_id, t2_a, t2_id = validate_swap(
        web3, token1, token2, chain_id, amount, wallet_address
    )

    time.sleep(2)
    t1_address = "" if t1_a == Config.INCH_NATIVE_TOKEN_ADDRESS else t1_a
    smallest_unit_amount = convert_to_smallest_unit(web3, amount, t1_address)
    result = get_quote(t1_a, t2_a, smallest_unit_amount, chain_id)

    if result:
        price = result["dstAmount"]
        t2_address = "" if t2_a == Config.INCH_NATIVE_TOKEN_ADDRESS else t2_a
        t2_quote = convert_to_readable_unit(web3, int(price), t2_address)
    else:
        raise SwapNotPossibleError(
            "Failed to generate a quote. Please ensure you're on the correct network."
        )

    return {
        "dst": t2_id,
        "dst_address": t2_a,
        "dst_amount": float(t2_quote),
        "src": t1_id,
        "src_address": t1_a,
        "src_amount": amount,
        "approve_tx_cb": "/approve",
        "swap_tx_cb": "/swap",
    }, "swap"


def get_tools():
    """Return a list of tools for the agent."""
    return [
        {
            "type": "function",
            "function": {
                "name": "swap_agent",
                "description": "swap two cryptocurrencies",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token1": {
                            "type": "string",
                            "description": "name or address of the cryptocurrency to sell",
                        },
                        "token2": {
                            "type": "string",
                            "description": "name or address of the cryptocurrency to buy",
                        },
                        "value": {
                            "type": "string",
                            "description": "Value or amount of the cryptocurrency to sell",
                        },
                    },
                    "required": ["token1", "token2", "value"],
                },
            },
        }
    ]
