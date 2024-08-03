import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Configuration object
class Config:
    # Model configuration
    MODEL_NAME = "meetkai/functionary-small-v2.4-GGUF"
    MODEL_REVISION = "functionary-small-v2.4.Q4_0.gguf"
    MODEL_PATH = "model/"+MODEL_REVISION
    DOWNLOAD_DIR = "model"
    OLLAMA_URL = "http://host.docker.internal:11434"
    MAX_UPLOAD_LENGTH = 16 * 1024 * 1024
    DELEGATOR_CONFIG = {
            "agents": [
            {
                "path": "rag_agent.src.agent",
                "class": "RagAgent",
                "description": "If the prompt is not a greeting or does not need the other agents always call rag agent.if the prompt requires a background knowledge or context call rag agent, if the question is not related to crypto call rag agent, if the prompt is a question that needs context call rag agent",
                "name": "rag agent",
                "upload_required": True
            },
            {
                "path": "data_agent.src.agent",
                "class": "DataAgent",
                "description": "if the prompt is a question like (price, market cap, fdv) of crypto currencies choose crypto data agent",
                "name": "crypto data agent",
                "upload_required": False
            },
            {
                "path": "swap_agent.src.agent",
                "class": "SwapAgent",
                "description": "if the prompt is related with swapping crypto currencies choose crypto swap agent. like if it is swap 4 eth or swap 4 eth to usdc choose crypto swap agent and if the query is about swapping crypto currencies always choose crypto swap agent",
                "name": "crypto swap agent",
                "upload_required": False
            }
            ]
        }
  
