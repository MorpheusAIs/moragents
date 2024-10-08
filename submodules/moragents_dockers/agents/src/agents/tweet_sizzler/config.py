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
        "attention-grabbing tweets based on the user's prompt. It is CRUCIAL that you "
        "keep the tweets strictly under 280 characters - this is a hard limit. Make the "
        "tweets as engaging as possible while adhering to this character limit. Do not "
        "surround your tweet with quotes or any other formatting. Do not preface it with "
        "any text like 'here is your tweet'. Simply generate and output the tweet, ensuring "
        "it is less than 280 characters long. Use newlines sparingly. Do not surrounded with "
        "quotes or braces. Do not use any other formatting."
    )

    DEFAULT_ACTION = "generate"

    ERROR_NO_TWEET_CONTENT = "No tweet content provided"
    ERROR_TWITTER_CLIENT_NOT_INITIALIZED = (
        "Twitter client not initialized. Please set X API credentials first."
    )
    ERROR_MISSING_API_CREDENTIALS = "Missing required X API credentials"
    ERROR_INVALID_ACTION = "Invalid action"
    ERROR_MISSING_PARAMETERS = "Missing required parameters"
