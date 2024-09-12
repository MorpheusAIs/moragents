import React, { FC } from "react";
import { SwapForm } from "../SwapForm";
import { SwapMessagePayload } from "../../services/backendClient";
import { Box, Text } from "@chakra-ui/react";

type SwapMessageProps = {
  isActive: boolean;
  onCancelSwap: (fromAction: number) => void;
  selectedAgent: string;
  fromMessage: SwapMessagePayload | null;
  onSubmitSwap: (swapTx: any) => void;
};

export const SwapMessage: FC<SwapMessageProps> = ({
  isActive,
  onCancelSwap,
  selectedAgent,
  fromMessage,
  onSubmitSwap,
}) => {
  if (!fromMessage) {
    return (
      <Box p={4} bg="red.100" color="red.800" borderRadius="md">
        <Text>Error: Swap message data is not available.</Text>
      </Box>
    );
  }

  return (
    <SwapForm
      isActive={isActive}
      onCancelSwap={onCancelSwap}
      selectedAgent={selectedAgent}
      fromMessage={fromMessage}
      onSubmitApprove={() => {}} // Implement approve logic if needed
      onSubmitSwap={onSubmitSwap}
    />
  );
};
