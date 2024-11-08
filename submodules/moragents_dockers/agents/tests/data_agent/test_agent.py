import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src", "data_agent", "src"))
)
# The above sys/os lines are needed because the agents have identical namings (i.e. agent.py, tools.py)

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, request
from src.data_agent.src.agent import (
    chat,
    clear_messages,
    generate_response,
    get_messages,
    get_response,
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
    response, role = get_response(message, mock_llm)
    assert response == "This is a test response"
    assert role == "assistant"


def test_get_response_with_tool_call(mock_llm):
    mock_llm.create_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "get_price", "arguments": '{"coin_name": "bitcoin"}'}}
                    ]
                }
            }
        ]
    }

    with patch("agent.tools.get_coin_price_tool") as mock_price_tool:
        mock_price_tool.return_value = "The price of bitcoin is $50,000"
        message = [{"role": "user", "content": "What's the price of Bitcoin?"}]
        response, role = get_response(message, mock_llm)

    assert response == "The price of bitcoin is $50,000"
    assert role == "assistant"


def test_generate_response(mock_llm):
    prompt = {"role": "user", "content": "Hello"}
    response, role = generate_response(prompt, mock_llm)
    assert response == "This is a test response"
    assert role == "assistant"


def test_chat(app, mock_llm):
    with app.test_request_context(json={"prompt": "Hello"}):
        with patch(
            "agent.generate_response", return_value=("This is a test response", "assistant")
        ):
            response, status_code = chat(request, mock_llm)

    assert status_code == 200
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
