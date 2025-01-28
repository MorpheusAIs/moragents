from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Default Agent."""

    # *************
    # AGENT CONFIG
    # ------------
    # This must be defined in every agent config file
    # It is required to load the agent
    # *************

    agent_config = AgentConfig(
        path="src.services.agents.default.agent",
        class_name="DefaultAgent",
        description="Must be used for meta-queries that ask about active Morpheus agents, and also for general, simple questions",
        human_readable_name="Default General Purpose",
        command="morpheus",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = [
        {
            "name": "get_available_agents",
            "description": "Get list of all available agents and their descriptions",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "get_agent_info",
            "description": "Get detailed information about a specific agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent to get info for",
                        "required": True,
                    }
                },
            },
        },
    ]
