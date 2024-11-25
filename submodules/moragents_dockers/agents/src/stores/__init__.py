from src.config import Config
from src.stores.agent_manager import AgentManager
from src.stores.chat_manager import ChatManager
from src.stores.key_manager import KeyManager

agent_manager = AgentManager(Config.AGENTS_CONFIG)
chat_manager = ChatManager()
key_manager = KeyManager()
