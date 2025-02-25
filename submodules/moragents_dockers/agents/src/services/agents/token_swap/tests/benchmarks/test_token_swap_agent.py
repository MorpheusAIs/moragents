import pytest
from unittest.mock import patch, Mock
from src.services.agents.token_swap.agent import TokenSwapAgent
from src.models.service.chat_models import AgentResponse, ChatRequest
from src.services.agents.token_swap.tools import InsufficientFundsError, TokenNotFoundError, SwapNotPossibleError


@pytest.fixture
def token_swap_agent(llm, embeddings):
    config = {
        "name": "token_swap",
        "description": "Agent for handling token swaps",
        "APIBASEURL": "https://api.1inch.io/v5.0/",
    }
    return TokenSwapAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_swap_success(token_swap_agent, make_chat_request):
    request = make_chat_request(
        content="Swap 1 ETH for USDT", agent_name="token_swap", chain_id="1", wallet_address="0x123"
    )

    mock_swap_result = {
        "fromToken": {"symbol": "ETH"},
        "toToken": {"symbol": "USDT"},
        "toAmount": "1000000000000000000",
    }

    with patch("src.services.agents.token_swap.tools.swap_coins") as mock_swap:
        mock_swap.return_value = (mock_swap_result, None)

        response = await token_swap_agent._execute_tool(
            "swap_agent", {"token1": "ETH", "token2": "USDT", "value": "1.0"}
        )

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "action_required"
        assert response.action_type == "swap"
        assert response.metadata == mock_swap_result


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_swap_insufficient_funds(token_swap_agent):
    with patch("src.services.agents.token_swap.tools.swap_coins") as mock_swap:
        mock_swap.side_effect = InsufficientFundsError("Insufficient funds")

        response = await token_swap_agent._execute_tool(
            "swap_agent", {"token1": "ETH", "token2": "USDT", "value": "1000.0"}
        )

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "needs_info"
        assert "Insufficient funds" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_swap_token_not_found(token_swap_agent):
    with patch("src.services.agents.token_swap.tools.swap_coins") as mock_swap:
        mock_swap.side_effect = TokenNotFoundError("Token not found")

        response = await token_swap_agent._execute_tool(
            "swap_agent", {"token1": "INVALID", "token2": "USDT", "value": "1.0"}
        )

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "needs_info"
        assert "Token not found" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_get_allowance(token_swap_agent):
    mock_allowance = {"allowance": "1000000000000000000"}

    with patch.object(token_swap_agent, "_check_allowance") as mock_check:
        mock_check.return_value = mock_allowance

        response = await token_swap_agent.get_allowance("0xtoken", "0xwallet", "1")

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert response.metadata == mock_allowance


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_approve_transaction(token_swap_agent):
    mock_approval = {"data": "0x...", "gasPrice": "10000000000"}

    with patch.object(token_swap_agent, "_approve_transaction") as mock_approve:
        mock_approve.return_value = mock_approval

        response = await token_swap_agent.approve("0xtoken", "1", "1000000000000000000")

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert response.metadata == mock_approval


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_tx_status_success(token_swap_agent):
    mock_request = Mock()
    mock_request.json.return_value = {"status": "success", "tx_hash": "0x123", "tx_type": "swap"}

    response = await token_swap_agent.tx_status(mock_request)

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "success"
    assert "transaction was successful" in response.content
    assert "0x123" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_missing_parameters(token_swap_agent):
    response = await token_swap_agent._execute_tool("swap_agent", {"token1": "ETH"})  # Missing token2 and value

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "needs_info"
    assert "Please provide all required parameters" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_unknown_tool(token_swap_agent):
    response = await token_swap_agent._execute_tool("unknown_tool", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "needs_info"
    assert "I don't know how to unknown_tool" in response.content
