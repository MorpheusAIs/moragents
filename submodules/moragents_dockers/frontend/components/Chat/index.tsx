import React, { FC, useCallback, useEffect, useState } from "react";
import { Box } from "@chakra-ui/react";
import {
  ChatMessage,
  ClaimMessage,
  ClaimMessagePayload,
  ClaimTransactionPayload,
  sendClaimStatus,
  sendSwapStatus,
  getHttpClient,
  SWAP_STATUS,
  CLAIM_STATUS,
} from "../../services/backendClient";
import {
  useAccount,
  useChainId,
  useSendTransaction,
  useTransactionConfirmations,
} from "wagmi";
import { MessageList } from "../MessageList";
import { ChatInput } from "../ChatInput";
import { LoadingIndicator } from "../LoadingIndicator";
import {
  UserOrAssistantMessage,
  SwapMessage,
} from "../../services/backendClient";

export type ChatProps = {
  onSubmitMessage: (message: string, file: File | null) => Promise<boolean>;
  onCancelSwap: (fromAction: number) => void;
  messages: ChatMessage[];
  selectedAgent: string;
  onBackendError: () => void;
};

export const Chat: FC<ChatProps> = ({
  onSubmitMessage,
  onCancelSwap,
  messages,
  selectedAgent,
  onBackendError,
}) => {
  const [messagesData, setMessagesData] = useState<ChatMessage[]>(messages);
  const [showSpinner, setShowSpinner] = useState<boolean>(false);
  const [txHash, setTxHash] = useState<string>("");
  const [approveTxHash, setApproveTxHash] = useState<string>("");

  const { address } = useAccount();
  const chainId = useChainId();
  const { sendTransaction } = useSendTransaction();

  const confirmatons = useTransactionConfirmations({
    hash: (txHash || "0x") as `0x${string}`,
  });

  const approveConfirmations = useTransactionConfirmations({
    hash: (approveTxHash || "0x") as `0x${string}`,
  });

  useEffect(() => {
    setMessagesData([...messages]);
  }, [messages]);

  const handleSwapStatus = useCallback(
    async (status: string, hash: string, isApprove: number) => {
      try {
        const response: ChatMessage = await sendSwapStatus(
          getHttpClient(),
          chainId,
          address?.toLowerCase() || "0x",
          status,
          hash,
          isApprove
        );

        if (
          response.role === "assistant" &&
          typeof response.content === "string"
        ) {
          setMessagesData((prev) => [
            ...prev,
            {
              role: "assistant",
              content: response.content,
            } as UserOrAssistantMessage,
          ]);
        } else if (response.role === "swap") {
          setMessagesData((prev) => [...prev, response as SwapMessage]);
        }

        if (isApprove) {
          setApproveTxHash("");
        } else {
          setTxHash("");
        }
        setShowSpinner(false);
      } catch (error) {
        console.log(
          `Error sending ${isApprove ? "approve" : "swap"} status: ${error}`
        );
        onBackendError();
        if (isApprove) {
          setApproveTxHash("");
        } else {
          setTxHash("");
        }
        setShowSpinner(false);
      }
    },
    [selectedAgent, chainId, address, onBackendError]
  );

  useEffect(() => {
    if (
      approveTxHash &&
      approveConfirmations.data &&
      approveConfirmations.data >= 1
    ) {
      handleSwapStatus(SWAP_STATUS.SUCCESS, approveTxHash, 1);
    }
  }, [approveTxHash, approveConfirmations.data, handleSwapStatus]);

  useEffect(() => {
    if (txHash && confirmatons.data && confirmatons.data >= 1) {
      setShowSpinner(true);
      handleSwapStatus(SWAP_STATUS.SUCCESS, txHash, 0);
    }
  }, [txHash, confirmatons.data, handleSwapStatus]);

  const handleSubmit = async (message: string, file: File | null) => {
    setShowSpinner(true);
    await onSubmitMessage(message, file);
    setShowSpinner(false);
  };

  const handleSwapSubmit = useCallback(
    (swapTx: any) => {
      setTxHash("");
      sendTransaction(
        {
          account: address,
          data: (swapTx?.tx.data || "0x") as `0x${string}`,
          to: (swapTx?.tx.to || "0x") as `0x${string}`,
          value: BigInt(swapTx?.tx.value || "0"),
        },
        {
          onSuccess: (hash) => {
            setTxHash(hash);
            handleSwapStatus(SWAP_STATUS.INIT, hash, 0);
          },
          onError: (error) => {
            console.log(`Error sending transaction: ${error}`);
            handleSwapStatus(SWAP_STATUS.FAIL, "", 0);
          },
        }
      );
    },
    [address, handleSwapStatus, sendTransaction]
  );

  const handleClaimStatus = useCallback(
    async (status: string, hash: string) => {
      try {
        const response: ChatMessage = await sendClaimStatus(
          getHttpClient(),
          chainId,
          address?.toLowerCase() || "0x",
          status,
          hash
        );

        if (
          response.role === "assistant" &&
          typeof response.content === "string"
        ) {
          setMessagesData((prev) => [
            ...prev,
            {
              role: "assistant",
              content: response.content,
            } as UserOrAssistantMessage,
          ]);
        } else if (response.role === "claim") {
          setMessagesData((prev) => [...prev, response as ClaimMessage]);
        }

        setTxHash("");
        setShowSpinner(false);
      } catch (error) {
        console.log(`Error sending claim status: ${error}`);
        onBackendError();
        setTxHash("");
        setShowSpinner(false);
      }
    },
    [selectedAgent, chainId, address, onBackendError]
  );

  // Add this near your other useTransactionConfirmations hooks
  const claimConfirmations = useTransactionConfirmations({
    hash: (txHash || "0x") as `0x${string}`,
  });

  // Add this effect to watch for claim transaction confirmations
  useEffect(() => {
    if (txHash && claimConfirmations.data && claimConfirmations.data >= 1) {
      handleClaimStatus(CLAIM_STATUS.SUCCESS, txHash);
    }
  }, [txHash, claimConfirmations.data, handleClaimStatus]);

  // Modify handleClaimSubmit to use the same txHash state
  const handleClaimSubmit = useCallback(
    (claimTx: ClaimTransactionPayload) => {
      setTxHash("");
      console.log("Claim transaction to be sent:", claimTx);
      sendTransaction(
        {
          account: address,
          data: claimTx.data as `0x${string}`,
          to: claimTx.to as `0x${string}`,
          value: BigInt(claimTx.value),
          chainId: parseInt(claimTx.chainId),
        },
        {
          onSuccess: (hash) => {
            setTxHash(hash);
            handleClaimStatus(CLAIM_STATUS.INIT, hash);
          },
          onError: (error) => {
            console.log(`Error sending transaction: ${error}`);
            handleClaimStatus(CLAIM_STATUS.FAIL, "");
          },
        }
      );
    },
    [address, handleClaimStatus, sendTransaction]
  );

  return (
    <Box width="65%">
      <MessageList
        messages={messagesData}
        selectedAgent={selectedAgent}
        onCancelSwap={onCancelSwap}
        onSwapSubmit={handleSwapSubmit}
        onClaimSubmit={handleClaimSubmit}
      />
      {showSpinner && <LoadingIndicator selectedAgent={selectedAgent} />}
      <ChatInput
        onSubmit={handleSubmit}
        selectedAgent={selectedAgent}
        disabled={
          showSpinner || messagesData[messagesData.length - 1]?.role === "swap"
        }
      />
    </Box>
  );
};
