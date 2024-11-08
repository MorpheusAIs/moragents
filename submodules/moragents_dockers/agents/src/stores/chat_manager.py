import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self):
        self.has_uploaded_file = False
        self.messages: List[Dict[str, str]] = [
            {
                "role": "assistant",
                "content": """This highly experimental chatbot is not intended for making important decisions,
                            and its responses are generated based on incomplete data and algorithms that may evolve rapidly.
                            By using this chatbot, you acknowledge that you use it at your own discretion
                            and assume all risks associated with its limitations and potential errors.""",
            }
        ]

    def add_message(self, message: Dict[str, str]):
        self.messages.append(message)
        logger.info(f"Added message: {message}")

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def set_uploaded_file(self, has_file: bool):
        self.has_uploaded_file = has_file
        logger.info(f"Set uploaded file status to: {has_file}")

    def get_uploaded_file_status(self) -> bool:
        return self.has_uploaded_file

    def clear_messages(self):
        self.messages = [self.messages[0]]  # Keep the initial message
        logger.info("Cleared message history")

    def get_last_message(self) -> Dict[str, str]:
        return self.messages[-1] if self.messages else {}

    def add_response(self, response: Dict[str, str], agent_name: str):
        response_with_agent = response.copy()
        response_with_agent["agentName"] = agent_name
        self.add_message(response_with_agent)
        logger.info(f"Added response from agent {agent_name}: {response_with_agent}")

    def get_chat_history(self) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.messages])
