import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:

    # Model configuration
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
    OLLAMA_URL = "http://host.docker.internal:11434"

    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024
    AGENTS_CONFIG = {
        "agents": [
            {
                "path": "src.agents.imagen.agent",
                "class": "ImagenAgent",
                "description": "Generates images based on a prompt.",
                "name": "imagen agent",
                "upload_required": False,
            },
            {
                "path": "src.agents.rag.agent",
                "class": "RagAgent",
                "description": "Must be used anytime an upload or uploaded document is referred to. Handles general queries, information retrieval, and context-based questions. Use for any query that doesn't explicitly match other agents' specialties.",
                "name": "general purpose and context-based rag agent",
                "upload_required": True,
            },
            {
                "path": "src.agents.crypto_data.agent",
                "class": "CryptoDataAgent",
                "description": "Crypto-specific. Provides real-time cryptocurrency data such as price, market cap, and fully diluted valuation (FDV).",
                "name": "crypto data agent",
                "upload_required": False,
            },
            # {
            #     "path": "src.agents.token_swap.agent",
            #     "class": "TokenSwapAgent",
            #     "description": "Handles cryptocurrency swapping operations. Use when the query explicitly mentions swapping, exchanging, or converting one cryptocurrency to another.",
            #     "name": "token swap agent",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.tweet_sizzler.agent",
                "class": "TweetSizzlerAgent",
                "description": "Generates and posts engaging tweets. Use when the query explicitly mentions Twitter, tweeting, or X platform.",
                "name": "tweet sizzler agent",
                "upload_required": False,
            },
            {
                "path": "src.agents.dca_agent.agent",
                "class": "DCAAgent",
                "description": "If the user wants to set up a dollar-cost averaging strategy for crypto purchases.",
                "name": "dca agent",
                "upload_required": False,
            },
            {
                "path": "src.agents.base_agent.agent",
                "class": "BaseAgent",
                "description": "If the user wants to send a transaction on Base.",
                "name": "base agent",
                "upload_required": False,
            },
            # {
            #     "path": "src.agents.mor_claims.agent",
            #     "class": "MorClaimsAgent",
            #     "description": "Manages the process of claiming rewards or tokens, specifically MOR rewards. Use when the query explicitly mentions claiming rewards or tokens.",
            #     "name": "mor claims agent",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.mor_rewards.agent",
                "class": "MorRewardsAgent",
                "description": "Provides information about user's accrued MOR rewards or tokens. Use when the query is about checking or querying reward balances.",
                "name": "mor rewards agent",
                "upload_required": False,
            },
            {
                "path": "src.agents.realtime_search.agent",
                "class": "RealtimeSearchAgent",
                "description": "Only use this agent for real-time data. This agent is not for general purpose queries. Use when the query is about searching the web for real-time information.",
                "name": "realtime search agent",
                "upload_required": False,
            },
            {
                "path": "src.agents.news_agent.agent",
                "class": "NewsAgent",
                "description": "Fetches and analyzes cryptocurrency news for potential price impacts.",
                "name": "crypto news agent",
                "upload_required": False,
            },
        ]
    }
