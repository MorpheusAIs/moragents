import pytest
from unittest.mock import patch, Mock
from src.agents.rugcheck.agent import RugcheckAgent
from src.models.core import AgentResponse, ChatRequest


@pytest.fixture
def rugcheck_agent(llm, embeddings):
    config = {"name": "rugcheck", "description": "Agent for analyzing token safety"}
    return RugcheckAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_token_report_success(rugcheck_agent, make_chat_request):
    request = make_chat_request(content="Analyze token BONK", agent_name="rugcheck")

    mock_report = {
        "score": 85,
        "risks": [{"name": "Liquidity Risk", "description": "Low liquidity detected", "score": 60}],
    }

    with patch.object(rugcheck_agent, "_fetch_token_report") as mock_fetch:
        mock_fetch.return_value = mock_report

        with patch.object(rugcheck_agent, "_resolve_token_identifier") as mock_resolve:
            mock_resolve.return_value = "BONK123"

            response = await rugcheck_agent._execute_tool("get_token_report", {"identifier": "BONK"})

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "success"
            assert "Token Analysis Report" in response.content
            assert "Overall Risk Score: 85" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_most_viewed_success(rugcheck_agent):
    mock_viewed = {
        "token1": {
            "mint": "mint123",
            "metadata": {"name": "Token1", "symbol": "TK1"},
            "visits": 1000,
            "user_visits": 500,
        }
    }

    with patch.object(rugcheck_agent, "_fetch_most_viewed") as mock_fetch:
        mock_fetch.return_value = mock_viewed

        response = await rugcheck_agent._execute_tool("get_most_viewed", {})

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "Most Viewed Tokens" in response.content
        assert "Token1" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_most_voted_success(rugcheck_agent):
    mock_voted = {"token1": {"mint": "mint123", "up_count": 100, "vote_count": 150}}

    with patch.object(rugcheck_agent, "_fetch_most_voted") as mock_fetch:
        mock_fetch.return_value = mock_voted

        response = await rugcheck_agent._execute_tool("get_most_voted", {})

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "Most Voted Tokens" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_invalid_token_identifier(rugcheck_agent):
    with patch.object(rugcheck_agent, "_resolve_token_identifier") as mock_resolve:
        mock_resolve.return_value = None

        response = await rugcheck_agent._execute_tool("get_token_report", {"identifier": "INVALID_TOKEN"})

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "error"
        assert "Could not resolve token identifier" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_unknown_tool(rugcheck_agent):
    response = await rugcheck_agent._execute_tool("unknown_function", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "error"
    assert "Unknown tool function" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_api_error_handling(rugcheck_agent):
    with patch.object(rugcheck_agent, "_fetch_token_report") as mock_fetch:
        mock_fetch.side_effect = Exception("API Error")

        with patch.object(rugcheck_agent, "_resolve_token_identifier") as mock_resolve:
            mock_resolve.return_value = "mint123"

            response = await rugcheck_agent._execute_tool("get_token_report", {"identifier": "TOKEN"})

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "error"
            assert "Failed to get token report" in response.error_message
