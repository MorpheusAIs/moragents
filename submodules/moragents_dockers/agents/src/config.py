import logging
import datetime

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:

    # Model configuration
    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
    OLLAMA_URL = "http://ollama:11434"

    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024
    AGENTS_CONFIG = {
        "agents": [
            {
                "path": "src.agents.default.agent",
                "class": "DefaultAgent",
                "description": "Must be used for meta-queries that ask about active Morpheus agents, and also for general, simple questions",
                "name": "default",
                "human_readable_name": "Default General Purpose",
                "command": "morpheus",
                "upload_required": False,
            },
            {
                "path": "src.agents.imagen.agent",
                "class": "ImagenAgent",
                "description": "Must only be used for image generation tasks. Use when the query explicitly mentions generating or creating an image.",
                "name": "imagen",
                "human_readable_name": "Image Generator",
                "command": "imagen",
                "upload_required": False,
            },
            {
                "path": "src.agents.base_agent.agent",
                "class": "BaseAgent",
                "description": "Handles transactions on the Base crypto network. Use when the user makes any reference to Base, base, the base network, or Coinbase",
                "name": "base",
                "human_readable_name": "Base Transaction Manager",
                "command": "base",
                "upload_required": False,
            },
            {
                "path": "src.agents.crypto_data.agent",
                "class": "CryptoDataAgent",
                "description": "Crypto-specific. Provides real-time cryptocurrency data such as price, market cap, and fully diluted valuation (FDV).",
                "name": "crypto data",
                "human_readable_name": "Crypto Data Fetcher",
                "command": "crypto",
                "upload_required": False,
            },
            # TODO: Pending fix to swap agent. The swap agent's preview is often correct however the metamask preview is wrong.
            # {
            #     "path": "src.agents.token_swap.agent",
            #     "class": "TokenSwapAgent",
            #     "description": "Handles cryptocurrency swapping operations. Use when the query explicitly mentions swapping, exchanging, or converting one cryptocurrency to another.",
            #     "name": "token swap",
            #     "human_readable_name": "Token Swap Manager",
            #     "command": "swap",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.tweet_sizzler.agent",
                "class": "TweetSizzlerAgent",
                "description": "Generates engaging tweets. Use ONLY when the query explicitly mentions tweet, Twitter, posting, tweeting, or the X platform.",
                "name": "tweet sizzler",
                "human_readable_name": "Tweet / X-Post Generator",
                "command": "tweet",
                "upload_required": False,
            },
            {
                "path": "src.agents.dca_agent.agent",
                "class": "DCAAgent",
                "description": "Sets up DCA strategies. Use when the user requests to set up a dollar-cost averaging strategy for crypto purchases or trades.",
                "name": "dca",
                "human_readable_name": "DCA Strategy Manager",
                "command": "dca",
                "upload_required": False,
            },
            {
                "path": "src.agents.rag.agent",
                "class": "RagAgent",
                "description": "Answers questions about a document. Must be used anytime an upload, a document, Documents, or uploaded document is mentioned",
                "name": "rag",
                "human_readable_name": "Document Assistant",
                "command": "document",
                "upload_required": True,
            },
            # DISABLED:
            #
            # {
            #     "path": "src.agents.mor_claims.agent",
            #     "class": "MorClaimsAgent",
            #     "description": "Manages the process of claiming rewards or tokens, specifically MOR rewards. Use when the query explicitly mentions claiming rewards or tokens.",
            #     "name": "mor claims",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.mor_rewards.agent",
                "class": "MorRewardsAgent",
                "description": "Provides information about user's accrued MOR rewards or tokens. Use when the query is about checking or querying reward balances.",
                "name": "mor rewards",
                "human_readable_name": "MOR Rewards Tracker",
                "command": "rewards",
                "upload_required": False,
            },
            {
                "path": "src.agents.realtime_search.agent",
                "class": "RealtimeSearchAgent",
                "description": f"Use when the query is about searching the web or asks about a recent / current event (The year is {datetime.datetime.now().year})",
                "name": "realtime search",
                "human_readable_name": "Real-Time Search",
                "command": "search",
                "upload_required": False,
            },
            # TODO: Pending fix to RSS feed. The RSS feed finds very irrelevant news right now.
            # {
            #     "path": "src.agents.news_agent.agent",
            #     "class": "NewsAgent",
            #     "description": "Fetches and analyzes cryptocurrency news for potential price impacts.",
            #     "name": "crypto news",
            #     "human_readable_name": "Crypto News Analyst",
            #     "command": "news",
            #     "upload_required": False,
            # },
            {
                "path": "src.agents.dexscreener.agent",
                "class": "DexScreenerAgent",
                "description": "Fetches and analyzes cryptocurrency trading data from DexScreener.",
                "name": "dexscreener",
                "human_readable_name": "DexScreener Analyst",
                "command": "dexscreener",
                "upload_required": False,
            },
            {
                "path": "src.agents.rugcheck.agent",
                "class": "RugcheckAgent",
                "description": "Analyzes token safety and trends using the Rugcheck API. Use when the query is about checking token safety, risks, or viewing trending tokens.",
                "name": "rugcheck",
                "human_readable_name": "Token Safety Analyzer",
                "command": "rugcheck",
                "upload_required": False,
            },
        ]
    }
