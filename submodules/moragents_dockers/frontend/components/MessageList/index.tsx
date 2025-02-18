import React, { FC, useEffect, useRef } from "react";
import { Box } from "@chakra-ui/react";
import { ChatMessage } from "@/services/types";
import { MessageItem } from "@/components/MessageItem";

import styles from "./index.module.css";

export const MessageList: FC<{ messages: ChatMessage[] }> = ({ messages }) => {
  const lastMessageRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length > 0 && lastMessageRef.current && containerRef.current) {
      const lastMessage = lastMessageRef.current;
      const container = containerRef.current;

      // Calculate the scroll position to show the start of the last message
      const scrollPosition = lastMessage.offsetTop - container.offsetTop;

      container.scrollTo({
        top: scrollPosition,
        behavior: "smooth",
      });
    }
  }, [messages]);

  return (
    <Box ref={containerRef} className={styles.messageList}>
      {messages.map((message, index) => (
        <div
          ref={index === messages.length - 1 ? lastMessageRef : undefined}
          key={index}
        >
          <MessageItem message={message} />
        </div>
      ))}
    </Box>
  );
};
