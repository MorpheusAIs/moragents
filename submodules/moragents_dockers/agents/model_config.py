import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:
    # Model configuration
    MODEL_NAME = "meetkai/functionary-small-v3.2-GGUF"
    MODEL_REVISION = "functionary-small-v3.2.Q4_0.gguf"
    MODEL_PATH = "model/" + MODEL_REVISION
    DOWNLOAD_DIR = "model"
