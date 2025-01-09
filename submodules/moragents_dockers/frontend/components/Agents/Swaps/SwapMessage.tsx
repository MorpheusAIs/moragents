import React, { FC } from "react";
import { Box, Text } from "@chakra-ui/react";
import { SwapMessagePayload } from "@/services/types";
import { SwapForm } from "@/components/Agents/Swaps/SwapForm";
import { useSwapTransaction } from "@/components/Agents/Swaps/useSwapTransaction";

type SwapMessageProps = {
  isActive: boolean;
  fromMessage: SwapMessagePayload | null;
};

export const SwapMessage: FC<SwapMessageProps> = ({
  isActive,
  fromMessage,
}) => {
  const { handleSwap, handleCancel, isLoading } = useSwapTransaction();

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
      fromMessage={fromMessage}
      onCancelSwap={handleCancel}
      onSubmitSwap={handleSwap}
      isLoading={isLoading}
    />
  );
};
