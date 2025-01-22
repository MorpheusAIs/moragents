import pytest
from unittest.mock import patch

from src.agents.dca_agent.agent import DCAAgent
from src.models.core import AgentResponse


@pytest.fixture
def dca_agent(llm, embeddings):
    config = {"name": "dca", "description": "Agent for DCA strategies"}
    return DCAAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_missing_cdp_client(dca_agent, make_chat_request):
    request = make_chat_request(content="Set up DCA strategy", agent_name="dca")

    with patch("src.stores.wallet_manager_instance.configure_cdp_client") as mock_cdp:
        mock_cdp.return_value = False

        response = await dca_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "needs_info"
        assert "CDP client is not initialized" in response.content
        assert "API credentials" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_missing_wallet(dca_agent, make_chat_request):
    request = make_chat_request(content="Set up DCA strategy", agent_name="dca")

    with patch("src.stores.wallet_manager_instance.configure_cdp_client") as mock_cdp:
        mock_cdp.return_value = True
        with patch("src.stores.wallet_manager_instance.get_active_wallet") as mock_wallet:
            mock_wallet.return_value = None

            response = await dca_agent._process_request(request)

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "needs_info"
            assert "select or create a wallet" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_successful_dca_setup(dca_agent, make_chat_request):
    request = make_chat_request(content="Set up DCA strategy", agent_name="dca")

    with patch("src.stores.wallet_manager_instance.configure_cdp_client") as mock_cdp:
        mock_cdp.return_value = True
        with patch("src.stores.wallet_manager_instance.get_active_wallet") as mock_wallet:
            mock_wallet.return_value = "mock_wallet"

            response = await dca_agent._process_request(request)

            assert isinstance(response, AgentResponse)
            assert response.response_type.value == "action_required"
            assert response.content == "Ready to set up DCA"
            assert response.action_type == "dca"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_execute_unknown_tool(dca_agent):
    response = await dca_agent._execute_tool("unknown_function", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "needs_info"
    assert "I don't know how to unknown_function yet" in response.content
