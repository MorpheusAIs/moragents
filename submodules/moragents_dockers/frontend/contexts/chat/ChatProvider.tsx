import React, { useReducer, useCallback, useEffect, ReactNode } from "react";
import { useChainId, useAccount } from "wagmi";
import { ChatMessage } from "@/services/types";
import { getHttpClient } from "@/services/constants";
import { writeMessage, uploadFile } from "@/services/ChatManagement/api";
import { getMessagesHistory } from "@/services/ChatManagement/storage";
import { deleteConversation } from "@/services/ChatManagement/conversations";
import { chatReducer, initialState } from "@/contexts/chat/ChatReducer";
import ChatContext from "@/contexts/chat/ChatContext";

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const chainId = useChainId();
  const { address } = useAccount();

  // Load initial messages for default conversation
  useEffect(() => {
    const loadInitialMessages = async () => {
      try {
        const messages = getMessagesHistory("default");
        dispatch({
          type: "SET_MESSAGES",
          payload: { conversationId: "default", messages },
        });
      } catch (error) {
        console.error("Failed to load initial messages:", error);
      }
    };

    loadInitialMessages();
  }, []);

  // Set current conversation and load its messages
  const setCurrentConversation = useCallback(
    async (conversationId: string) => {
      dispatch({ type: "SET_CURRENT_CONVERSATION", payload: conversationId });

      // Load messages if not already loaded
      if (!state.messages[conversationId]) {
        dispatch({ type: "SET_LOADING", payload: true });
        try {
          const messages = getMessagesHistory(conversationId);
          dispatch({
            type: "SET_MESSAGES",
            payload: { conversationId, messages },
          });
        } catch (error) {
          console.error(
            `Failed to load messages for conversation ${conversationId}:`,
            error
          );
          dispatch({ type: "SET_ERROR", payload: "Failed to load messages" });
        } finally {
          dispatch({ type: "SET_LOADING", payload: false });
        }
      }
    },
    [state.messages]
  );

  // Refresh messages for current conversation
  const refreshMessages = useCallback(async () => {
    const { currentConversationId } = state;
    dispatch({ type: "SET_LOADING", payload: true });

    try {
      const messages = getMessagesHistory(currentConversationId);
      dispatch({
        type: "SET_MESSAGES",
        payload: { conversationId: currentConversationId, messages },
      });
    } catch (error) {
      console.error("Failed to refresh messages:", error);
      dispatch({ type: "SET_ERROR", payload: "Failed to refresh messages" });
    } finally {
      dispatch({ type: "SET_LOADING", payload: false });
    }
  }, [state.currentConversationId]);

  // Send message or file
  const sendMessage = useCallback(
    async (message: string, file: File | null) => {
      if (!message && !file) return;

      const { currentConversationId } = state;
      dispatch({ type: "SET_LOADING", payload: true });

      try {
        if (!file) {
          // Text message flow
          // Add optimistic user message
          const optimisticMessage: ChatMessage = {
            role: "user",
            content: message,
            timestamp: Date.now(),
          };

          // Update UI immediately
          dispatch({
            type: "ADD_OPTIMISTIC_MESSAGE",
            payload: {
              conversationId: currentConversationId,
              message: optimisticMessage,
            },
          });

          // Send to server
          await writeMessage(
            message,
            getHttpClient(),
            chainId,
            address || "",
            currentConversationId
          );
        } else {
          // File upload flow
          await uploadFile(
            file,
            getHttpClient(),
            chainId,
            address || "",
            currentConversationId
          );
        }

        // Refresh messages to get server response
        await refreshMessages();
      } catch (error) {
        console.error("Failed to send message:", error);
        dispatch({ type: "SET_ERROR", payload: "Failed to send message" });
      } finally {
        dispatch({ type: "SET_LOADING", payload: false });
      }
    },
    [state.currentConversationId, chainId, address, refreshMessages]
  );

  // Delete conversation
  const deleteChat = useCallback(
    async (conversationId: string) => {
      dispatch({ type: "SET_LOADING", payload: true });

      try {
        deleteConversation(conversationId);

        // If current conversation was deleted, switch to default
        if (conversationId === state.currentConversationId) {
          dispatch({ type: "SET_CURRENT_CONVERSATION", payload: "default" });
          const defaultMessages = getMessagesHistory("default");
          dispatch({
            type: "SET_MESSAGES",
            payload: { conversationId: "default", messages: defaultMessages },
          });
        }
      } catch (error) {
        console.error("Failed to delete conversation:", error);
        dispatch({
          type: "SET_ERROR",
          payload: "Failed to delete conversation",
        });
      } finally {
        dispatch({ type: "SET_LOADING", payload: false });
      }
    },
    [state.currentConversationId]
  );

  // Context value
  const value = {
    state,
    setCurrentConversation,
    sendMessage,
    refreshMessages,
    deleteChat,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
