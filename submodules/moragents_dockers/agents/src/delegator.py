import importlib
import logging
import json

logger = logging.getLogger(__name__)


class Delegator:
    def __init__(self, config, llm, llm_ollama, embeddings, flask_app):
        self.llm = llm
        self.flask_app = flask_app
        self.llm_ollama = llm_ollama
        self.embeddings = embeddings
        self.config = config
        self.agents = self.load_agents(config)
        logger.info("Delegator initialized with %d agents", len(self.agents))

    def load_agents(self, config):
        agents = {}
        for agent_info in config["agents"]:
            try:
                module = importlib.import_module(agent_info["path"])
                agent_class = getattr(module, agent_info["class"])
                agent_instance = agent_class(
                    agent_info,
                    self.llm,
                    self.llm_ollama,
                    self.embeddings,
                    self.flask_app,
                )
                agents[agent_info["name"]] = agent_instance
                logger.info("Loaded agent: %s", agent_info["name"])
            except Exception as e:
                logger.error("Failed to load agent %s: %s", agent_info["name"], str(e))
        return agents

    def get_delegator_response(self, prompt, upload_state):
        available_agents = [
            agent_info["name"]
            for agent_info in self.config["agents"]
            if not (agent_info["upload_required"] and not upload_state)
        ]
        agent_descriptions = "\n".join(
            f"- {agent_info['name']}: {agent_info['description']}"
            for agent_info in self.config["agents"]
            if agent_info["name"] in available_agents
        )

        prompt_text = (
            "### Instruction: Your name is Morpheus. "
            "Your primary function is to select the correct agent based on the user's input. "
            "You MUST use the 'route' function to select an agent. "
            "Available agents and their descriptions:\n"
            f"{agent_descriptions}\n"
            "Analyze the user's input and select the most appropriate agent. "
            "Do not respond with any text other than calling the 'route' function. "
            "###"
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "route",
                    "description": "Choose which agent to run next",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "next": {
                                "type": "string",
                                "enum": available_agents,
                                "description": "The name of the next agent to run",
                            }
                        },
                        "required": ["next"],
                    },
                },
            }
        ]

        message_list = [
            {"role": "system", "content": prompt_text},
            prompt,
            {
                "role": "system",
                "content": "Remember, you must use the 'route' function to select an agent.",
            },
        ]

        logger.info("Sending prompt to LLM: %s", prompt)
        result = self.llm.create_chat_completion(
            messages=message_list,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "route"}},
            temperature=0.3,
        )
        logger.info("Received response from LLM: %s", result)

        response = result["choices"][0]["message"]
        if "tool_calls" in response and response["tool_calls"]:
            try:
                function_args = json.loads(
                    response["tool_calls"][0]["function"]["arguments"]
                )
                return {"next": function_args["next"]}
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing function call: {e}")
                return {"next": available_agents[0]}
        else:
            logger.warning("No tool calls in LLM response, defaulting to first agent")
            return {"next": available_agents[0]}

    def delegate_chat(self, agent_name, request):
        logger.info(f"Attempting to delegate chat to agent: {agent_name}")
        agent = self.agents.get(agent_name)
        if agent:
            logger.info(f"Successfully found agent: {agent_name}")
            logger.info(f"Request data for {agent_name}: {request}")
            try:
                result = agent.chat(request)
                logger.info(f"Chat delegation to {agent_name} completed successfully")
                logger.info(f"Response from {agent_name}: {result}")
                return agent_name, result
            except Exception as e:
                logger.error(f"Error during chat delegation to {agent_name}: {str(e)}")
                return {"error": f"Chat delegation to {agent_name} failed"}, 500
        else:
            logger.warning(f"Attempted to delegate to non-existent agent: {agent_name}")
            return {"error": f"No such agent registered: {agent_name}"}, 400

    def delegate_route(self, agent_name, request, method_name):
        agent = self.agents.get(agent_name)
        if agent:
            if hasattr(agent, method_name):
                logger.info("Delegating %s to agent: %s", method_name, agent_name)
                method = getattr(agent, method_name)
                return method(request)
            else:
                logger.warning(
                    "Method %s not found in agent %s", method_name, agent_name
                )
                return {
                    "error": f"No such method '{method_name}' in agent '{agent_name}'"
                }, 400
        logger.warning("Attempted to delegate to non-existent agent: %s", agent_name)
        return {"error": "No such agent registered"}, 400
