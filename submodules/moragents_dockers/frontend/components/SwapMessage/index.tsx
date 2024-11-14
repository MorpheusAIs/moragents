import React, { FC } from "react";
import { SwapForm } from "../SwapForm";
import { SwapMessagePayload } from "../../services/backendClient";
import { Box, Text } from "@chakra-ui/react";
import { useSendTransaction } from 'wagmi';

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
  const { sendTransaction } = useSendTransaction();

  const handleApprove = async (txData: ApproveTxPayloadType) => {
    console.log('Received approve tx data:', txData);
    try {
      if (!txData || !txData.to) {
        console.error('Invalid transaction data:', txData);
        return;
      }

      const tx = await sendTransaction({
        to: txData.to,
        data: txData.data,
        value: txData.value,
        gasPrice: txData.gasPrice
      });
      console.log('Approve transaction sent:', tx);
    } catch (error) {
      console.error('Error sending approve transaction:', error);
    }
  };

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
      onSubmitApprove={handleApprove}
      onSubmitSwap={onSubmitSwap}
    />
  );
};
