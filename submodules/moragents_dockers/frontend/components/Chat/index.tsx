import React, { FC } from "react";
import { Flex, Box, useBreakpointValue } from "@chakra-ui/react";
import { MessageList } from "@/components/MessageList";
import { ChatInput } from "@/components/ChatInput";
import { LoadingIndicator } from "@/components/LoadingIndicator";
import { useChatContext } from "@/contexts/chat/useChatContext";

export const Chat: FC<{ isSidebarOpen?: boolean }> = ({
  isSidebarOpen = false,
}) => {
  const { state, sendMessage } = useChatContext();
  const { messages, currentConversationId, isLoading } = state;

  const currentMessages = messages[currentConversationId] || [];
  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleSubmit = async (message: string, file: File | null) => {
    await sendMessage(message, file);
  };

  return (
    <Box position="relative" height="100%" width="100%">
      <Flex
        direction="column"
        height="100%"
        width="100%"
        transition="all 0.3s ease-in-out"
        mt={2}
        paddingLeft={isMobile ? "5%" : isSidebarOpen ? "30%" : "20%"}
        paddingRight={isMobile ? "5%" : isSidebarOpen ? "20%" : "20%"}
        ml="auto"
        mr="auto"
      >
        <MessageList messages={currentMessages} />
        {isLoading && <LoadingIndicator />}
        <ChatInput
          onSubmit={handleSubmit}
          hasMessages={currentMessages.length > 1}
          disabled={isLoading}
          isSidebarOpen={isSidebarOpen}
        />
      </Flex>
    </Box>
  );
};
