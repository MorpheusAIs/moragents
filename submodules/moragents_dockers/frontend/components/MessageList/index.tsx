import React, { FC } from "react";
import { Box } from "@chakra-ui/react";
import { ChatMessage } from "../../services/backendClient";
import { MessageItem } from "../MessageItem";

type MessageListProps = {
  messages: ChatMessage[];
  selectedAgent: string;
  onCancelSwap: (fromAction: number) => void;
  onSwapSubmit: (swapTx: any) => void;
  onClaimSubmit: (claimTx: any) => void;
};

export const MessageList: FC<MessageListProps> = ({
  messages,
  selectedAgent,
  onCancelSwap,
  onSwapSubmit,
  onClaimSubmit,
}) => {
  return (
    <Box
      flex="1"
      bg="#020804"
      p={4}
      sx={{
        overflowY: "scroll",
        overflowX: "hidden",
        height: "calc(100vh - 200px)",
        "::-webkit-scrollbar": {
          width: "8px",
          backgroundColor: "transparent",
        },
        "::-webkit-scrollbar-thumb": {
          backgroundColor: "#111613",
          borderRadius: "4px",
        },
      }}
    >
      {messages.map((message, index) => (
        <MessageItem
          key={index}
          message={message}
          selectedAgent={selectedAgent}
          onCancelSwap={onCancelSwap}
          onSwapSubmit={onSwapSubmit}
          onClaimSubmit={onClaimSubmit}
          isLastSwapMessage={
            index === messages.length - 1 && message.role === "swap"
          }
          isLastClaimMessage={
            index === messages.length - 1 && message.role === "claim"
          }
        />
      ))}
    </Box>
  );
};