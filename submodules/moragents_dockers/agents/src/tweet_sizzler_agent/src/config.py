import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Configuration object
class Config:

    # Twitter API configuration
    TWITTER_API_VERSION = "2"
    TWEET_MAX_LENGTH = 280

    LLM_MAX_TOKENS = 280
    LLM_TEMPERATURE = 0.7

    TWEET_GENERATION_PROMPT = (
        "You are a witty and engaging tweet generator. Your task is to create spicy, "
        "attention-grabbing tweets based on the user's prompt. Keep the tweets within "
        "280 characters and make them as engaging as possible."
    )

    DEFAULT_ACTION = "generate"

    ERROR_NO_TWEET_CONTENT = "No tweet content provided"
    ERROR_TWITTER_CLIENT_NOT_INITIALIZED = (
        "Twitter client not initialized. Please set X API credentials first."
    )
    ERROR_MISSING_API_CREDENTIALS = "Missing required X API credentials"
    ERROR_INVALID_ACTION = "Invalid action"
    ERROR_MISSING_PARAMETERS = "Missing required parameters"
