import React, { FC } from "react";
import { Box } from "@chakra-ui/react";
import { ChatMessage } from "@/services/types";
import { MessageItem } from "../MessageItem";

export const MessageList: FC<{ messages: ChatMessage[] }> = ({ messages }) => {
  return (
    <Box
      flex="1"
      bg="#020804"
      p={4}
      sx={{
        overflowY: "scroll",
        overflowX: "hidden",
        height: "100%",
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
        <MessageItem key={index} message={message} />
      ))}
    </Box>
  );
};
