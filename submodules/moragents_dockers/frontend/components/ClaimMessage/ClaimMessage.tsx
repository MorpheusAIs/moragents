import React, { FC } from "react";
import { ClaimForm } from "../ClaimForm/ClaimForm";
import { ClaimMessagePayload } from "../../services/backendClient";

type ClaimMessageProps = {
  isActive: boolean;
  selectedAgent: string;
  fromMessage: ClaimMessagePayload;
  onSubmitClaim: (claimTx: any) => void;
};

export const ClaimMessage: FC<ClaimMessageProps> = ({
  isActive,
  selectedAgent,
  fromMessage,
  onSubmitClaim,
}) => {
  console.log("ClaimMessage received fromMessage:", fromMessage);
  if (!fromMessage) {
    return <div>Error: Claim message data is not available.</div>;
  }

  return (
    <ClaimForm
      isActive={isActive}
      selectedAgent={selectedAgent}
      fromMessage={fromMessage}
      onSubmitClaim={onSubmitClaim}
    />
  );
};