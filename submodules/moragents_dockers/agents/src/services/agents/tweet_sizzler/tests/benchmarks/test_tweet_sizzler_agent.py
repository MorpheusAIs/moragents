import pytest
from unittest.mock import patch, Mock

from src.services.agents.tweet_sizzler.agent import TweetSizzlerAgent
from src.models.service.chat_models import AgentResponse
from src.stores import key_manager_instance


@pytest.fixture
def tweet_sizzler_agent(llm, embeddings):
    config = {"name": "tweet_sizzler", "description": "Agent for generating and posting tweets"}
    return TweetSizzlerAgent(config, llm, embeddings)


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_generate_tweet_success(tweet_sizzler_agent, make_chat_request):
    request = make_chat_request(content="Write a tweet about AI")

    with patch.object(tweet_sizzler_agent.llm, "invoke") as mock_invoke:
        mock_invoke.return_value.content = "AI is transforming our world! #AI #Technology"

        response = await tweet_sizzler_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "success"
        assert "AI is transforming" in response.content


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_post_tweet_success(tweet_sizzler_agent, make_chat_request):
    request = make_chat_request(content="Post this tweet: Test tweet #testing")

    mock_tweet_response = Mock()
    mock_tweet_response.data = {"text": "Test tweet #testing", "id": "123456789"}

    with patch("tweepy.Client") as mock_client:
        mock_client.return_value.create_tweet.return_value = mock_tweet_response
        with patch.object(key_manager_instance, "has_x_keys", return_value=True):
            with patch.object(key_manager_instance, "get_x_keys") as mock_get_keys:
                mock_get_keys.return_value = Mock(
                    api_key="test_key",
                    api_secret="test_secret",
                    access_token="test_token",
                    access_token_secret="test_token_secret",
                    bearer_token="test_bearer",
                )

                response = await tweet_sizzler_agent._process_request(request)

                assert isinstance(response, AgentResponse)
                assert response.response_type.value == "success"
                assert "Tweet posted successfully" in response.content
                assert response.metadata["tweet_id"] == "123456789"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_post_tweet_missing_credentials(tweet_sizzler_agent, make_chat_request):
    request = make_chat_request(content="Post this tweet: Test tweet")

    with patch.object(key_manager_instance, "has_x_keys", return_value=False):
        response = await tweet_sizzler_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "error"
        assert "API credentials" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_tweet_generation_error(tweet_sizzler_agent, make_chat_request):
    request = make_chat_request(content="Write a tweet")

    with patch.object(tweet_sizzler_agent.llm, "invoke", side_effect=Exception("LLM Error")):
        response = await tweet_sizzler_agent._process_request(request)

        assert isinstance(response, AgentResponse)
        assert response.response_type.value == "error"
        assert "LLM Error" in response.error_message


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_execute_tool_not_implemented(tweet_sizzler_agent):
    response = await tweet_sizzler_agent._execute_tool("any_tool", {})

    assert isinstance(response, AgentResponse)
    assert response.response_type.value == "error"
    assert "does not support tool execution" in response.error_message
