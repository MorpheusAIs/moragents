import React, { FC, useEffect, useState } from "react";
import { Flex, Box } from "@chakra-ui/react";
import { ChatMessage } from "../../services/backendClient";
import { useTransactionConfirmations } from "wagmi";
import { MessageList } from "../MessageList";
import { ChatInput } from "../ChatInput";
import { LoadingIndicator } from "../LoadingIndicator";
import { Widgets, shouldOpenWidget } from "../Widgets";
import { ChatProps } from "./types";
import { useChat } from "./hooks";

export const Chat: FC<ChatProps> = ({
  onSubmitMessage,
  onCancelSwap,
  messages,
  selectedAgent,
  onBackendError,
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
      >
        <MessageList
          messages={messagesData}
          selectedAgent={selectedAgent}
          onCancelSwap={onCancelSwap}
          onSwapSubmit={handleSwapSubmit}
          onClaimSubmit={handleClaimSubmit}
        />
        {showSpinner && <LoadingIndicator selectedAgent={selectedAgent} />}
        <ChatInput
          onSubmit={handleSubmit}
          hasMessages={messagesData.length > 1}
          disabled={
            showSpinner ||
            messagesData[messagesData.length - 1]?.role === "swap"
          }
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
        <Widgets activeWidget={activeWidget} onClose={handleCloseWidget} />
      </Box>
    </Box>
  );
};
