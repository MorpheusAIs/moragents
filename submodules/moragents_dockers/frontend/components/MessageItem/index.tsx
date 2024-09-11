import React, { FC } from "react";
import { Grid, GridItem, Text, Textarea } from "@chakra-ui/react";
import { ChatMessage, SwapMessagePayload } from "../../services/backendClient";
import { Avatar } from "../Avatar";
import { availableAgents } from "../../config";
import { SwapMessage } from "../SwapMessage";

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
      bg={"#020804"}
      color={"white"}
      borderRadius={4}
      mb={2}
      gap={2}
    >
      <GridItem area="avatar">
        <Avatar
          isAgent={message.role !== "user"}
          agentName={availableAgents[selectedAgent]?.name || "Undefined Agent"}
        />
      </GridItem>
      <GridItem area="name">
        <Text
          sx={{
            fontSize: "16px",
            fontWeight: "bold",
            lineHeight: "125%",
            mt: 1,
            ml: 2,
          }}
        >
          {message.role === "user"
            ? "Me"
            : availableAgents[selectedAgent]?.name || "Undefined Agent"}
        </Text>
      </GridItem>
      <GridItem area="message">
        {typeof message.content === "string" ? (
          message.agentName === "tweet_sizzler" ? (
            <Textarea
              value={message.content}
              readOnly
              sx={{
                fontSize: "16px",
                lineHeight: "125%",
                mt: 4,
                mb: 5,
                ml: 2,
                color: "white",
                backgroundColor: "#111613",
                border: "none",
                resize: "vertical",
              }}
            />
          ) : (
            <Text
              sx={{ fontSize: "16px", lineHeight: "125%", mt: 4, mb: 5, ml: 2 }}
            >
              {message.content}
            </Text>
          )
        ) : (
          <SwapMessage
            isActive={isLastSwapMessage}
            onCancelSwap={onCancelSwap}
            selectedAgent={selectedAgent}
            fromMessage={message.content as unknown as SwapMessagePayload}
            onSubmitSwap={onSwapSubmit}
          />
        )}
      </GridItem>
    </Grid>
  );
};
