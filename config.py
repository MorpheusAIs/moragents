
class AgentDockerConfig:
    PRICE_FETCHER_IMAGE_NAME = "morpheus/price_fetcher_agent"
    PRICE_FETCHER_DOCKERFILE = {
        "ARM64": "agents/morpheus_price_agent/agent/Dockerfile-apple",
        "x86_64": "agents/morpheus_price_agent/agent/Dockerfile"
    }
    PRICE_FETCHER_INTERNAL_PORT = 5000

