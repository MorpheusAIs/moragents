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
                "path": "src.agents.default.agent",
                "class": "DefaultAgent",
                "description": "Must be used for meta-queries that ask about active agents, and also for general purpose queries that don't match other agents' specialties.",
                "name": "default agent",
                "human_readable_name": "Default General Purpose Agent",
                "upload_required": False,
            },
            # {
            #     "path": "src.agents.imagen.agent",
            #     "class": "ImagenAgent",
            #     "description": "Must only be used for image generation tasks. Use when the query explicitly mentions generating or creating an image.",
            #     "name": "imagen agent",
            #     "human_readable_name": "Image Generator",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.rag.agent",
            #     "class": "RagAgent",
            #     "description": "Must be used anytime an upload or uploaded document is referred to.",
            #     "name": "rag agent",
            #     "human_readable_name": "Document Assistant",
            #     "upload_required": True,
            # },
            # {
            #     "path": "src.agents.crypto_data.agent",
            #     "class": "CryptoDataAgent",
            #     "description": "Crypto-specific. Provides real-time cryptocurrency data such as price, market cap, and fully diluted valuation (FDV).",
            #     "name": "crypto data agent",
            #     "human_readable_name": "Crypto Data Fetcher",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.token_swap.agent",
            #     "class": "TokenSwapAgent",
            #     "description": "Handles cryptocurrency swapping operations. Use when the query explicitly mentions swapping, exchanging, or converting one cryptocurrency to another.",
            #     "name": "token swap agent",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.tweet_sizzler.agent",
            #     "class": "TweetSizzlerAgent",
            #     "description": "Generates and posts engaging tweets. Use when the query explicitly mentions Twitter, tweeting, or X platform.",
            #     "name": "tweet sizzler agent",
            #     "human_readable_name": "Tweet / X-Post Generator",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.dca_agent.agent",
                "class": "DCAAgent",
                "description": "If the user wants to DCA into or set up a dollar-cost averaging strategy for crypto purchases.",
                "name": "dca agent",
                "human_readable_name": "DCA Strategy Manager",
                "upload_required": False,
            },
            {
                "path": "src.agents.base_agent.agent",
                "class": "BaseAgent",
                "description": "If the user wants to run any transactions on Base or makes any reference to Coinbase or Base.",
                "name": "base agent",
                "human_readable_name": "Base Transaction Manager",
                "upload_required": False,
            },
            # {
            #     "path": "src.agents.mor_claims.agent",
            #     "class": "MorClaimsAgent",
            #     "description": "Manages the process of claiming rewards or tokens, specifically MOR rewards. Use when the query explicitly mentions claiming rewards or tokens.",
            #     "name": "mor claims agent",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.mor_rewards.agent",
            #     "class": "MorRewardsAgent",
            #     "description": "Provides information about user's accrued MOR rewards or tokens. Use when the query is about checking or querying reward balances.",
            #     "name": "mor rewards agent",
            #     "human_readable_name": "MOR Rewards Tracker",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.realtime_search.agent",
            #     "class": "RealtimeSearchAgent",
            #     "description": "Use when the query is about searching the web for real-time information or asks about a recent / current event.",
            #     "name": "realtime search agent",
            #     "human_readable_name": "Real-Time Search",
            #     "upload_required": False,
            # },
            # {
            #     "path": "src.agents.news_agent.agent",
            #     "class": "NewsAgent",
            #     "description": "Fetches and analyzes cryptocurrency news for potential price impacts.",
            #     "name": "crypto news agent",
            #     "human_readable_name": "Crypto News Analyst",
            #     "upload_required": False,
            # },
        ]
    }
