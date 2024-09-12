import React, { FC } from "react";
import { Grid, GridItem, Text } from "@chakra-ui/react";
import { ChatMessage, SwapMessagePayload } from "../../services/backendClient";
import { Avatar } from "../Avatar";
import { availableAgents } from "../../config";
import { SwapMessage } from "../SwapMessage";
import { UserOrAssistantMessage } from "../../services/backendClient";
import { Tweet } from "../Tweet";
import styles from "./index.module.css";

type MessageItemProps = {
  message: ChatMessage;
  selectedAgent: string;
  onCancelSwap: (fromAction: number) => void;
  onSwapSubmit: (swapTx: any) => void;
  isLastSwapMessage: boolean;
};

export const MessageItem: FC<MessageItemProps> = ({
  message,
  selectedAgent,
  onCancelSwap,
  onSwapSubmit,
  isLastSwapMessage,
}) => {
  return (
    <Grid
      templateAreas={`
        "avatar name"
        "avatar message"
      `}
      templateColumns={"0fr 3fr"}
      className={styles.messageGrid}
    >
      <GridItem area="avatar">
        <Avatar
          isAgent={message.role !== "user"}
          agentName={availableAgents[selectedAgent]?.name || "Undefined Agent"}
        />
      </GridItem>
      <GridItem area="name">
        <Text className={styles.nameText}>
          {message.role === "user"
            ? "Me"
            : availableAgents[selectedAgent]?.name || "Undefined Agent"}
        </Text>
      </GridItem>
      <GridItem area="message">
        {typeof message.content === "string" ? (
          (message as UserOrAssistantMessage).agentName ===
          "tweet sizzler agent" ? (
            <Tweet
              initialContent={message.content}
              selectedAgent={selectedAgent}
            />
          ) : (
            <Text className={styles.messageText}>{message.content}</Text>
          )
        ) : (
          <SwapMessage
            isActive={isLastSwapMessage}
            onCancelSwap={onCancelSwap}
            selectedAgent={selectedAgent}
            fromMessage={message.content as SwapMessagePayload}
            onSubmitSwap={onSwapSubmit}
          />
        )}
      </GridItem>
    </Grid>
  );
};
