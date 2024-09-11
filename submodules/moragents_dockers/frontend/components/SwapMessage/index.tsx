import React, { FC } from "react";
import { SwapForm } from "../SwapForm";
import { SwapMessagePayload } from "../../services/backendClient";

type SwapMessageProps = {
  isActive: boolean;
  onCancelSwap: (fromAction: number) => void;
  selectedAgent: string;
  fromMessage: SwapMessagePayload;
  onSubmitSwap: (swapTx: any) => void;
};

export const SwapMessage: FC<SwapMessageProps> = ({
  isActive,
  onCancelSwap,
  selectedAgent,
  fromMessage,
  onSubmitSwap,
}) => {
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
