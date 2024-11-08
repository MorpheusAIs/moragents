import logging

import tweepy
from src.agents.tweet_sizzler.config import Config
from src.models.messages import ChatRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TweetSizzlerAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self.x_api_key = None
        self.last_prompt_content = None
        self.twitter_client = None

    def generate_tweet(self, prompt_content=None):
        # State management for tweet regeneration purposes
        if prompt_content is not None:
            self.last_prompt_content = prompt_content
        elif self.last_prompt_content is None:
            logger.warning("No prompt content available for tweet generation")
            return "Tweet generation failed. Please provide a prompt."
        else:
            prompt_content = self.last_prompt_content

        logger.info(f"Generating tweet for prompt_content: {prompt_content}")
        messages = [
            {
                "role": "system",
                "content": Config.TWEET_GENERATION_PROMPT,
            },
            {"role": "user", "content": f"Generate a tweet for: {prompt_content}"},
        ]

        try:
            result = self.llm.invoke(messages)
            logger.info(f"Received response from LLM: {result}")
            tweet = result.content.strip()
            tweet = " ".join(tweet.split())

            # Remove any dictionary-like formatting, if present
            if tweet.startswith("{") and tweet.endswith("}"):
                tweet = tweet.strip("{}").split(":", 1)[-1].strip().strip('"')

            logger.info(f"Tweet generated successfully: {tweet}")
            return tweet
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            raise

    async def post_tweet(self, request):
        logger.info(f"Received tweet request: {request}")
        data = await request.json()
        logger.info(f"Received tweet data: {data}")

        tweet_content = data.get("post_content")
        logger.info(f"Received tweet content: {tweet_content}")

        if not tweet_content:
            logger.warning("Attempted to post tweet without providing content")
            return {"error": Config.ERROR_NO_TWEET_CONTENT}, 400

        required_keys = [
            "api_key",
            "api_secret",
            "access_token",
            "access_token_secret",
            "bearer_token",
        ]
        if not all(key in data for key in required_keys):
            logger.warning("Missing required API credentials")
            return {"error": Config.ERROR_MISSING_API_CREDENTIALS}, 400

        try:
            client = tweepy.Client(
                consumer_key=data["api_key"],
                consumer_secret=data["api_secret"],
                access_token=data["access_token"],
                access_token_secret=data["access_token_secret"],
                bearer_token=data["bearer_token"],
            )

            # Post tweet
            response = client.create_tweet(text=tweet_content)
            logger.info(f"Tweet posted successfully: {response}")
            return {
                "success": "Tweet posted successfully",
                "tweet": response.data["text"],
                "tweet_id": response.data["id"],
            }, 200
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {"error": f"Failed to post tweet: {str(e)}"}, 500

    def set_x_api_key(self, request):
        data = request.get_json()
        required_keys = [
            "api_key",
            "api_secret",
            "access_token",
            "access_token_secret",
            "bearer_token",
        ]

        if not all(key in data for key in required_keys):
            logger.warning("Missing required API credentials")
            return {"error": Config.ERROR_MISSING_API_CREDENTIALS}, 400

        # Save these credentials to local storage
        for key in required_keys:
            self.flask_app.config[key] = data[key]

        return {"success": "API credentials saved successfully"}, 200

    def chat(self, chat_request: ChatRequest):
        try:
            prompt = chat_request.prompt.dict()
            logger.info(f"Received chat request: {prompt}")

            action = prompt.get("action", Config.DEFAULT_ACTION)
            logger.debug(f"Extracted prompt content: {prompt['content']}, action: {action}")

            if action == "generate":
                logger.info(f"Generating tweet for prompt: {prompt['content']}")
                tweet = self.generate_tweet(prompt["content"])
                logger.info(f"Generated tweet: {tweet}")
                return {"role": "assistant", "content": tweet}
            elif action == "post":
                logger.info("Attempting to post tweet")
                result, status_code = self.post_tweet(chat_request)
                logger.info(f"Posted tweet result: {result}, status code: {status_code}")
                if isinstance(result, dict) and "error" in result:
                    return result, status_code
                return {
                    "role": "assistant",
                    "content": f"Tweet posted successfully: {result.get('tweet', '')}",
                }, status_code
            else:
                logger.error(f"Invalid action received: {action}")
                return {"role": "assistant", "content": Config.ERROR_INVALID_ACTION}

        except Exception as e:
            logger.exception(f"Unexpected error in chat method: {str(e)}")
            return {"role": "assistant", "content": f"Error: {str(e)}"}
