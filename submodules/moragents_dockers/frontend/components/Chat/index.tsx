import React, { FC, useEffect, useState } from "react";
import { Flex, Box } from "@chakra-ui/react";
import { ChatMessage } from "@/services/types";
// import { useTransactionConfirmations } from "wagmi";
import { MessageList } from "@/components/MessageList";
import { ChatInput } from "@/components/ChatInput";
import { LoadingIndicator } from "@/components/LoadingIndicator";
import { Widgets, shouldOpenWidget } from "@/components/Widgets";
import { ChatProps } from "@/components/Chat/types";

export const Chat: FC<ChatProps> = ({
  onSubmitMessage,
  messages,
  isSidebarOpen = false,
  setIsSidebarOpen,
}) => {
  const [messagesData, setMessagesData] = useState<ChatMessage[]>(messages);
  const [activeWidget, setActiveWidget] = useState<ChatMessage | null>(null);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "assistant" && shouldOpenWidget(lastMessage)) {
        setActiveWidget(lastMessage);
        setIsWidgetOpen(true);
        setIsSidebarOpen(false);
      } else {
        setActiveWidget(null);
        setIsWidgetOpen(false);
      }
    }
    setMessagesData([...messages]);
  }, [messages, setIsSidebarOpen]);

  const handleSubmit = async (message: string, file: File | null) => {
    setIsLoading(true);
    await onSubmitMessage(message, file);
    setIsLoading(false);
  };

  return (
    <Box position="relative" height="100%" width="100%">
      <Flex
        direction="column"
        height="100%"
        width="100%"
        transition="all 0.3s ease-in-out"
        mt={4}
        paddingLeft={isWidgetOpen ? "5%" : "20%"}
        paddingRight={isWidgetOpen ? "35%" : "20%"}
        ml="auto"
        mr="auto"
      >
        <MessageList messages={messagesData} />
        {isLoading && <LoadingIndicator />}
        <ChatInput
          onSubmit={handleSubmit}
          hasMessages={messagesData.length > 1}
          disabled={isLoading}
          isSidebarOpen={isSidebarOpen}
        />
      </Flex>

      <Box
        position="fixed"
        right={0}
        top={0}
        width="30%"
        height="100%"
        transition="transform 0.3s ease-in-out"
        transform={isWidgetOpen ? "translateX(0)" : "translateX(100%)"}
        borderLeft="1px solid gray"
        zIndex={1}
      >
        <Widgets
          activeWidget={activeWidget}
          onClose={() => setIsWidgetOpen(false)}
        />
      </Box>
    </Box>
  );
};
