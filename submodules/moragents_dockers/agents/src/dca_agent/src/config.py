import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

DELEGATOR_CONFIG = {
    "agents": [
        {
            "path": "dca_agent.agent",
            "class": "DCAAgent",
            "description": "If the user wants to set up a dollar-cost averaging strategy for crypto purchases.",
            "name": "DCA Agent",
            "upload": False
        }
    ]
}

class Config:

    CDP_API_KEY = "cdp_api_key"
    CDP_API_SECRET = "cdp_api_secret"
