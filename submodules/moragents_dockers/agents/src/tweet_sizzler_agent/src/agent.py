import logging
import tweepy
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TweetSizzlerAgent:
    def __init__(self, config, llm, llm_ollama, embeddings, flask_app):
        self.llm = llm
        self.flask_app = flask_app
        self.config = config
        self.x_api_key = None
        self.current_tweet = None
        self.twitter_client = None

    def generate_tweet(self, prompt):
        logger.info(f"Generating tweet for prompt: {prompt}")
        messages = [
            {
                "role": "system",
                "content": Config.TWEET_GENERATION_PROMPT,
            },
            {"role": "user", "content": f"Generate a tweet for: {prompt}"},
        ]

        try:
            result = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=Config.LLM_MAX_TOKENS,
                temperature=Config.LLM_TEMPERATURE,
            )
            self.current_tweet = result["choices"][0]["message"]["content"]
            logger.info(f"Tweet generated successfully: {self.current_tweet}")
            return self.current_tweet
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            raise

    def post_tweet(self, request):
        data = request.get_json()
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

    def chat(self, request):
        try:
            data = request.get_json()
            logger.info(f"Received chat request: {data}")
            if "prompt" in data:
                prompt = data["prompt"]
                action = data.get("action", Config.DEFAULT_ACTION)
                logger.debug(f"Extracted prompt: {prompt}, action: {action}")

                if action == "generate":
                    logger.info(f"Generating tweet for prompt: {prompt['content']}")
                    tweet = self.generate_tweet(prompt["content"])
                    logger.info(f"Generated tweet: {tweet}")
                    return {"role": "assistant", "content": tweet}
                elif action == "post":
                    logger.info("Attempting to post tweet")
                    result, status_code = self.post_tweet(request)
                    logger.info(
                        f"Posted tweet result: {result}, status code: {status_code}"
                    )
                    return result, status_code
                else:
                    logger.error(f"Invalid action received: {action}")
                    return {"error": Config.ERROR_INVALID_ACTION}, 400
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {"error": Config.ERROR_MISSING_PARAMETERS}, 400
        except Exception as e:
            logger.exception(f"Unexpected error in chat method: {str(e)}")
            return {"Error": str(e)}, 500
