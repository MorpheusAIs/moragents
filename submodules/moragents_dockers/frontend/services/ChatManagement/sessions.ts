import { ChatMessage, AssistantMessage, UserMessage } from "@/services/types";

interface Conversation {
  id: string;
  messages: ChatMessage[];
  createdAt: number;
  hasUploadedFile: boolean;
}

interface LocalStorageData {
  conversations: { [key: string]: Conversation };
  lastConversationId: number;
}

const STORAGE_KEY = "chat_data";

// Default welcome message that appears in all new conversations
const DEFAULT_MESSAGE: AssistantMessage = {
  role: "assistant",
  agentName: "Morpheus AI",
  content: `This highly experimental chatbot is not intended for making important decisions. Its
            responses are generated using AI models and may not always be accurate.
            By using this chatbot, you acknowledge that you use it at your own discretion
            and assume all risks associated with its limitations and potential errors.`,
  timestamp: Date.now(),
  metadata: {},
  requires_action: false,
};

// Initialize local storage with default data
export const initializeStorage = (): LocalStorageData => {
  const defaultData: LocalStorageData = {
    conversations: {
      default: {
        id: "default",
        messages: [DEFAULT_MESSAGE],
        createdAt: Date.now(),
        hasUploadedFile: false,
      },
    },
    lastConversationId: 0,
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
  return defaultData;
};

// Get all data from local storage
export const getStorageData = (): LocalStorageData => {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) {
    return initializeStorage();
  }

  try {
    const parsedData = JSON.parse(data) as LocalStorageData;

    // Ensure all conversations have the required structure
    Object.keys(parsedData.conversations).forEach((convId) => {
      const conv = parsedData.conversations[convId];

      // Ensure hasUploadedFile property exists
      if (conv.hasUploadedFile === undefined) {
        conv.hasUploadedFile = false;
      }

      // Ensure default message exists in each conversation
      if (
        conv.messages.length === 0 ||
        !conv.messages.some(
          (msg) =>
            msg.role === "assistant" &&
            msg.agentName === "Morpheus AI" &&
            (typeof msg.content === "string"
              ? msg.content.includes("highly experimental chatbot")
              : false)
        )
      ) {
        conv.messages.unshift({
          ...DEFAULT_MESSAGE,
          timestamp: conv.createdAt,
        });
      }
    });

    return parsedData;
  } catch (error) {
    console.error("Error parsing chat data from localStorage:", error);
    return initializeStorage();
  }
};

// Save data to local storage
export const saveStorageData = (data: LocalStorageData): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

// Conversation Management
export const createNewConversation = (): string => {
  const data = getStorageData();
  const newId = `chat_${data.lastConversationId + 1}`;
  const timestamp = Date.now();

  data.conversations[newId] = {
    id: newId,
    messages: [{ ...DEFAULT_MESSAGE, timestamp }],
    createdAt: timestamp,
    hasUploadedFile: false,
  };

  data.lastConversationId += 1;
  saveStorageData(data);

  return newId;
};

export const getOrCreateConversation = (
  conversationId: string = "default"
): string => {
  const data = getStorageData();

  if (!data.conversations[conversationId]) {
    if (conversationId === "default") {
      // Create the default conversation if it doesn't exist
      data.conversations.default = {
        id: "default",
        messages: [DEFAULT_MESSAGE],
        createdAt: Date.now(),
        hasUploadedFile: false,
      };
      saveStorageData(data);
    } else {
      // For non-default conversations, create a new one
      return createNewConversation();
    }
  }

  return conversationId;
};

export const deleteConversation = (conversationId: string): void => {
  if (conversationId === "default") {
    // Clear messages instead of deleting the default conversation
    clearMessagesHistory("default");
    return;
  }

  const data = getStorageData();
  if (data.conversations[conversationId]) {
    delete data.conversations[conversationId];
    saveStorageData(data);
  }
};

export const getAllConversations = (): string[] => {
  const data = getStorageData();
  return Object.keys(data.conversations).sort((a, b) => {
    if (a === "default") return -1;
    if (b === "default") return 1;
    return data.conversations[b].createdAt - data.conversations[a].createdAt;
  });
};

// File Upload Management
export const setUploadedFileStatus = (
  hasFile: boolean,
  conversationId: string = "default"
): void => {
  const data = getStorageData();
  const convId = getOrCreateConversation(conversationId);

  if (data.conversations[convId]) {
    data.conversations[convId].hasUploadedFile = hasFile;
    saveStorageData(data);
  }
};

export const getUploadedFileStatus = (
  conversationId: string = "default"
): boolean => {
  const data = getStorageData();
  const convId = getOrCreateConversation(conversationId);
  return data.conversations[convId]?.hasUploadedFile || false;
};

// Message Management
export const getMessagesHistory = (
  conversationId: string = "default"
): ChatMessage[] => {
  const data = getStorageData();
  const convId = getOrCreateConversation(conversationId);
  return [...(data.conversations[convId]?.messages || [DEFAULT_MESSAGE])];
};

export const clearMessagesHistory = (
  conversationId: string = "default"
): void => {
  const data = getStorageData();
  const convId = getOrCreateConversation(conversationId);

  if (data.conversations[convId]) {
    // Keep only the default message
    data.conversations[convId].messages = [
      { ...DEFAULT_MESSAGE, timestamp: Date.now() },
    ];
    data.conversations[convId].hasUploadedFile = false;
    saveStorageData(data);
  }
};

export const addMessageToHistory = (
  message: ChatMessage,
  conversationId: string = "default"
): void => {
  const data = getStorageData();
  const convId = getOrCreateConversation(conversationId);

  // Ensure the message has a timestamp
  if (!message.timestamp) {
    message.timestamp = Date.now();
  }

  data.conversations[convId].messages.push(message);
  saveStorageData(data);
};

export const getLastMessage = (
  conversationId: string = "default"
): ChatMessage | null => {
  const messages = getMessagesHistory(conversationId);
  return messages.length > 0 ? messages[messages.length - 1] : null;
};

export const getChatHistoryAsString = (
  conversationId: string = "default"
): string => {
  const messages = getMessagesHistory(conversationId);
  return messages
    .map(
      (msg) =>
        `${msg.role}: ${
          typeof msg.content === "string"
            ? msg.content
            : JSON.stringify(msg.content)
        }`
    )
    .join("\n");
};

// API Integration
export const writeMessage = async (
  message: string,
  backendClient: any,
  chainId: number,
  address: string,
  conversationId: string = "default"
): Promise<ChatMessage[]> => {
  const convId = getOrCreateConversation(conversationId);
  const currentHistory = getMessagesHistory(convId);

  const newMessage: UserMessage = {
    role: "user",
    content: message,
    timestamp: Date.now(),
  };

  // Add user message to local storage
  addMessageToHistory(newMessage, convId);

  try {
    // Send message along with conversation history to backend
    const response = await backendClient.post("/api/v1/chat", {
      prompt: {
        role: "user",
        content: message,
      },
      conversation_history: currentHistory,
      chain_id: String(chainId),
      wallet_address: address,
    });

    // FIX: The response directly contains the message object, not nested in a "message" field
    if (response.data) {
      // Add assistant's response to local storage
      addMessageToHistory(response.data, convId);
    }

    // Return the updated messages after API response is processed
    return getMessagesHistory(convId);
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
};
