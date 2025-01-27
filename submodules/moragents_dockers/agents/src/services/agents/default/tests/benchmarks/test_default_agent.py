import pytest
from unittest.mock import patch

from src.agents.default.agent import DefaultAgent
from src.models.service.chat_models import AgentResponse


@pytest.fixture
def default_agent(llm, embeddings):
    config = {"name": "default", "description": "Agent for general conversation"}
    return DefaultAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_general_conversation(default_agent, make_chat_request):
    request = make_chat_request(content="What is the weather like?", agent_name="default")

    with patch("src.stores.agent_manager_instance.get_available_agents") as mock_available:
        mock_available.return_value = []
        with patch("src.stores.agent_manager_instance.get_selected_agents") as mock_selected:
            mock_selected.return_value = []

            response = await default_agent._process_request(request)

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "success"
            assert response.content is not None


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_agent_info_request(default_agent, make_chat_request):
    request = make_chat_request(content="What can Morpheus agents do?", agent_name="default")

    mock_agents = [
        {"name": "crypto_data", "human_readable_name": "Crypto Data", "description": "Crypto data queries"},
        {"name": "dca", "human_readable_name": "DCA", "description": "DCA strategies"},
    ]

    with patch("src.stores.agent_manager_instance.get_available_agents") as mock_available:
        mock_available.return_value = mock_agents
        with patch("src.stores.agent_manager_instance.get_selected_agents") as mock_selected:
            mock_selected.return_value = ["crypto_data", "dca"]

            response = await default_agent._process_request(request)

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "success"
            assert response.content is not None


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_error_handling(default_agent, make_chat_request):
    request = make_chat_request(content="Test error handling", agent_name="default")

    with patch("src.stores.agent_manager_instance.get_available_agents") as mock_available:
        mock_available.side_effect = Exception("Test error")

        response = await default_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "error"
        assert "Test error" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_unknown_tool(default_agent):
    response = await default_agent._execute_tool("unknown_function", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "error"
    assert "Unknown tool" in response.error_message
