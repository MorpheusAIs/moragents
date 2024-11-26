from src.config import Config
from src.stores.agent_manager import AgentManager
from src.stores.chat_manager import ChatManager
from src.stores.key_manager import KeyManager
from src.stores.wallet_manager import WalletManager

agent_manager = AgentManager(Config.AGENTS_CONFIG)
chat_manager = ChatManager()
key_manager = KeyManager()
wallet_manager = WalletManager()
