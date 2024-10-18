import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)


# Configuration object
class Config:
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    MAX_LENGTH = 16 * 1024 * 1024
