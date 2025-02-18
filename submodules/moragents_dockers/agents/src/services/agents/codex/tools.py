import logging
import os
from typing import Optional, List, Dict, Any

import aiohttp

from .config import Config
from .models import TopTokensResponse, TopHoldersResponse, NftSearchResponse

logger = logging.getLogger(__name__)


async def _make_graphql_request(query: str, variables: Optional[Dict[str, Any]] = None) -> Any:
    """Make a GraphQL request to Codex API."""
    # Get API key from environment
    api_key = os.environ.get("CODEX_API_KEY")
    if not api_key:
        raise Exception("CODEX_API_KEY environment variable is not set")

    headers = {"Authorization": api_key, "Content-Type": "application/json"}

    data = {"query": query, "variables": variables or {}}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(Config.GRAPHQL_URL, json=data, headers=headers) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get("message", str(result))
                    raise Exception(f"API request failed with status {response.status}: {error_msg}")

                if "errors" in result:
                    error = result["errors"][0]
                    error_msg = error.get("message", "Unknown GraphQL error")
                    raise Exception(f"GraphQL error: {error_msg}")

                return result["data"]
    except Exception as e:
        logger.error(f"API request failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to fetch data: {str(e)}")


async def list_top_tokens(
    limit: Optional[int] = None,
    network_filter: Optional[List[int]] = None,
    resolution: Optional[str] = None,
) -> TopTokensResponse:
    """Get list of trending tokens across specified networks."""
    try:
        variables = {
            "limit": min(limit or 20, 50),  # Default 20, max 50
            "networkFilter": network_filter or [],
            "resolution": resolution or "1D",  # Default to 1 day
        }

        query = """
        query ListTopTokens($limit: Int, $networkFilter: [Int!], $resolution: String) {
            listTopTokens(limit: $limit, networkFilter: $networkFilter, resolution: $resolution) {
                address
                createdAt
                decimals
                id
                imageBannerUrl
                imageLargeUrl
                imageSmallUrl
                imageThumbUrl
                isScam
                lastTransaction
                liquidity
                marketCap
                name
                networkId
                price
                priceChange
                priceChange1
                priceChange4
                priceChange12
                priceChange24
                quoteToken
                resolution
                symbol
                topPairId
                txnCount1
                txnCount4
                txnCount12
                txnCount24
                uniqueBuys1
                uniqueBuys4
                uniqueBuys12
                uniqueBuys24
                uniqueSells1
                uniqueSells4
                uniqueSells12
                uniqueSells24
                volume
            }
        }
        """

        response = await _make_graphql_request(query, variables)
        return TopTokensResponse(success=True, data=response["listTopTokens"])
    except Exception as e:
        logger.error(f"Failed to get top tokens: {str(e)}", exc_info=True)
        raise Exception(f"Failed to get top tokens: {str(e)}")


async def get_top_holders_percent(token_id: str) -> TopHoldersResponse:
    """Get percentage owned by top 10 holders for a token."""
    try:
        variables = {"tokenId": token_id}

        query = """
        query GetTop10HoldersPercent($tokenId: String!) {
            top10HoldersPercent(tokenId: $tokenId)
        }
        """

        response = await _make_graphql_request(query, variables)
        return TopHoldersResponse(success=True, data=response["top10HoldersPercent"])
    except Exception as e:
        logger.error(f"Failed to get top holders percentage: {str(e)}", exc_info=True)
        raise Exception(f"Failed to get top holders percentage: {str(e)}")


async def search_nfts(
    search: str,
    limit: Optional[int] = None,
    network_filter: Optional[List[int]] = None,
    filter_wash_trading: Optional[bool] = None,
    window: Optional[str] = None,
) -> NftSearchResponse:
    """Search for NFT collections by name or address."""
    try:
        variables = {
            "search": search,
            "limit": limit or 20,  # Default to 20 results
            "networkFilter": network_filter or [],
            "filterWashTrading": filter_wash_trading or False,
            "window": window or "1d",  # Default to 1 day
        }

        query = """
        query SearchNFTs($search: String!, $limit: Int, $networkFilter: [Int!], $filterWashTrading: Boolean, $window: String) {
            searchNfts(search: $search, limit: $limit, networkFilter: $networkFilter, filterWashTrading: $filterWashTrading, window: $window) {
                hasMore
                items {
                    address
                    average
                    ceiling
                    floor
                    id
                    imageUrl
                    name
                    networkId
                    symbol
                    tradeCount
                    tradeCountChange
                    volume
                    volumeChange
                    window
                }
            }
        }
        """

        response = await _make_graphql_request(query, variables)
        return NftSearchResponse(
            success=True, hasMore=response["searchNfts"]["hasMore"], items=response["searchNfts"]["items"]
        )
    except Exception as e:
        logger.error(f"Failed to search NFTs: {str(e)}", exc_info=True)
        raise Exception(f"Failed to search NFTs: {str(e)}")
