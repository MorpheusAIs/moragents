import logging

from src.models.messages import ChatRequest
from src.stores import agent_manager_instance

logger = logging.getLogger(__name__)


class DefaultAgent:
    def __init__(self, config, llm, embeddings):
        self.config = config
        self.llm = llm

    def chat(self, request: ChatRequest):
        try:
            data = request.dict()
            if "prompt" in data:
                prompt = data["prompt"]["content"]
                # Get currently selected agents for system prompt
                available_agents = agent_manager_instance.get_available_agents()
                selected_agent_names = agent_manager_instance.get_selected_agents()

                # Build list of human readable names for selected agents
                selected_agents_info = []
                for agent in available_agents:
                    if agent["name"] in selected_agent_names and agent["name"] != "default agent":
                        human_name = agent.get("human_readable_name", agent["name"])
                        selected_agents_info.append(f"- {human_name}: {agent['description']}")

                system_prompt = (
                    "You are a helpful assistant that can engage in general conversation and provide information about Morpheus agents when specifically asked.\n"
                    "For general questions, respond naturally without mentioning Morpheus or its agents.\n"
                    "Only when explicitly asked about Morpheus or its capabilities, use this list of available agents:\n"
                    f"{chr(10).join(selected_agents_info)}\n"
                    "Remember: Only mention Morpheus agents if directly asked about them. Otherwise, simply answer questions normally as a helpful assistant."
                )

                messages = [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ]

                result = self.llm.invoke(messages)
                return {"role": "assistant", "content": result.content.strip()}
            else:
                return {"error": "Missing required parameters"}, 400
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return {"Error": str(e)}, 500
