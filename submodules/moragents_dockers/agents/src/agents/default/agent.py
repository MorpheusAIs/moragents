import logging

from src.models.messages import ChatRequest
from src.stores import agent_manager

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
                available_agents = agent_manager.get_available_agents()
                selected_agent_names = agent_manager.get_selected_agents()

                # Build list of human readable names for selected agents
                selected_agents_info = []
                for agent in available_agents:
                    if agent["name"] in selected_agent_names:
                        human_name = agent.get("human_readable_name", agent["name"])
                        selected_agents_info.append(
                            f"- {human_name}: {agent['description']}"
                        )

                system_prompt = f"""
                You are a helpful assistant. Use the context provided to respond to the user's question.
                The following Morpheus agents are currently available if the user asks about them:
                {chr(10).join(selected_agents_info)}"""

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
