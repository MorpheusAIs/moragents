# Configuration object
class Config:
    ALCHEMY_API_KEY = "NRQxqrVyo02u4NK55FNKjJep_xEm6n7b"
    VERBOSE = True
    LLM_CONFIG = lambda: {
        "cache_seed": None,
        "config_list": [
            {
                "model": "gpt-4o",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
            }
        ],
    }
