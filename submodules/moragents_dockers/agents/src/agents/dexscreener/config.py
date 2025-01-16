class Config:
    """Configuration for DexScreener Token API."""

    BASE_URL = "https://api.dexscreener.com"
    RATE_LIMIT = 60  # requests per minute

    ENDPOINTS = {
        "token_profiles": "/token-profiles/latest/v1",
        "latest_boosts": "/token-boosts/latest/v1",
        "top_boosts": "/token-boosts/top/v1",
        "dex_search": "/latest/dex/search",
    }

    tools = [
        {
            "name": "get_latest_token_profiles",
            "description": "Get the latest token profiles from DexScreener",
            "parameters": {
                "type": "object",
                "properties": {
                    "chain_id": {
                        "type": "string",
                        "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
                        "required": False,
                    }
                },
            },
        },
        {
            "name": "get_latest_boosted_tokens",
            "description": "Get the latest boosted tokens from DexScreener",
            "parameters": {
                "type": "object",
                "properties": {
                    "chain_id": {
                        "type": "string",
                        "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
                        "required": False,
                    }
                },
            },
        },
        {
            "name": "get_top_boosted_tokens",
            "description": "Get the tokens with most active boosts",
            "parameters": {
                "type": "object",
                "properties": {
                    "chain_id": {
                        "type": "string",
                        "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
                        "required": False,
                    }
                },
            },
        },
        {
            "name": "search_dex_pairs",
            "description": "Search for DEX trading pairs and their activity",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., token symbol like 'ETH' or 'BTC')",
                        "required": True,
                    }
                },
            },
        },
    ]
