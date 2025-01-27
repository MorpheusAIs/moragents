import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from src.agents.crypto_data.routes import router
from src.models.service.chat_models import AgentResponse

client = TestClient(router)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_data_success():
    test_data = {"prompt": "What's the price of Bitcoin?"}
    mock_response = AgentResponse.success(content="Bitcoin price is $50,000")

    with patch("src.stores.agent_manager_instance.get_agent") as mock_get_agent:
        mock_agent = Mock()
        mock_agent.process_data.return_value = mock_response
        mock_get_agent.return_value = mock_agent

        with patch("src.stores.chat_manager_instance.add_message") as mock_add_message:
            response = client.post("/crypto_data/process_data", json=test_data)

            assert response.status_code == 200
            assert response.json() == mock_response.dict()
            mock_add_message.assert_called_once_with(mock_response)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_data_agent_not_found():
    test_data = {"prompt": "What's the price of Bitcoin?"}

    with patch("src.stores.agent_manager_instance.get_agent") as mock_get_agent:
        mock_get_agent.return_value = None

        response = client.post("/crypto_data/process_data", json=test_data)

        assert response.status_code == 400
        assert response.json() == {"status": "error", "message": "Crypto data agent not found"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_data_error():
    test_data = {"prompt": "What's the price of Bitcoin?"}

    with patch("src.stores.agent_manager_instance.get_agent") as mock_get_agent:
        mock_agent = Mock()
        mock_agent.process_data.side_effect = Exception("Test error")
        mock_get_agent.return_value = mock_agent

        response = client.post("/crypto_data/process_data", json=test_data)

        assert response.status_code == 500
        assert response.json() == {"status": "error", "message": "Failed to process data: Test error"}
