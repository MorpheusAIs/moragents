import json
import requests
import logging
from flask import jsonify

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
        logger.info("TweetSizzlerAgent initialized")

    def generate_tweet(self, prompt):
        logger.info(f"Generating tweet for prompt: {prompt}")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a witty and engaging tweet generator. Your task is to create spicy, "
                    "attention-grabbing tweets based on the user's prompt. Keep the tweets within "
                    "280 characters and make them as engaging as possible."
                ),
            },
            {"role": "user", "content": f"Generate a spicy tweet about: {prompt}"},
        ]

        try:
            result = self.llm.create_chat_completion(
                messages=messages, max_tokens=280, temperature=0.7
            )
            self.current_tweet = result["choices"][0]["message"]["content"]
            logger.info(f"Tweet generated successfully: {self.current_tweet}")
            return self.current_tweet
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            raise

    def post_tweet(self):
        if not self.current_tweet:
            logger.warning("Attempted to post tweet without generating one first")
            return {"error": "No tweet generated yet"}, 400

        if not self.x_api_key:
            logger.warning("Attempted to post tweet without setting X API key")
            return {"error": "X API key not set", "action": "request_api_key"}, 400

        try:
            tweet_data = self._make_x_api_call(self.current_tweet)
            logger.info(f"Tweet posted successfully: {tweet_data}")
            return {
                "success": "Tweet posted successfully",
                "tweet": tweet_data["data"]["text"],
                "tweet_id": tweet_data["data"]["id"],
            }, 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {"error": f"Failed to post tweet: {str(e)}"}, 500

    def _make_x_api_call(self, tweet_text):
        url = "https://api.x.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {self.x_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"text": tweet_text}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def set_x_api_key(self, api_key):
        self.x_api_key = api_key
        logger.info("X API key set successfully")
        return {"success": "X API key set successfully"}, 200

    def chat(self, request):
        try:
            data = request.get_json()
            logger.info(f"Received chat request: {data}")
            if "prompt" in data:
                prompt = data["prompt"]
                action = data.get("action", "generate")
                logger.debug(f"Extracted prompt: {prompt}, action: {action}")

                if action == "generate":
                    logger.info(f"Generating tweet for prompt: {prompt['content']}")
                    tweet = self.generate_tweet(prompt["content"])
                    logger.info(f"Generated tweet: {tweet}")
                    return {"role": "assistant", "content": tweet}
                elif action == "post":
                    logger.info("Attempting to post tweet")
                    result, status_code = self.post_tweet()
                    logger.info(
                        f"Posted tweet result: {result}, status code: {status_code}"
                    )
                    return result, status_code
                elif action == "set_api_key":
                    logger.info("Attempting to set API key")
                    result, status_code = self.set_x_api_key(prompt["content"])
                    logger.info(
                        f"Set API key result: {result}, status code: {status_code}"
                    )
                    return result, status_code
                else:
                    logger.error(f"Invalid action received: {action}")
                    return {"error": "Invalid action"}, 400
            else:
                logger.error("Missing 'prompt' in chat request data")
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.exception(f"Unexpected error in chat method: {str(e)}")
            return {"Error": str(e)}, 500
