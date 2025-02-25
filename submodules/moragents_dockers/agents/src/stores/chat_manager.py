import logging
import time
from typing import Dict, List, Optional
from src.models.service.chat_models import ChatMessage, Conversation, AgentResponse

logger = logging.getLogger(__name__)


class ChatManager:
    """
    Manages chat conversations and message history.

    This class provides functionality to:
    - Create and manage multiple conversations identified by unique IDs
    - Add/retrieve messages and responses within conversations
    - Track file upload status per conversation
    - Clear conversation history
    - Get chat history in different formats
    - Delete conversations

    Each conversation starts with a default disclaimer message about the experimental nature
    of the chatbot.

    Attributes:
        conversations (Dict[str, Conversation]): Dictionary mapping conversation IDs to Conversation objects
        default_message (ChatMessage): Default disclaimer message added to new conversations

    Example:
        >>> chat_manager = ChatManager()
        >>> chat_manager.add_message({"role": "user", "content": "Hello"}, "conv1")
        >>> messages = chat_manager.get_messages("conv1")
    """

    def __init__(self) -> None:
        self.conversations: Dict[str, Conversation] = {}
        self.default_message = ChatMessage(
            role="assistant",
            agentName="Morpheus AI",
            content="""This highly experimental chatbot is not intended for making important decisions. Its
                        responses are generated using AI models and may not always be accurate.
                        By using this chatbot, you acknowledge that you use it at your own discretion
                        and assume all risks associated with its limitations and potential errors.""",
            metadata={},
            requires_action=False,
        )

        # Initialize with default conversation
        self.conversations["default"] = Conversation(messages=[self.default_message], has_uploaded_file=False)

    def _get_conversation_id(self, conversation_id: Optional[str] = None) -> str:
        """Helper method to get conversation ID, defaulting to 'default' if None provided"""
        return conversation_id or "default"

    def get_messages(self, conversation_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get all messages for a specific conversation.

        Args:
            conversation_id (str, optional): Unique identifier for the conversation. Defaults to "default"

        Returns:
            List[Dict[str, str]]: List of messages as dictionaries
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        return [msg.dict() for msg in conversation.messages]

    def add_message(self, message: Dict[str, str], conversation_id: Optional[str] = None):
        """
        Add a new message to a conversation.

        Args:
            message (Dict[str, str]): Message to add
            conversation_id (str, optional): Conversation to add message to. Defaults to "default"
        """
        conversation_id = self._get_conversation_id(conversation_id)
        conversation = self._get_or_create_conversation(conversation_id)
        chat_message = ChatMessage(**message)
        if "timestamp" not in message:
            chat_message.timestamp = time.time()
        conversation.messages.append(chat_message)
        logger.info(f"Added message to conversation {conversation_id}: {chat_message.content}")

    def add_response(self, response: Dict[str, str], agent_name: str, conversation_id: Optional[str] = None):
        """
        Add an agent's response to a conversation.

        Args:
            response (Dict[str, str]): Response content
            agent_name (str): Name of the responding agent
            conversation_id (str, optional): Conversation to add response to. Defaults to "default"
        """
        # Convert the dictionary to an AgentResponse first
        agent_response = AgentResponse(**response)
        # Then convert to ChatMessage
        chat_message = agent_response.to_chat_message(agent_name)
        self.add_message(chat_message.dict(), self._get_conversation_id(conversation_id))
        logger.info(f"Added response from agent {agent_name} to conversation {conversation_id}")

    def set_uploaded_file(self, has_file: bool, conversation_id: Optional[str] = None):
        """
        Set whether a conversation has an uploaded file.

        Args:
            has_file (bool): Whether file is uploaded
            conversation_id (str, optional): Target conversation. Defaults to "default"
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        conversation.has_uploaded_file = has_file
        logger.info(f"Set uploaded file status to {has_file} for conversation {conversation_id}")

    def get_uploaded_file_status(self, conversation_id: Optional[str] = None) -> bool:
        """
        Check if a conversation has an uploaded file.

        Args:
            conversation_id (str, optional): Conversation to check. Defaults to "default"

        Returns:
            bool: True if conversation has uploaded file, False otherwise
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        return conversation.has_uploaded_file

    def clear_messages(self, conversation_id: Optional[str] = None):
        """
        Clear all messages in a conversation except the default message.

        Args:
            conversation_id (str, optional): Conversation to clear. Defaults to "default"
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        conversation.messages = [self.default_message]  # Keep the initial message
        logger.info(f"Cleared message history for conversation {conversation_id}")

    def get_last_message(self, conversation_id: Optional[str] = None) -> Dict[str, str]:
        """
        Get the most recent message from a conversation.

        Args:
            conversation_id (str, optional): Conversation to get message from. Defaults to "default"

        Returns:
            Dict[str, str]: Last message or empty dict if no messages
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        return conversation.messages[-1].dict() if conversation.messages else {}

    def get_chat_history(self, conversation_id: Optional[str] = None) -> str:
        """
        Get formatted chat history for a conversation.

        Args:
            conversation_id (str, optional): Conversation to get history for. Defaults to "default"

        Returns:
            str: Formatted chat history as string
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        return "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])

    def get_all_conversation_ids(self) -> List[str]:
        """
        Get a list of all conversation IDs.

        Returns:
            List[str]: List of conversation IDs
        """
        return list(self.conversations.keys())

    def delete_conversation(self, conversation_id: Optional[str] = None):
        """
        Delete a conversation by ID.

        Args:
            conversation_id (str, optional): ID of conversation to delete. Defaults to "default"
        """
        conversation_id = self._get_conversation_id(conversation_id)
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation {conversation_id}")

    def create_conversation(self, conversation_id: Optional[str] = None) -> Dict:
        """
        Create a new conversation with the given ID.

        Args:
            conversation_id (str, optional): ID for new conversation. Defaults to "default"

        Returns:
            Dict: Created conversation as dictionary
        """
        conversation = self._get_or_create_conversation(self._get_conversation_id(conversation_id))
        return conversation.dict()

    def _get_or_create_conversation(self, conversation_id: str) -> Conversation:
        """
        Get existing conversation or create new one if not exists.

        Args:
            conversation_id (str): Conversation ID to get/create

        Returns:
            Conversation: Retrieved or created conversation
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(messages=[self.default_message], has_uploaded_file=False)
        return self.conversations[conversation_id]


# Create an instance to act as a singleton store
chat_manager_instance = ChatManager()
