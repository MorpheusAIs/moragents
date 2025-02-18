import { ChatMessage, UserMessage } from "@/services/types";

interface Conversation {
  id: string;
  messages: ChatMessage[];
  createdAt: number;
}

interface LocalStorageData {
  conversations: { [key: string]: Conversation };
  lastConversationId: number;
}

const STORAGE_KEY = "chat_data";

// Initialize local storage with default data
export const initializeStorage = (): LocalStorageData => {
  const defaultData: LocalStorageData = {
    conversations: {
      default: {
        id: "default",
        messages: [],
        createdAt: Date.now(),
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
  return JSON.parse(data);
};

// Save data to local storage
export const saveStorageData = (data: LocalStorageData) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
};

// Conversation Management
export const createNewConversation = (): string => {
  const data = getStorageData();
  const newId = `chat_${data.lastConversationId + 1}`;

  data.conversations[newId] = {
    id: newId,
    messages: [],
    createdAt: Date.now(),
  };

  data.lastConversationId += 1;
  saveStorageData(data);

  return newId;
};

export const deleteConversation = (conversationId: string): void => {
  if (conversationId === "default") {
    throw new Error("Cannot delete default conversation");
  }

  const data = getStorageData();
  delete data.conversations[conversationId];
  saveStorageData(data);
};

export const getAllConversations = (): string[] => {
  const data = getStorageData();
  return Object.keys(data.conversations).sort((a, b) => {
    if (a === "default") return -1;
    if (b === "default") return 1;
    return data.conversations[b].createdAt - data.conversations[a].createdAt;
  });
};

// Message Management
export const getMessagesHistory = (
  conversationId: string = "default"
): ChatMessage[] => {
  const data = getStorageData();
  return data.conversations[conversationId]?.messages || [];
};

export const clearMessagesHistory = (
  conversationId: string = "default"
): void => {
  const data = getStorageData();
  if (data.conversations[conversationId]) {
    data.conversations[conversationId].messages = [];
    saveStorageData(data);
  }
};

export const addMessageToHistory = (
  message: ChatMessage,
  conversationId: string = "default"
): void => {
  const data = getStorageData();
  if (!data.conversations[conversationId]) {
    throw new Error(`Conversation ${conversationId} not found`);
  }

  data.conversations[conversationId].messages.push(message);
  saveStorageData(data);
};

// API Integration
export const writeMessage = async (
  message: string,
  backendClient: any,
  chainId: number,
  address: string,
  conversationId: string = "default"
): Promise<ChatMessage[]> => {
  const currentHistory = getMessagesHistory(conversationId);

  const newMessage: UserMessage = {
    role: "user",
    content: message,
    timestamp: Date.now(),
  };

  // Add user message to local storage
  addMessageToHistory(newMessage, conversationId);

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

    // Add assistant's response to local storage
    if (response.data.message) {
      addMessageToHistory(response.data.message, conversationId);
    }

    return getMessagesHistory(conversationId);
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
};
