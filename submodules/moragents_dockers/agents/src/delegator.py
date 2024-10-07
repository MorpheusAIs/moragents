import importlib
import logging
import json
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

# Configurable default agent
DEFAULT_AGENT = "general purpose and context-based rag agent"

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
            "Your name is Morpheus. "
            "Your primary function is to select the correct agent based on the user's input. "
            "You MUST use the 'choose_appropriate_agent' function to select an agent. "
            "Available agents and their descriptions:\n"
            f"{agent_descriptions}\n"
            "Analyze the user's input and select the most appropriate agent. "
            "Do not respond with any text other than calling the 'choose_appropriate_agent' function."
        )

        # Define the tool in the format expected by OllamaFunctions
        tools = [
            {
                "name": "choose_appropriate_agent",
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
            }
        ]

        # Initialize the AI model with the correct tool format
        model = OllamaFunctions(
            model="llama3.2:3b", format="json", temperature=0, base_url="http://host.docker.internal:11434"
        )
        model = model.bind_tools(tools=tools, function_call={"name": "choose_appropriate_agent"})

        # Create the messages for the AI model
        print("prompt", prompt)
        messages = [
            SystemMessage(content=prompt_text),
            HumanMessage(content=prompt),
        ]

        # Process the query
        try:
            result = model.invoke(messages)
            logger.info(f"Model result: {result}")

            # Parse the result to extract the chosen agent
            if hasattr(result, 'additional_kwargs') and 'function_call' in result.additional_kwargs:
                function_call = result.additional_kwargs['function_call']
                if function_call['name'] == 'choose_appropriate_agent':
                    next_agent = json.loads(function_call['arguments'])['next']
                    return {"next": next_agent}
            
            logger.warning("Unexpected response format, defaulting to general purpose agent")
            return {"next": DEFAULT_AGENT}

        except Exception as e:
            logger.error(f"Error during model invocation: {e}")
            return {"next": DEFAULT_AGENT}

    def delegate_chat(self, agent_name, request):
        logger.info(f"Attempting to delegate chat to agent: {agent_name}")
        agent = self.agents.get(agent_name)
        if agent:
            logger.info(f"Successfully found agent: {agent_name}")
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
