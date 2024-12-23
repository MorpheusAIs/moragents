import logging
from typing import Dict, List
from src.models.messages import ChatMessage, Conversation

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.default_message = ChatMessage(
            role="assistant",
            agentName="Morpheus AI",
            content="""This highly experimental chatbot is not intended for making important decisions. Its
                        responses are generated using AI models and may not always be accurate.
                        By using this chatbot, you acknowledge that you use it at your own discretion
                        and assume all risks associated with its limitations and potential errors.""",
        )

    def _get_or_create_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(messages=[self.default_message], has_uploaded_file=False)
        return self.conversations[conversation_id]

    def add_message(self, message: Dict[str, str], conversation_id: str):
        conversation = self._get_or_create_conversation(conversation_id)
        chat_message = ChatMessage(**message)
        conversation.messages.append(chat_message)
        logger.info(f"Added message to conversation {conversation_id}: {message}")

    def get_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        conversation = self._get_or_create_conversation(conversation_id)
        return [msg.dict() for msg in conversation.messages]

    def set_uploaded_file(self, has_file: bool, conversation_id: str):
        conversation = self._get_or_create_conversation(conversation_id)
        conversation.has_uploaded_file = has_file
        logger.info(f"Set uploaded file status to {has_file} for conversation {conversation_id}")

    def get_uploaded_file_status(self, conversation_id: str) -> bool:
        conversation = self._get_or_create_conversation(conversation_id)
        return conversation.has_uploaded_file

    def clear_messages(self, conversation_id: str):
        conversation = self._get_or_create_conversation(conversation_id)
        conversation.messages = [self.default_message]  # Keep the initial message
        logger.info(f"Cleared message history for conversation {conversation_id}")

    def get_last_message(self, conversation_id: str) -> Dict[str, str]:
        conversation = self._get_or_create_conversation(conversation_id)
        return conversation.messages[-1].dict() if conversation.messages else {}

    def add_response(self, response: Dict[str, str], agent_name: str, conversation_id: str):
        response_with_agent = response.copy()
        response_with_agent["agentName"] = agent_name
        chat_message = ChatMessage(**response_with_agent)
        self.add_message(chat_message.message, conversation_id)
        logger.info(f"Added response from agent {agent_name} to conversation {conversation_id}: {response_with_agent}")

    def get_chat_history(self, conversation_id: str) -> str:
        conversation = self._get_or_create_conversation(conversation_id)
        return "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])

    def get_all_conversation_ids(self) -> List[str]:
        """Get a list of all conversation IDs"""
        return list(self.conversations.keys())

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation by ID"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")

    def create_conversation(self, conversation_id: str) -> Dict:
        """Create a new conversation with the given ID"""
        conversation = self._get_or_create_conversation(conversation_id)
        return conversation.dict()


# Create an instance to act as a singleton store
chat_manager_instance = ChatManager()
