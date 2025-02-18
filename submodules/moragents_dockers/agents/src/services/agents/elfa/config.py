from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Elfa Social API."""

    # *************
    # AGENT CONFIG
    # ------------
    # This must be defined in every agent config file
    # It is required to load the agent
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.elfa.agent",
        class_name="ElfaAgent",
        description="Fetches and analyzes social media data related to cryptocurrency from Elfa.",
        human_readable_name="Elfa Social Analyst",
        command="elfa",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "get_mentions",
            "description": "Get tweets by smart accounts with at least 10 other smart interactions",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of mentions to return (default: 100)",
                        "required": False,
                    },
                    "offset": {
                        "type": "number",
                        "description": "Offset for pagination (default: 0)",
                        "required": False,
                    },
                },
            },
        },
        {
            "name": "get_top_mentions",
            "description": "Get top mentions for a specific ticker, ranked by view count",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The ticker symbol to get mentions for",
                        "required": True,
                    },
                    "timeWindow": {
                        "type": "string",
                        "description": "Time window for mentions (e.g., '1h', '24h', '7d')",
                        "required": False,
                    },
                    "includeAccountDetails": {
                        "type": "boolean",
                        "description": "Include account details in response",
                        "required": False,
                    },
                },
            },
        },
        {
            "name": "search_mentions",
            "description": "Search for mentions by keywords within a time range",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search for (max 5). Defaults to ['crypto']",
                        "required": False,
                    },
                    "from": {
                        "type": "number",
                        "description": "Start timestamp (unix). Defaults to 7 days ago",
                        "required": False,
                    },
                    "to": {
                        "type": "number",
                        "description": "End timestamp (unix). Defaults to now",
                        "required": False,
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of results to return (default: 20, max: 30)",
                        "required": False,
                    },
                    "cursor": {
                        "type": "string",
                        "description": "Cursor for pagination",
                        "required": False,
                    },
                },
            },
        },
        {
            "name": "get_trending_tokens",
            "description": "Get trending tokens based on social media mentions",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeWindow": {
                        "type": "string",
                        "description": "Time window for trending analysis (default: '24h')",
                        "required": False,
                    },
                    "minMentions": {
                        "type": "number",
                        "description": "Minimum number of mentions required (default: 5)",
                        "required": False,
                    },
                },
            },
        },
        {
            "name": "get_account_smart_stats",
            "description": "Get smart stats and social metrics for a given username",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to get stats for",
                        "required": True,
                    },
                },
            },
        },
    ]

    # *************
    # API CONFIG
    # *************

    BASE_URL = "https://api.elfa.ai"
    API_VERSION = "v1"
    RATE_LIMIT = 60  # requests per minute

    # Headers configuration
    API_KEY_HEADER = "x-elfa-api-key"  # Updated header name for API key

    ENDPOINTS = {
        "mentions": f"/{API_VERSION}/mentions",
        "top_mentions": f"/{API_VERSION}/top-mentions",
        "mentions_search": f"/{API_VERSION}/mentions/search",
        "trending_tokens": f"/{API_VERSION}/trending-tokens",
        "account_smart_stats": f"/{API_VERSION}/account/smart-stats",
    }
