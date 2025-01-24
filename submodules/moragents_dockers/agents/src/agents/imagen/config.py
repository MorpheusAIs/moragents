from src.models.service.agent_config import AgentConfig


class Config:
    """Configuration for Image Generation Agent."""

    # *************
    # AGENT CONFIG
    # *************

    agent_config = AgentConfig(
        path="src.agents.imagen.agent",
        class_name="ImagenAgent",
        description="Must only be used for image generation tasks. Use when the query explicitly mentions generating or creating an image.",
        human_readable_name="Image Generator",
        command="imagen",
        upload_required=False,
    )

    # *************
    # TOOLS CONFIG
    # *************

    tools = []  # No tools needed for image generation

    # *************
    # API CONFIG
    # *************

    CHROME_BINARY = "/usr/bin/chromium"
    CHROME_DRIVER = "/usr/bin/chromedriver"
    FLUX_AI_URL = "https://fluxai.pro/fast-flux"
    PAGE_LOAD_TIMEOUT = 30  # seconds
    ELEMENT_WAIT_TIMEOUT = 30  # seconds
