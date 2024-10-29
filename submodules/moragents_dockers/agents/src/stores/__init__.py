from src.stores.agent_manager import AgentManager
from src.stores.chat_manager import ChatManager
from src.config import Config

agent_manager = AgentManager(Config.AGENTS_CONFIG)
chat_manager = ChatManager()
