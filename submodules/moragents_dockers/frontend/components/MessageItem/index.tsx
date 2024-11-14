import React, { FC } from "react";
import { Grid, GridItem, Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import {
  ChatMessage,
  SwapMessagePayload,
  UserOrAssistantMessage,
  ClaimMessagePayload,
} from "../../services/backendClient";
import { Avatar } from "../Avatar";
import { availableAgents } from "../../config";
import { SwapMessage } from "../SwapMessage";
import { ClaimMessage } from "../ClaimMessage/ClaimMessage";
import { Tweet } from "../Tweet";
import styles from "./index.module.css";

const TWEET_AGENT = "tweet sizzler agent";
const SWAP_AGENT = "token swap agent";
const USER_ROLE = "user";
const UNDEFINED_AGENT = "Undefined Agent";

type MessageItemProps = {
  message: ChatMessage;
  selectedAgent: string;
  onCancelSwap: (fromAction: number) => void;
  onSwapSubmit: (swapTx: any) => void;
  onClaimSubmit: (claimTx: any) => void;
  isLastSwapMessage: boolean;
  isLastClaimMessage: boolean;
};

export const MessageItem: FC<MessageItemProps> = ({
  message,
  selectedAgent,
  onCancelSwap,
  onSwapSubmit,
  onClaimSubmit,
  isLastSwapMessage,
  isLastClaimMessage,
}) => {
  const agentName = availableAgents[selectedAgent]?.name || UNDEFINED_AGENT;
  const isUser = message.role === USER_ROLE;
  const { content } = message;

  const renderContent = () => {
    if (typeof content === "string") {
      if ((message as UserOrAssistantMessage).agentName === TWEET_AGENT) {
        return <Tweet initialContent={content} selectedAgent={selectedAgent} />;
      }

      return (
        <ReactMarkdown className={styles.messageText}>{content}</ReactMarkdown>
      );
    }

    if (message.role === "swap")  {
      return (
        <SwapMessage
          isActive={isLastSwapMessage}
          onCancelSwap={onCancelSwap}
          selectedAgent={selectedAgent}
          fromMessage={content as SwapMessagePayload}
          onSubmitSwap={onSwapSubmit}
        />
      );
    }

    if (message.role === "claim") {
      console.log("MessageItem rendering ClaimMessage with content:", message.content);
      return (
        <ClaimMessage
      isActive={isLastClaimMessage}
      selectedAgent={selectedAgent}
      fromMessage={message.content as ClaimMessagePayload}
      onSubmitClaim={onClaimSubmit}
    />
      );
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
        <Avatar isAgent={!isUser} agentName={agentName} />
      </GridItem>
      <GridItem area="name">
        <Text className={styles.nameText}>{isUser ? "Me" : agentName}</Text>
      </GridItem>
      <GridItem area="message">{renderContent()}</GridItem>
    </Grid>
  );
};