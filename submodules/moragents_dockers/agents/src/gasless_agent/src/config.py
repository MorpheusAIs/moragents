import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DELEGATOR_CONFIG = {
    "agents": [
        {
            "path": "gasless_agent.agent",
            "class": "GaslessTransactionAgent",
            "description": "If the user wants to send a gasless transaction to another user.",
            "name": "Gasless Transaction Agent",
            "upload": False
        }
    ]
}

class Config:

    CDP_API_KEY = "cdp_api_key"
    CDP_API_SECRET = "cdp_api_secret"