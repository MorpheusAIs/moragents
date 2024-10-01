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