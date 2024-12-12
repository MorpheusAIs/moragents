import React, { FC, useEffect, useState } from "react";
import { Box, VStack, Text, Button, useToast } from "@chakra-ui/react";
import {
  IconChevronLeft,
  IconChevronRight,
  IconPlus,
  IconTrash,
} from "@tabler/icons-react";
import { getHttpClient } from "@/services/constants";
import { createNewConversation } from "@/services/apiHooks";

export type LeftSidebarProps = {
  currentConversationId: string;
  onConversationSelect: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
};

export const LeftSidebar: FC<LeftSidebarProps> = ({
  currentConversationId,
  onConversationSelect,
  onDeleteConversation,
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
    <Box
      bg="#020804"
      height="100vh"
      width={isCollapsed ? "60px" : "240px"}
      transition="width 0.2s"
      position="relative"
    >
      <Button
        position="absolute"
        right="-12px"
        top="20px"
        size="sm"
        zIndex={2}
        onClick={() => setIsCollapsed(!isCollapsed)}
        bg="#2D3748"
        color="white"
        _hover={{ bg: "#4A5568" }}
      >
        {isCollapsed ? (
          <IconChevronRight size={16} />
        ) : (
          <IconChevronLeft size={16} />
        )}
      </Button>

      <VStack align="stretch" p={4} height="100%" spacing={4}>
        <Button
          onClick={handleCreateNewConversation}
          isLoading={isLoading}
          bg="#2D3748"
          color="white"
          _hover={{ bg: "#4A5568" }}
          w="100%"
        >
          {isCollapsed ? <IconPlus size={20} /> : "New Chat"}
        </Button>

        {conversations.map((conversationId) => (
          <Box
            key={conversationId}
            p={3}
            bg={
              currentConversationId === conversationId ? "#2D3748" : "#1A1A1A"
            }
            borderRadius="md"
            cursor="pointer"
            transition="all 0.2s"
            _hover={{ bg: "#2D3748" }}
            onClick={() => onConversationSelect(conversationId)}
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            overflow="hidden"
          >
            {!isCollapsed && (
              <Text color="white" fontSize="sm" isTruncated>
                {formatConversationName(conversationId)}
              </Text>
            )}
            {conversationId !== "default" && (
              <Button
                size="sm"
                colorScheme="red"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteConversation(conversationId);
                }}
                opacity={0.8}
                _hover={{ opacity: 1 }}
              >
                {isCollapsed ? <IconTrash size={16} /> : "Delete"}
              </Button>
            )}
          </Box>
        ))}
      </VStack>
    </Box>
  );
};
