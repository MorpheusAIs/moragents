import pytest
from unittest.mock import patch

from src.agents.dexscreener.agent import DexScreenerAgent
from src.models.core import AgentResponse


@pytest.fixture
def dex_agent(llm, embeddings):
    config = {"name": "dexscreener", "description": "Agent for DexScreener API interactions"}
    return DexScreenerAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_search_dex_pairs_success(dex_agent, make_chat_request):
    request = make_chat_request(content="Search for ETH/USDC pairs", agent_name="dexscreener")

    mock_pairs = [
        {
            "baseToken": {"symbol": "ETH"},
            "quoteToken": {"symbol": "USDC"},
            "dexId": "uniswap",
            "chainId": "ethereum",
            "priceUsd": "1850.45",
            "priceChange": {"h24": 2.5},
            "volume": {"h24": 1000000},
            "liquidity": {"usd": 5000000},
            "txns": {"h24": {"buys": 100, "sells": 50}},
            "url": "https://dexscreener.com/eth/pair",
        }
    ]

    with patch("src.agents.dexscreener.tools.search_dex_pairs") as mock_search:
        mock_search.return_value = mock_pairs

        response = await dex_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "ETH / USDC" in response.content
        assert "uniswap" in response.content.lower()


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_get_latest_token_profiles(dex_agent, make_chat_request):
    request = make_chat_request(content="Get latest token profiles on ethereum", agent_name="dexscreener")

    mock_tokens = [
        {
            "tokenAddress": "0x123",
            "description": "Test Token",
            "icon": "https://icon.url",
            "url": "https://dexscreener.com/token",
            "links": [{"type": "website", "url": "https://test.com"}],
        }
    ]

    with patch("src.agents.dexscreener.tools.get_latest_token_profiles") as mock_profiles:
        mock_profiles.return_value = mock_tokens

        response = await dex_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "0x123" in response.content
        assert "Test Token" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_get_boosted_tokens(dex_agent, make_chat_request):
    request = make_chat_request(content="Show me boosted tokens", agent_name="dexscreener")

    mock_tokens = [
        {"tokenAddress": "0x456", "description": "Boosted Token", "url": "https://dexscreener.com/boosted", "links": []}
    ]

    with patch("src.agents.dexscreener.tools.get_latest_boosted_tokens") as mock_boosted:
        mock_boosted.return_value = mock_tokens

        response = await dex_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "0x456" in response.content
        assert "Boosted Token" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_error_handling(dex_agent, make_chat_request):
    request = make_chat_request(content="Search for tokens", agent_name="dexscreener")

    with patch("src.agents.dexscreener.tools.search_dex_pairs") as mock_search:
        mock_search.side_effect = Exception("API Error")

        response = await dex_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "error"
        assert "API Error" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_empty_results(dex_agent, make_chat_request):
    request = make_chat_request(content="Search for non-existent token", agent_name="dexscreener")

    with patch("src.agents.dexscreener.tools.search_dex_pairs") as mock_search:
        mock_search.return_value = []

        response = await dex_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "No DEX pairs found" in response.content
