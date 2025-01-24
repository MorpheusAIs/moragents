from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Crypto Data Agent."""

    # *************
    # AGENT CONFIG
    # *************

    agent_config = AgentConfig(
        path="src.agents.crypto_data.agent",
        class_name="CryptoDataAgent",
        description="Fetches cryptocurrency price and market data from various sources.",
        human_readable_name="Crypto Data Analyst",
        command="cryptodata",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "get_price",
            "description": "Get current price of a cryptocurrency",
            "parameters": {
                "type": "object",
                "properties": {
                    "coin_name": {"type": "string", "description": "Name of the cryptocurrency"},
                },
                "required": ["coin_name"],
            },
        },
        {
            "name": "get_floor_price",
            "description": "Get NFT collection floor price",
            "parameters": {
                "type": "object",
                "properties": {
                    "nft_name": {"type": "string", "description": "Name of the NFT collection"},
                },
                "required": ["nft_name"],
            },
        },
        {
            "name": "get_tvl",
            "description": "Get total value locked (TVL) of a protocol",
            "parameters": {
                "type": "object",
                "properties": {
                    "protocol_name": {"type": "string", "description": "Name of the protocol"},
                },
                "required": ["protocol_name"],
            },
        },
    ]

    # *************
    # API CONFIG
    # *************

    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    DEFILLAMA_BASE_URL = "https://api.llama.fi"

    # Response messages
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
