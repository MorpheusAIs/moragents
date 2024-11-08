import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "swap_agent", "src"))
)
# The above sys/os lines are needed because the agents have identical namings (i.e. agent.py, tools.py)

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, request
from src.swap_agent.src.agent import (
    approve,
    chat,
    clear_messages,
    generate_response,
    get_allowance,
    get_messages,
    get_response,
    swap,
)


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.create_chat_completion.return_value = {
        "choices": [{"message": {"content": "This is a test response"}}]
    }
    return mock


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


def test_get_response(mock_llm):
    message = [{"role": "user", "content": "Hello"}]
    response, role = get_response(message, "chain_id", "wallet_address", mock_llm)
    assert response == "This is a test response"
    assert role == "assistant"


def test_get_response_with_tool_call(mock_llm):
    mock_llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "swap_agent",
                                "arguments": '{"token1": "ETH", "token2": "USDT", "value": "1.0"}',
                            }
                        }
                    ]
                }
            }
        ]
    }

    with patch("src.swap_agent.src.tools.swap_coins") as mock_swap_coins:
        mock_swap_coins.return_value = ("Swap successful", "assistant")
        message = [{"role": "user", "content": "Swap 1 ETH for USDT"}]
        response, role = get_response(message, "chain_id", "wallet_address", mock_llm)

    assert response == "Swap successful"
    assert role == "assistant"


def test_generate_response(mock_llm):
    prompt = {"role": "user", "content": "Hello"}
    response, role = generate_response(prompt, "chain_id", "wallet_address", mock_llm)
    assert response == "This is a test response"
    assert role == "assistant"


def test_chat(app, mock_llm):
    with app.test_request_context(
        json={"prompt": "Hello", "wallet_address": "0x123", "chain_id": "1"}
    ):
        with patch(
            "src.swap_agent.src.agent.generate_response",
            return_value=("This is a test response", "assistant"),
        ):
            response = chat(request, mock_llm)

    assert response.status_code == 200
    assert response.json == {"role": "assistant", "content": "This is a test response"}


def test_chat_missing_prompt(app):
    with app.test_request_context(json={}):
        response, status_code = chat(request, None)

    assert status_code == 400
    assert "error" in response.json


def test_get_messages(app):
    with app.test_request_context():
        response = get_messages()

    assert response.status_code == 200
    assert "messages" in response.json


def test_clear_messages(app):
    with app.test_request_context():
        response = clear_messages()

    assert response.status_code == 200
    assert response.json["response"] == "successfully cleared message history"


def test_get_allowance(app):
    with app.test_request_context(
        json={"tokenAddress": "0x123", "walletAddress": "0x456", "chain_id": "1"}
    ):
        with patch("src.swap_agent.src.agent.check_allowance", return_value={"allowance": "1000"}):
            response = get_allowance(request)

    assert response.status_code == 200
    assert "response" in response.json


def test_approve(app):
    with app.test_request_context(
        json={"tokenAddress": "0x123", "chain_id": "1", "amount": "1000"}
    ):
        with patch(
            "src.swap_agent.src.agent.approve_transaction", return_value={"txHash": "0x789"}
        ):
            response = approve(request)

    assert response.status_code == 200
    assert "response" in response.json


def test_swap(app):
    swap_params = {
        "src": "ETH",
        "dst": "USDT",
        "walletAddress": "0x123",
        "amount": "1.0",
        "slippage": "1",
        "chain_id": "1",
    }
    with app.test_request_context(json=swap_params):
        with patch("src.swap_agent.src.agent.build_tx_for_swap", return_value={"txHash": "0x789"}):
            response = swap(request)

    assert {"txHash": "0x789"} == response
