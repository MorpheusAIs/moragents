import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:
    # Model configuration
    MODEL_NAME = "bartowski/functionary-small-v3.2-GGUF"
    MODEL_REVISION = "functionary-small-v3.2-Q6_K_L.gguf"
    MODEL_PATH = "model/" + MODEL_REVISION
    DOWNLOAD_DIR = "model"
