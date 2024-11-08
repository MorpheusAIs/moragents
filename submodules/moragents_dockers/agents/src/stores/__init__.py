from src.config import Config
from src.stores.agent_manager import AgentManager
from src.stores.chat_manager import ChatManager

agent_manager = AgentManager(Config.AGENTS_CONFIG)
chat_manager = ChatManager()
