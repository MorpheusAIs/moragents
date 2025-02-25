import logging
from typing import Dict, Any, Optional
import tweepy
from langchain.schema import HumanMessage, SystemMessage
from src.models.service.chat_models import ChatRequest, AgentResponse
from src.models.service.agent_core import AgentCore
from src.stores import key_manager_instance, chat_manager_instance
from .config import Config

logger = logging.getLogger(__name__)


class TweetSizzlerAgent(AgentCore):
    """Agent for generating and posting tweets."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        super().__init__(config, llm, embeddings)
        self.tools_provided = Config.tools
        self.tool_bound_llm = self.llm.bind_tools(self.tools_provided)

    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """Process the validated chat request for tweet generation and posting."""
        try:
            messages = [
                SystemMessage(content=Config.TWEET_GENERATION_PROMPT),
                HumanMessage(content=request.prompt.content),
            ]

            # Add chat history if available
            chat_history = chat_manager_instance.get_chat_history(request.conversation_id)
            if chat_history:
                messages.append(HumanMessage(content=f"Previous conversation context: {chat_history}"))

            result = self.tool_bound_llm.invoke(messages)
            return await self._handle_llm_response(result)

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute the appropriate tool based on function name."""
        try:
            if func_name == "generate_tweet":
                content = args.get("content")
                if not content:
                    return AgentResponse.error(error_message="Please provide content for tweet generation")

                result = await self._generate_tweet(content)
                return AgentResponse.success(content=result)

            elif func_name == "post_tweet":
                if not key_manager_instance.has_x_keys():
                    return AgentResponse.error(error_message=Config.ERROR_MISSING_API_CREDENTIALS)

                tweet_content = args.get("tweet_content")
                if not tweet_content:
                    return AgentResponse.error(error_message="Please provide content for posting the tweet")

                result = await self._post_tweet(tweet_content)
                if "error" in result:
                    return AgentResponse.error(error_message=result["error"])

                return AgentResponse.success(
                    content=f"Tweet posted successfully: {result['tweet']}", metadata={"tweet_id": result["tweet_id"]}
                )

            else:
                return AgentResponse.error(error_message=f"Unknown tool function: {func_name}")

        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message=str(e))

    async def _generate_tweet(self, content: str) -> str:
        """Generate tweet content based on prompt and context."""
        result = self.llm.invoke(
            [
                SystemMessage(content=Config.TWEET_GENERATION_PROMPT),
                HumanMessage(content=f"Generate a tweet for: {content}"),
            ]
        )

        tweet = result.content.strip()
        tweet = " ".join(tweet.split())  # Normalize whitespace

        # Remove any dictionary-like formatting
        if tweet.startswith("{") and tweet.endswith("}"):
            tweet = tweet.strip("{}").split(":", 1)[-1].strip().strip('"')

        logger.info(f"Tweet generated successfully: {tweet}")
        return tweet

    async def _post_tweet(self, tweet_content: str) -> Dict[str, Any]:
        """Post tweet using stored X API credentials."""
        try:
            x_keys = key_manager_instance.get_x_keys()
            client = tweepy.Client(
                consumer_key=x_keys.api_key,
                consumer_secret=x_keys.api_secret,
                access_token=x_keys.access_token,
                access_token_secret=x_keys.access_token_secret,
                bearer_token=x_keys.bearer_token,
            )

            response = client.create_tweet(text=tweet_content)
            logger.info(f"Tweet posted successfully: {response}")

            return {"tweet": response.data["text"], "tweet_id": response.data["id"]}
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {"error": f"Failed to post tweet: {str(e)}"}
