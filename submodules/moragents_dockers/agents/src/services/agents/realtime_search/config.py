from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Realtime Search Agent."""

    # *************
    # AGENT CONFIG
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.realtime_search.agent",
        class_name="RealtimeSearchAgent",
        description="Performs real-time web searches to find current information. Should be used whenever the user refers to something recent or time-sensitive.",
        human_readable_name="Web Search Assistant",
        command="search",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "perform_web_search",
            "description": "Perform a web search and return relevant results",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "The search term to look up",
                    }
                },
                "required": ["search_term"],
            },
        }
    ]

    # *************
    # SEARCH CONFIG
    # *************

    # Web scraping configuration
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    MAX_SEARCH_RESULTS = 5
    SEARCH_URL = "https://www.google.com/search?q={}"

    # Chrome options for headless browsing
    CHROME_OPTIONS = ["--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]

    # LLM configuration for answer synthesis
    SYNTHESIS_SYSTEM_PROMPT = "Synthesize information from web search results into a clear, direct answer."
    MAX_TOKENS = 150
    TEMPERATURE = 0.3
