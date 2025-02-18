import React, { FC, useEffect, useState } from "react";
import {
  Box,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Text,
  VStack,
  Popover,
  PopoverContent,
  PopoverBody,
  PopoverArrow,
  PopoverTrigger,
} from "@chakra-ui/react";
import {
  IconChevronLeft,
  IconChevronRight,
  IconPlus,
  IconSearch,
  IconRefresh,
  IconTrash,
} from "@tabler/icons-react";
import {
  getAllConversations,
  createNewConversation,
  clearMessagesHistory,
} from "@/services/chat_management/sessions";
import { ProfileMenu } from "./ProfileMenu";
import styles from "./index.module.css";
import { useRouter } from "next/router";

export type LeftSidebarProps = {
  isSidebarOpen: boolean;
  onToggleSidebar: (open: boolean) => void;
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
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("llama3.2:3b");
  const router = useRouter();
  const ToggleIcon = isSidebarOpen ? IconChevronLeft : IconChevronRight;

  const modelOptions = [{ value: "llama3.2:3b", label: "Llama 3.2 (3B)" }];

  const fetchConversations = () => {
    try {
      // Get conversations from local storage
      const conversationIds = getAllConversations();
      setConversations(conversationIds);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
    }
  };

  const handleCreateNewConversation = async () => {
    setIsLoading(true);
    try {
      // Create new conversation in local storage
      const newConversationId = createNewConversation();
      fetchConversations();
      onConversationSelect(newConversationId);
      setCurrentConversationId(newConversationId);
    } catch (error) {
      console.error("Failed to create new conversation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      await onDeleteConversation(conversationId);
      fetchConversations();
      if (conversationId === currentConversationId) {
        onConversationSelect("default");
        setCurrentConversationId("default");
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  const handleClearChatHistory = async () => {
    try {
      clearMessagesHistory(currentConversationId);
      router.reload();
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [currentConversationId]);

  const formatConversationName = (id: string) => {
    if (id === "default") return "Default Chat";
    const parts = id.split("_");
    const number = parts.length > 1 ? parts[1] : id;
    return `Chat ${number}`;
  };

  const filteredConversations = conversations.filter((conv) =>
    formatConversationName(conv)
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
  );

  return (
    <div
      className={`${styles.sidebarContainer} ${
        !isSidebarOpen ? styles.collapsed : ""
      }`}
    >
      <div className={styles.sidebar}>
        <div className={styles.container}>
          <div className={styles.searchContainer}>
            <InputGroup>
              <InputLeftElement>
                <IconSearch className={styles.searchIcon} size={16} />
              </InputLeftElement>
              <Input
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={styles.searchInput}
              />
            </InputGroup>
            <button
              className={styles.newChatIcon}
              onClick={handleCreateNewConversation}
              disabled={isLoading}
            >
              <IconPlus size={16} />
            </button>
          </div>

          <div className={styles.mainContent}>
            {filteredConversations.map((conversationId) => (
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

          <Box width="100%" mb={1}>
            <Popover
              placement="top"
              trigger="hover"
              openDelay={0}
              closeDelay={0}
            >
              <PopoverTrigger>
                <Box
                  as="button"
                  width="100%"
                  bg="rgba(255, 255, 255, 0.05)"
                  color="white"
                  borderColor="rgba(255, 255, 255, 0.1)"
                  borderWidth="1px"
                  borderRadius="8px"
                  fontSize="15px"
                  fontWeight="500"
                  height="40px"
                  opacity="0.8"
                  cursor="pointer"
                  _hover={{ bg: "rgba(255, 255, 255, 0.08)" }}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  Create or Trade Tokenized Agents
                </Box>
              </PopoverTrigger>
              <PopoverContent
                bg="#080808"
                borderColor="rgba(255, 255, 255, 0.1)"
                boxShadow="0 4px 12px rgba(0, 0, 0, 0.2)"
                color="white"
                fontSize="14px"
                maxWidth="380px"
                _focus={{
                  boxShadow: "none",
                  outline: "none",
                }}
              >
                <PopoverArrow bg="#080808" />
                <PopoverBody p={4}>
                  All of the functionality in moragents can be leveraged in your
                  own custom agents that can trade for you, post on X, and more.
                  Agent tokenization is coming soon.
                </PopoverBody>
              </PopoverContent>
            </Popover>
          </Box>

          <div className={styles.footer}>
            <VStack spacing={4} align="stretch" width="100%">
              <Box width="100%">
                <Box className={styles.modelSelection}>
                  <Text className={styles.modelLabel}>Model:</Text>
                  <Select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className={styles.modelSelect}
                  >
                    {modelOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </Box>
                <div className={styles.comingSoonContainer}>
                  <Text className={styles.costInfo}>Coming soon</Text>
                  <Text className={styles.modelNote}>
                    Stake your Morpheus tokens to access more powerful models
                    and leverage builder keys to automatically enable advanced
                    agents.
                  </Text>
                </div>
              </Box>
            </VStack>

            <ProfileMenu />
          </div>
        </div>
      </div>

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
