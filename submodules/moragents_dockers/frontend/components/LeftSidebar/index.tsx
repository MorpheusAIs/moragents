import React, { FC, useEffect, useState } from "react";
import { useToast } from "@chakra-ui/react";
import { IconMenu2, IconPencilPlus, IconTrash } from "@tabler/icons-react";
import { getHttpClient } from "@/services/constants";
import { createNewConversation } from "@/services/apiHooks";
import styles from "./index.module.css";

export type LeftSidebarProps = {
  currentConversationId: string;
  onConversationSelect: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
  setCurrentConversationId: (conversationId: string) => void;
};

export const LeftSidebar: FC<LeftSidebarProps> = ({
  currentConversationId,
  onConversationSelect,
  onDeleteConversation,
  setCurrentConversationId,
}) => {
  const [conversations, setConversations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const toast = useToast();

  const fetchConversations = async () => {
    try {
      const response = await getHttpClient().get("/chat/conversations");
      setConversations(response.data.conversation_ids);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
      toast({
        title: "Error",
        description: "Failed to fetch conversations",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleCreateNewConversation = async () => {
    setIsLoading(true);
    try {
      const response = await createNewConversation(getHttpClient());
      await fetchConversations();
      onConversationSelect(response);
      setCurrentConversationId(response);
      toast({
        title: "Success",
        description: "New conversation created",
        status: "success",
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Failed to create new conversation:", error);
      toast({
        title: "Error",
        description: "Failed to create new conversation",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await onDeleteConversation(conversationId);
      await fetchConversations();
      if (conversationId === currentConversationId) {
        onConversationSelect("default");
        setCurrentConversationId("default");
      }
      toast({
        title: "Success",
        description: "Conversation deleted",
        status: "success",
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      toast({
        title: "Error",
        description: "Failed to delete conversation",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  const formatConversationName = (id: string) => {
    if (id === "default") return "Default Chat";
    const number = id.split("_")[1];
    return `Chat ${number}`;
  };

  return (
    <>
      <button
        className={styles.toggleButton}
        onClick={() => setIsCollapsed(!isCollapsed)}
        aria-label="Toggle sidebar"
      >
        <IconMenu2 size={20} />
      </button>

      <div
        className={`${styles.sidebar} ${
          isCollapsed ? styles.sidebarCollapsed : styles.sidebarExpanded
        }`}
      >
        <div className={styles.container}>
          <button
            className={styles.newChatButton}
            onClick={handleCreateNewConversation}
            disabled={isLoading}
          >
            <IconPencilPlus size={16} />
            <span>New chat</span>
          </button>

          {conversations.map((conversationId) => (
            <div
              key={conversationId}
              className={`${styles.conversationItem} ${
                currentConversationId === conversationId
                  ? styles.conversationActive
                  : ""
              }`}
              onClick={() => {
                onConversationSelect(conversationId);
                setCurrentConversationId(conversationId);
              }}
            >
              <span className={styles.conversationName}>
                {formatConversationName(conversationId)}
              </span>
              {conversationId !== "default" && (
                <button
                  className={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteConversation(conversationId);
                  }}
                >
                  <IconTrash size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};
