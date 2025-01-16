import logging
from typing import Dict, Any, List, Optional
import aiohttp
from src.agents.dexscreener.models import TokenProfile, BoostedToken
from src.agents.dexscreener.config import Config

logger = logging.getLogger(__name__)


def filter_by_chain(tokens: List[Dict[str, Any]], chain_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Filter tokens by chain ID if provided."""
    if not chain_id:
        return tokens
    return [token for token in tokens if token.get("chainId", "").lower() == chain_id.lower()]


async def _make_request(endpoint: str) -> Dict[str, Any]:
    """Make an API request to DexScreener."""
    url = f"{Config.BASE_URL}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                return await response.json()
    except Exception as e:
        logger.error(f"API request failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to fetch data: {str(e)}")


async def get_latest_token_profiles(chain_id: Optional[str] = None) -> List[TokenProfile]:
    """Get the latest token profiles, optionally filtered by chain."""
    try:
        response = await _make_request(Config.ENDPOINTS["token_profiles"])
        tokens = response if isinstance(response, list) else []
        return filter_by_chain(tokens, chain_id)
    except Exception as e:
        raise Exception(f"Failed to get token profiles: {str(e)}")


async def get_latest_boosted_tokens(chain_id: Optional[str] = None) -> List[BoostedToken]:
    """Get the latest boosted tokens, optionally filtered by chain."""
    try:
        response = await _make_request(Config.ENDPOINTS["latest_boosts"])
        tokens = response if isinstance(response, list) else []
        return filter_by_chain(tokens, chain_id)
    except Exception as e:
        raise Exception(f"Failed to get boosted tokens: {str(e)}")


async def get_top_boosted_tokens(chain_id: Optional[str] = None) -> List[BoostedToken]:
    """Get tokens with most active boosts, optionally filtered by chain."""
    try:
        response = await _make_request(Config.ENDPOINTS["top_boosts"])
        tokens = response if isinstance(response, list) else []
        filtered_tokens = filter_by_chain(tokens, chain_id)

        # Sort by total amount
        return sorted(filtered_tokens, key=lambda x: float(x.get("totalAmount", 0) or 0), reverse=True)
    except Exception as e:
        raise Exception(f"Failed to get top boosted tokens: {str(e)}")


async def search_dex_pairs(query: str) -> List[Dict[str, Any]]:
    """Search for DEX pairs matching the query."""
    try:
        endpoint = f"{Config.ENDPOINTS['dex_search']}?q={query}"
        response = await _make_request(endpoint)
        return response.get("pairs", [])
    except Exception as e:
        raise Exception(f"Failed to search DEX pairs: {str(e)}")
