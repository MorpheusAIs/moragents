import importlib


class Delegator:
    def __init__(self, config, llm, llm_ollama, embeddings, flask_app):
        self.llm = llm
        self.flask_app = flask_app
        self.llm_ollama = llm_ollama
        self.embeddings = embeddings
        self.agents = self.load_agents(config)
        self.config = config

    def load_agents(self, config):
        agents = {}
        for agent_info in config['agents']:
            module = importlib.import_module(agent_info['path'])
            agent_class = getattr(module, agent_info['class'])
            agent_instance = agent_class(
                agent_info, self.llm, self.llm_ollama, self.embeddings, self.flask_app
            )
            agents[agent_info['name']] = agent_instance
        return agents

    def get_delegator_response(self, prompt, upload_state):
        available_agents = []
        text = ""
        for agent_info in self.config['agents']:
            if agent_info["upload_required"] and not upload_state:
                continue
            available_agents.append(agent_info["name"])
            text += f", {agent_info['description']}"
        pre = "### Instruction: Your name is Morpheus. Your primary function is to select the correct agent."
        post = "###"
        prompt_text = f"{pre}{text}{post}"
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "route",
                    "description": "choose which agent to run next",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "next": {
                                "title": "Next",
                                "anyOf": [
                                    {"enum": available_agents},
                                ],
                            }
                        },
                        "required": ["next"],
                    },
                }
            }
        ]
        message_list = [{"role": "system", "content": prompt_text}] + [prompt]
        result = self.llm.create_chat_completion(
            messages=message_list,
            tools=tools,
            tool_choice="auto",
            temperature=0.3
        )
        return result["choices"][0]["message"]

    def delegate_chat(self, agent_name, request):
        agent = self.agents.get(agent_name)
        if agent:
            return agent.chat(request)
        return {"error": "No such agent registered"}

    def delegate_route(self, agent_name, request, method_name):
        agent = self.agents.get(agent_name)
        if agent:
            if hasattr(agent, method_name):
                method = getattr(agent, method_name)
                return method(request)
            else:
                return {"error": f"No such method '{method_name}' in agent '{agent_name}'"}, 400
        return {"error": "No such agent registered"}, 400
