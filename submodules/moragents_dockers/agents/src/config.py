import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:

    # Model configuration
    MODEL_NAME = "meetkai/functionary-small-v2.4-GGUF"
    MODEL_REVISION = "functionary-small-v2.4.Q4_0.gguf"
    MODEL_PATH = "model/" + MODEL_REVISION
    DOWNLOAD_DIR = "model"
    OLLAMA_URL = "http://host.docker.internal:11434"
    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024
    DELEGATOR_CONFIG = {
        "agents": [
            {
                "path": "rag_agent.src.agent",
                "class": "RagAgent",
                "description": "Handles general queries, information retrieval, and context-based questions. Use for any query that doesn't explicitly match other agents' specialties.",
                "name": "general purpose and context-based rag agent",
                "upload_required": True,
            },
            {
                "path": "data_agent.src.agent",
                "class": "DataAgent",
                "description": "Crypto-specific. Provides real-time cryptocurrency data such as price, market cap, and fully diluted valuation (FDV).",
                "name": "crypto data agent",
                "upload_required": False,
            },
            {
                "path": "swap_agent.src.agent",
                "class": "SwapAgent",
                "description": "Handles cryptocurrency swapping operations. Use when the query explicitly mentions swapping, exchanging, or converting one cryptocurrency to another.",
                "name": "crypto swap agent",
                "upload_required": False,
            },
            {
                "path": "tweet_sizzler_agent.src.agent",
                "class": "TweetSizzlerAgent",
                "description": "Generates and posts engaging tweets. Use when the query explicitly mentions Twitter, tweeting, or X platform.",
                "name": "tweet sizzler agent",
                "upload_required": False,
            },
            {
                "path": "dca_agent.src.agent",
                "class": "DCAAgent",
                "description": "If the user wants to set up a dollar-cost averaging strategy for crypto purchases.",
                "name": "dca agent",
                "upload_required": False
            },
            {
                "path": "gasless_agent.src.agent",
                "class": "GaslessAgent",
                "description": "If the user wants to create a gasless wallet and send a transaction.",
                "name": "gasless agent",
                "upload_required": False
            },
            {
                "path": "reward_agent.src.agent",
                "class": "RewardAgent",
                "description": "Provides information about user's accrued MOR rewards or tokens. Use when the query is about checking or querying reward balances.",
                "name": "reward agent",
                "upload_required": False,
            },
        ]
    }
