# Configuration object
class Config:
    ALCHEMY_API_KEY = "NRQxqrVyo02u4NK55FNKjJep_xEm6n7b"
    VERBOSE = True
    LLM_CONFIG = lambda: {
        "model_client_cls": "LlamaClient",
        "model": "meetkai/functionary-small-v2.4-GGUF"
    }
