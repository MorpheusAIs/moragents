import React, { FC } from "react";
import { Box } from "@chakra-ui/react";
import { ChatMessage } from "@/services/types";
import { MessageItem } from "../MessageItem";

import styles from "./index.module.css";

export const MessageList: FC<{ messages: ChatMessage[] }> = ({ messages }) => {
  return (
    <Box className={styles.messageList}>
      {messages.map((message, index) => (
        <MessageItem key={index} message={message} />
      ))}
    </Box>
  );
};
