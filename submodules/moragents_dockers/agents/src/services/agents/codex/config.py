from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Codex.io API."""

    # *************
    # AGENT CONFIG
    # ------------
    # This must be defined in every agent config file
    # It is required to load the agent
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.codex.agent",
        class_name="CodexAgent",
        description="Fetches and analyzes token and NFT data from Codex.io.",
        human_readable_name="Codex Market Analyst",
        command="codex",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "list_top_tokens",
            "description": "Get a list of trending tokens across specified networks",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tokens to return (max 50)",
                        "required": False,
                    },
                    "networkFilter": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of network IDs to filter by",
                        "required": False,
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Time frame for trending results (1, 5, 15, 30, 60, 240, 720, or 1D)",
                        "required": False,
                    },
                },
            },
        },
        {
            "name": "get_top_holders_percent",
            "description": "Get the top holders for a token",
            "parameters": {
                "type": "object",
                "properties": {
                    "tokenId": {
                        "type": "string",
                        "description": "Token ID",
                        "required": True,
                    },
                },
            },
        },
        {
            "name": "search_nfts",
            "description": "Search for NFT collections by name or address",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Query string to search for",
                        "required": True,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "required": False,
                    },
                    "networkFilter": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of network IDs to filter by",
                        "required": False,
                    },
                    "filterWashTrading": {
                        "type": "boolean",
                        "description": "Whether to filter collections linked to wash trading",
                        "required": False,
                    },
                    "window": {
                        "type": "string",
                        "description": "Time frame for stats (1h, 4h, 12h, or 1d)",
                        "required": False,
                    },
                },
            },
        },
    ]

    # *************
    # API CONFIG
    # *************

    GRAPHQL_URL = "https://graph.codex.io/graphql"
