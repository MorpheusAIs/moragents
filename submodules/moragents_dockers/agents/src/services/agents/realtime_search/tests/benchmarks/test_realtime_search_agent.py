import pytest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup

from src.agents.realtime_search.agent import RealtimeSearchAgent
from src.models.service.chat_models import AgentResponse


@pytest.fixture
def realtime_search_agent(llm, embeddings):
    config = {"name": "realtime_search", "description": "Agent for real-time web searches"}
    return RealtimeSearchAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_web_search_success(realtime_search_agent, make_chat_request):
    request = make_chat_request(content="Search for latest news about AI", agent_name="realtime_search")

    mock_results = """
    Result:
    Latest breakthrough in AI technology announced
    Scientists develop new machine learning model
    """

    with patch.object(realtime_search_agent, "_perform_search_with_web_scraping") as mock_search:
        mock_search.return_value = mock_results

        with patch.object(realtime_search_agent, "_synthesize_answer") as mock_synthesize:
            mock_synthesize.return_value = "Here are the latest AI developments..."

            response = await realtime_search_agent._process_request(request)

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "success"
            assert "latest AI developments" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_web_search_no_results(realtime_search_agent, make_chat_request):
    request = make_chat_request(content="Search for nonexistent topic", agent_name="realtime_search")

    with patch.object(realtime_search_agent, "_perform_search_with_web_scraping") as mock_search:
        mock_search.return_value = AgentResponse.needs_info(
            content="I couldn't find any results for that search. Could you try rephrasing it?"
        )

        response = await realtime_search_agent._execute_tool("perform_web_search", {"search_term": "nonexistent topic"})

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "needs_info"
        assert "try rephrasing" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_web_search_fallback(realtime_search_agent, make_chat_request):
    request = make_chat_request(content="Search with fallback", agent_name="realtime_search")

    with patch.object(realtime_search_agent, "_perform_search_with_web_scraping") as mock_search:
        mock_search.side_effect = Exception("Primary search failed")

        with patch.object(realtime_search_agent, "_perform_search_with_headless_browsing") as mock_fallback:
            mock_fallback.return_value = "Fallback search results"

            response = await realtime_search_agent._execute_tool(
                "perform_web_search", {"search_term": "fallback search"}
            )

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "success"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_unknown_tool(realtime_search_agent):
    response = await realtime_search_agent._execute_tool("unknown_function", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "error"
    assert "Unknown tool" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_empty_search_term(realtime_search_agent):
    response = await realtime_search_agent._execute_tool("perform_web_search", {"search_term": ""})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "needs_info"
    assert "provide a search term" in response.content
