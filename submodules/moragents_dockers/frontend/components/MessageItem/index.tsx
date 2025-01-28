import React, { FC } from "react";
import { Grid, GridItem, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import {
  ChatMessage,
  ImageMessageContent,
  CryptoDataMessageContent,
  BaseMessageContent,
  AssistantMessage,
} from "@/services/types";
import { getHumanReadableAgentName } from "@/services/utils";
import { Avatar } from "@/components/Avatar";
import { Tweet } from "@/components/Agents/Tweet/TweetMessage";

import styles from "./index.module.css";

type MessageItemProps = {
  message: ChatMessage;
};

export const MessageItem: FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === "user";
  const { content, error_message } = message;

  console.log("Message:", message);

  const renderContent = () => {
    // First check for error message
    if (error_message) {
      return (
        <Text color="red.500" className={styles.messageText}>
          {error_message}
        </Text>
      );
    }

    if (typeof content === "string") {
      if (message.agentName === "tweet sizzler") {
        return <Tweet initialContent={content} />;
      }
      return (
        <ReactMarkdown className={styles.messageText}>{content}</ReactMarkdown>
      );
    }

    // Type guard to ensure we're working with AssistantMessage
    if (message.role === "assistant") {
      const assistantMessage = message as AssistantMessage;

      if (message.agentName === "imagen") {
        const imageContent = assistantMessage.content as ImageMessageContent;
        if (!imageContent.success) {
          return (
            <Text color="red.500" className={styles.messageText}>
              {imageContent.error || "Failed to generate image"}
            </Text>
          );
        }
        return (
          <ReactMarkdown className={styles.messageText}>
            {`Successfully generated image with ${imageContent.service}`}
          </ReactMarkdown>
        );
      }

      if (message.agentName === "crypto data") {
        const cryptoDataContent =
          assistantMessage.content as CryptoDataMessageContent;
        return (
          <ReactMarkdown className={styles.messageText}>
            {cryptoDataContent.data}
          </ReactMarkdown>
        );
      }

      if (message.agentName === "base") {
        const baseContent = assistantMessage.content as BaseMessageContent;
        return (
          <ReactMarkdown className={styles.messageText}>
            {baseContent.message}
          </ReactMarkdown>
        );
      }

      // if (assistantMessage.action_type === "claim") {
      //   return (
      //     <ClaimMessage
      //       isActive={isLastClaimMessage}
      //       fromMessage={assistantMessage.content as ClaimMessagePayload}
      //       onSubmitClaim={onClaimSubmit}
      //     />
      //   );
      // }
    }

    return (
      <Text className={styles.messageText}>{JSON.stringify(content)}</Text>
    );
  };

  return (
    <Grid
      templateAreas={`"avatar name" "avatar message"`}
      templateColumns="0fr 3fr"
      className={styles.messageGrid}
    >
      <GridItem area="avatar">
        <Avatar
          isAgent={!isUser}
          agentName={getHumanReadableAgentName(message.agentName || "")}
        />
      </GridItem>
      <GridItem area="name">
        <Text className={styles.nameText}>
          {isUser ? "Me" : getHumanReadableAgentName(message.agentName || "")}
        </Text>
      </GridItem>
      <GridItem area="message">{renderContent()}</GridItem>
    </Grid>
  );
};
