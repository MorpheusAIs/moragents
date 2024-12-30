import React, { FC, useEffect, useState } from "react";
import { Flex, Box } from "@chakra-ui/react";
import { ChatMessage } from "@/services/types";
import { useTransactionConfirmations } from "wagmi";
import { MessageList } from "@/components/MessageList";
import { ChatInput } from "@/components/ChatInput";
import { LoadingIndicator } from "@/components/LoadingIndicator";
import { Widgets, shouldOpenWidget } from "@/components/Widgets";
import { ChatProps } from "@/components/Chat/types";
import { useChat } from "@/components/Chat/hooks";

export const Chat: FC<ChatProps> = ({
  onSubmitMessage,
  onCancelSwap,
  messages,
  onBackendError,
  // New prop from Home that indicates whether the sidebar is open
  isSidebarOpen = false,
}) => {
  const [messagesData, setMessagesData] = useState<ChatMessage[]>(messages);
  const [activeWidget, setActiveWidget] = useState<ChatMessage | null>(null);
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);

  const {
    txHash,
    approveTxHash,
    showSpinner,
    setShowSpinner,
    handleSwapSubmit,
    handleClaimSubmit,
  } = useChat(onBackendError);

  useTransactionConfirmations({
    hash: (txHash || "0x") as `0x${string}`,
  });

  useTransactionConfirmations({
    hash: (approveTxHash || "0x") as `0x${string}`,
  });

  useEffect(() => {
    if (messages.length > 0) {
      console.log("messages", messages);
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "assistant" && shouldOpenWidget(lastMessage)) {
        setActiveWidget(lastMessage);
        setIsWidgetOpen(true);
      } else {
        setActiveWidget(null);
        setIsWidgetOpen(false);
      }
    }
    setMessagesData([...messages]);
  }, [messages]);

  const handleSubmit = async (message: string, file: File | null) => {
    setShowSpinner(true);
    await onSubmitMessage(message, file);
    setShowSpinner(false);
  };

  const handleCloseWidget = () => {
    setIsWidgetOpen(false);
    setActiveWidget(null);
  };

  // Decide how far from the left we want to be when the sidebar is open vs closed.
  // Example: if the sidebar is fully open, let's shift it 280px to the right.
  // If it's closed, maybe shift only 80px from the edge. Tweak as needed.
  const chatMarginLeft = isSidebarOpen ? "280px" : "80px";

  return (
    <Box position="relative" height="100%" width="100%">
      <Flex
        direction="column"
        height="100%"
        width="100%"
        transition="all 0.3s ease-in-out"
        mt={4}
        // Existing widget-based padding logic
        paddingLeft={isWidgetOpen ? "5%" : "10%"}
        paddingRight={isWidgetOpen ? "35%" : "30%"}
        // NEW MARGIN to keep space from the sidebar
        ml={chatMarginLeft}
      >
        <MessageList
          messages={messagesData}
          onCancelSwap={onCancelSwap}
          onSwapSubmit={handleSwapSubmit}
          onClaimSubmit={handleClaimSubmit}
        />
        {showSpinner && <LoadingIndicator />}
        <ChatInput
          onSubmit={handleSubmit}
          hasMessages={messagesData.length > 1}
          disabled={
            showSpinner ||
            messagesData[messagesData.length - 1]?.role === "swap"
          }
          isSidebarOpen={isSidebarOpen}
        />
      </Flex>

      {/* The widgets panel on the right side */}
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
        <Widgets activeWidget={activeWidget} onClose={handleCloseWidget} />
      </Box>
    </Box>
  );
};
