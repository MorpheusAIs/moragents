class Config:
    """Configuration for RugcheckAgent tools"""

    tools = [
        {
            "name": "get_token_report",
            "description": "Generate a report summary for a given token mint address",
            "parameters": {
                "type": "object",
                "properties": {"mint": {"type": "string", "description": "Token mint address to analyze"}},
                "required": ["mint"],
            },
        },
        {
            "name": "get_most_viewed",
            "description": "Get most viewed tokens in past 24 hours",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "get_most_voted",
            "description": "Get most voted tokens in past 24 hours",
            "parameters": {"type": "object", "properties": {}},
        },
    ]
