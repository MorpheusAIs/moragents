class AgentManager:
    def __init__(self):
        self.active_agent = None

    def get_active_agent(self):
        return self.active_agent

    def set_active_agent(self, agent_name):
        self.active_agent = agent_name

    def clear_active_agent(self):
        self.active_agent = None
