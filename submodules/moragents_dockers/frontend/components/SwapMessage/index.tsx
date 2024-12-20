import React, { FC } from "react";
import { SwapForm } from "../SwapForm";
import { SwapMessagePayload } from "@/services/types";
import { Box, Text } from "@chakra-ui/react";

type SwapMessageProps = {
  isActive: boolean;
  onCancelSwap: (fromAction: number) => void;
  fromMessage: SwapMessagePayload | null;
  onSubmitSwap: (swapTx: any) => void;
};

export const SwapMessage: FC<SwapMessageProps> = ({
  isActive,
  onCancelSwap,
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
      fromMessage={fromMessage}
      onSubmitApprove={() => {}} // Implement approve logic if needed
      onSubmitSwap={onSubmitSwap}
    />
  );
};
