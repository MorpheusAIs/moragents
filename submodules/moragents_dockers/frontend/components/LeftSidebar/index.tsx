import React, { FC, useEffect, useState } from "react";
import { Box, VStack, Text, Button } from "@chakra-ui/react";
import { getHttpClient } from "@/services/constants";

export type LeftSidebarProps = {};

export const LeftSidebar: FC<LeftSidebarProps> = () => {
  const [conversations, setConversations] = useState<string[]>([]);

  const fetchConversations = async () => {
    try {
      const response = await getHttpClient().get("/chat/conversations");
      setConversations(response.data.conversation_ids);
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
    }
  };

  const createNewConversation = async () => {
    try {
      await getHttpClient().post("/chat/conversations");
      fetchConversations();
    } catch (error) {
      console.error("Failed to create new conversation:", error);
    }
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      await getHttpClient().delete(`/chat/conversations/${conversationId}`);
      fetchConversations();
    } catch (error) {
      console.error("Failed to delete conversation:", error);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  return (
    <Box bg="#020804" p={4}>
      <VStack align="stretch" height="85%" spacing={4}>
        <Button onClick={createNewConversation}>New Chat</Button>
        {conversations.map((conversationId) => (
          <Box
            key={conversationId}
            p={3}
            bg="#1A1A1A"
            borderRadius="md"
            display="flex"
            justifyContent="space-between"
            alignItems="center"
          >
            <Text color="white">{conversationId}</Text>
            <Button
              size="sm"
              colorScheme="red"
              onClick={() => deleteConversation(conversationId)}
            >
              Delete
            </Button>
          </Box>
        ))}
      </VStack>
    </Box>
  );
};
