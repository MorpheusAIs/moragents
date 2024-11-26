import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DELEGATOR_CONFIG = {
    "agents": [
        {
            "path": "dca_agent.agent",
            "class": "DCAAgent",
            "description": "If the user wants to set up a dollar-cost averaging strategy for crypto purchases.",
            "name": "DCA Agent",
            "upload": False,
        }
    ]
}


class Config:

    CDP_API_KEY = ""
    CDP_API_SECRET = ""
    DEFAULT_ACTION = "eth_transfer"
