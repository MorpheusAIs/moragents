class AgentManager:
    def __init__(self):
        self.active_agents = {}

    def get_active_agent(self, user_id):
        return self.active_agents.get(user_id)

    def set_active_agent(self, user_id, agent_name):
        self.active_agents[user_id] = agent_name

    def clear_active_agent(self, user_id):
        self.active_agents.pop(user_id, None)
