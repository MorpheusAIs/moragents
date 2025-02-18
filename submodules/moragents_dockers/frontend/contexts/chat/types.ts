import { ChatMessage } from "@/services/types";
export interface ChatState {
  messages: Record<string, ChatMessage[]>;
  currentConversationId: string;
  isLoading: boolean;
  error: string | null;
}

export type ChatAction =
  | {
      type: "SET_MESSAGES";
      payload: { conversationId: string; messages: ChatMessage[] };
    }
  | { type: "SET_CURRENT_CONVERSATION"; payload: string }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | {
      type: "ADD_OPTIMISTIC_MESSAGE";
      payload: { conversationId: string; message: ChatMessage };
    };

export interface ChatContextType {
  state: ChatState;
  setCurrentConversation: (id: string) => void;
  sendMessage: (message: string, file: File | null) => Promise<void>;
  refreshMessages: () => Promise<void>;
  deleteChat: (conversationId: string) => Promise<void>;
}
