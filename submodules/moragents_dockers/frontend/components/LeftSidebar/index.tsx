import React, { FC, useEffect, useState } from "react";
import { useToast, Select, VStack, Box, Text } from "@chakra-ui/react";
import {
  IconTrash,
  IconPencilPlus,
  IconChevronLeft,
  IconChevronRight,
  IconRefresh,
} from "@tabler/icons-react";
import { getHttpClient } from "@/services/constants";
import {
  createNewConversation,
  clearMessagesHistory,
} from "@/services/apiHooks";
import { SettingsButton } from "@/components/Settings";
import { Workflows } from "@/components/Workflows";
import styles from "./index.module.css";
import { useRouter } from "next/router";
import { ApiCredentialsButton } from "@/components/Credentials/Button";

export type LeftSidebarProps = {
  /** Whether the sidebar is currently open (expanded) or collapsed */
  isSidebarOpen: boolean;
  /** Callback to toggle the sidebar state */
  onToggleSidebar: (open: boolean) => void;

  /** Your existing props for conversation management */
  currentConversationId: string;
  onConversationSelect: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
  setCurrentConversationId: (conversationId: string) => void;
};

export const LeftSidebar: FC<LeftSidebarProps> = ({
  isSidebarOpen,
  onToggleSidebar,
  currentConversationId,
  onConversationSelect,
  onDeleteConversation,
  setCurrentConversationId,
}) => {
  const [conversations, setConversations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("llama3.2:3b");
  const backendClient = getHttpClient();
  const router = useRouter();
  const toast = useToast();

  const modelOptions = [{ value: "llama3.2:3b", label: "Llama 3.2 (3B)" }];

  // Decide which icon to show depending on whether the sidebar is open
  const ToggleIcon = isSidebarOpen ? IconChevronLeft : IconChevronRight;

  // Fetch existing conversations from your backend
  const fetchConversations = async () => {
    try {
      const response = await getHttpClient().get("/chat/conversations");
      const conversationIds: string[] = response.data.conversation_ids;
      // Ensure "default" is always at the top if it exists
      conversationIds.sort((a, b) => {
        if (a === "default") return -1;
        if (b === "default") return 1;
        return a.localeCompare(b);
      });
      setConversations(conversationIds);
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

  // Create a new conversation
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

  // Delete a conversation
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

  const handleClearChatHistory = async () => {
    try {
      await clearMessagesHistory(backendClient);
      router.reload();
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    }
  };

  // On mount, fetch conversations
  useEffect(() => {
    fetchConversations();
  }, []);

  // Simple function to give each conversation a friendly name
  const formatConversationName = (id: string) => {
    if (id === "default") return "Default Chat";
    const parts = id.split("_");
    const number = parts.length > 1 ? parts[1] : id;
    return `Chat ${number}`;
  };

  return (
    <div
      className={`${styles.sidebarContainer} ${
        isSidebarOpen ? "" : styles.collapsed
      }`}
    >
      {/* Sidebar Content */}
      <div className={styles.sidebar}>
        <div className={styles.container}>
          <div className={styles.mainContent}>
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
                <div className={styles.buttonGroup}>
                  <button
                    className={styles.resetButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleClearChatHistory();
                    }}
                  >
                    <IconRefresh size={16} />
                  </button>
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
              </div>
            ))}
          </div>

          <VStack spacing={4} className={styles.sidebarFooter} align="stretch">
            <Box display="flex" flexDirection="column" gap={2}>
              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Text fontSize="md" fontWeight="bold" color="white" mr={2}>
                  Model:
                </Text>
                <Select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  size="md"
                  bg="#1f1f1f"
                  color="white"
                  borderColor="rgba(255, 255, 255, 0.2)"
                  _hover={{ borderColor: "rgba(255, 255, 255, 0.4)" }}
                  _focus={{ borderColor: "teal.400" }}
                  width="65%"
                >
                  {modelOptions.map((option) => (
                    <option
                      key={option.value}
                      value={option.value}
                      style={{ backgroundColor: "#1f1f1f", color: "white" }}
                    >
                      {option.label}
                    </option>
                  ))}
                </Select>
              </Box>

              <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
              >
                <Text fontSize="md" fontWeight="bold" color="white" mr={2}>
                  Cost:
                </Text>
                <Text fontSize="sm" color="green.400" fontWeight="500">
                  Free. Running locally.
                </Text>
              </Box>

              <Text fontSize="sm" color="gray.400" fontStyle="italic">
                More powerful models are coming soon via the Lumerin Node Router
              </Text>
            </Box>

            <Workflows />
            <ApiCredentialsButton />
            <SettingsButton />
          </VStack>
        </div>
      </div>

      {/* Toggle Button on the right edge of the sidebar */}
      <button
        className={styles.toggleButton}
        onClick={() => onToggleSidebar(!isSidebarOpen)}
        aria-label="Toggle sidebar"
      >
        <ToggleIcon size={20} />
      </button>
    </div>
  );
};
