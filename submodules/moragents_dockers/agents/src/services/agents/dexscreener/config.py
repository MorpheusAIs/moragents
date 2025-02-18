# from src.models.service.agent_config import AgentConfig


# class Config:
#     """Configuration for DexScreener Token API."""

#     # *************
#     # AGENT CONFIG
#     # ------------
#     # This must be defined in every agent config file
#     # It is required to load the agent
#     # *************

#     agent_config = AgentConfig(
#         path="src.services.agents.dexscreener.agent",
#         class_name="DexScreenerAgent",
#         description="Fetches and analyzes cryptocurrency trading data from DexScreener.",
#         human_readable_name="DexScreener Analyst",
#         command="dexscreener",
#         upload_required=False,
#     )

#     # *************
#     # TOOLS CONFIG
#     # *************

#     tools = [
#         {
#             "name": "get_latest_token_profiles",
#             "description": "Get the latest token profiles from DexScreener",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "chain_id": {
#                         "type": "string",
#                         "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
#                         "required": False,
#                     }
#                 },
#             },
#         },
#         {
#             "name": "get_latest_boosted_tokens",
#             "description": "Get the latest boosted tokens from DexScreener",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "chain_id": {
#                         "type": "string",
#                         "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
#                         "required": False,
#                     }
#                 },
#             },
#         },
#         {
#             "name": "get_top_boosted_tokens",
#             "description": "Get the tokens with most active boosts",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "chain_id": {
#                         "type": "string",
#                         "description": "Optional chain ID to filter results (e.g., 'solana', 'ethereum')",
#                         "required": False,
#                     }
#                 },
#             },
#         },
#         {
#             "name": "search_dex_pairs",
#             "description": "Search for DEX trading pairs and their activity",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "Search query (e.g., token symbol like 'ETH' or 'BTC')",
#                         "required": True,
#                     }
#                 },
#             },
#         },
#     ]

#     # *************
#     # API CONFIG
#     # *************

#     BASE_URL = "https://api.dexscreener.com"
#     RATE_LIMIT = 60  # requests per minute

#     ENDPOINTS = {
#         "token_profiles": "/token-profiles/latest/v1",
#         "latest_boosts": "/token-boosts/latest/v1",
#         "top_boosts": "/token-boosts/top/v1",
#         "dex_search": "/latest/dex/search",
#     }
