import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DELEGATOR_CONFIG = {
    "agents": [
        {
            "path": "base_agent.agent",
            "class": "BaseAgent",
            "description": "If the user wants to send a transaction on Base",
            "name": "Base Agent",
            "upload": False
        }
    ]
}

class Config:

    DEFAULT_ACTION = "eth_transfer"