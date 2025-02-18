import asyncio
import sys

import pytest
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

from src.models.service.chat_models import ChatRequest, ChatMessage
from src.config import AppConfig


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption("--benchmark", action="store_true", help="run benchmark tests")
    parser.addoption("--unit", action="store_true", help="run unit tests")


def pytest_runtest_setup(item):
    """Skip tests based on custom command line options"""
    markers = {marker.name for marker in item.iter_markers()}
    benchmark_opt = item.config.getoption("--benchmark")
    unit_opt = item.config.getoption("--unit")

    # Handle benchmark tests
    if "benchmark" in markers and not benchmark_opt:
        pytest.skip(reason="skipping benchmark tests")

    # Handle unit tests
    if "unit" in markers and not unit_opt:
        pytest.skip(reason="skipping unit tests")


# See https://github.com/pytest-dev/pytest-asyncio/issues/68
# See https://github.com/pytest-dev/pytest-asyncio/issues/257
# Also need ProactorEventLoop on older versions of Python with Windows so
# that asyncio subprocess works properly
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session"""
    if sys.version_info < (3, 8) and sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def llm():
    try:
        return ChatOllama(
            model=AppConfig.OLLAMA_MODEL,
            base_url="http://localhost:11434",
            seed=42,
        )
    except Exception as e:
        pytest.skip(f"Ollama service not available: {str(e)}")


@pytest.fixture(scope="session")
def embeddings():
    """Shared fixture for Ollama embeddings"""
    return OllamaEmbeddings(model=AppConfig.OLLAMA_EMBEDDING_MODEL, base_url=AppConfig.OLLAMA_URL)


@pytest.fixture
def make_chat_request():
    """
    Factory fixture to create ChatRequest objects with default values.

    Usage:
        def test_something(make_chat_request):
            request = make_chat_request(
                content="What's my balance?",
                agent_name="base"
            )
    """

    def _make_chat_request(
        content: str,
        agent_name: str = "base",
        conversation_id: str = "test_conv",
        chain_id: str = "1",
        wallet_address: str = "0x123",
        role: str = "user",
    ) -> ChatRequest:
        return ChatRequest(
            conversation_id=conversation_id,
            prompt=ChatMessage(role=role, content=content, agentName=agent_name),
            chain_id=chain_id,
            wallet_address=wallet_address,
        )

    return _make_chat_request


# Optional: Add common test data fixtures
@pytest.fixture
def mock_wallet():
    """Fixture for a mock wallet with common test values"""
    return {"address": "0x123", "private_key": "0xabc"}
