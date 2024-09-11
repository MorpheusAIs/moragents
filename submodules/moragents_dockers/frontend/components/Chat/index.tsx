import React, { FC, useCallback, useEffect, useState } from "react";
import { Box } from "@chakra-ui/react";
import {
  ChatMessage,
  sendSwapStatus,
  getHttpClient,
  SWAP_STATUS,
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
  const [callbackSent, setCallbackSent] = useState<boolean>(false);

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

  useEffect(() => {
    if (approveTxHash === "") {
      return;
    }

    if (
      approveTxHash !== "" &&
      approveConfirmations.data &&
      approveConfirmations.data >= 1
    ) {
      sendSwapStatus(
        getHttpClient(selectedAgent),
        chainId,
        address?.toLowerCase() || "0x",
        SWAP_STATUS.SUCCESS,
        approveTxHash,
        1
      )
        .then((response: ChatMessage) => {
          setMessagesData([
            ...messagesData,
            {
              role: "assistant",
              content: response.content,
              agentName: response.agentName,
            } as UserOrAssistantMessage,
          ]);

          setApproveTxHash("");
        })
        .catch((error) => {
          setApproveTxHash("");
          console.log(`Error sending approve status: ${error}`);

          onBackendError();
        });
    }
  }, [
    approveTxHash,
    approveConfirmations,
    selectedAgent,
    chainId,
    address,
    messagesData,
    onBackendError,
  ]);

  useEffect(() => {
    if (!callbackSent && confirmatons.data && confirmatons.data >= 1) {
      setCallbackSent(true);
      setShowSpinner(true);
      sendSwapStatus(
        getHttpClient(selectedAgent),
        chainId,
        address?.toLowerCase() || "0x",
        SWAP_STATUS.SUCCESS,
        txHash,
        0
      )
        .then((response: ChatMessage) => {
          setMessagesData([
            ...messagesData,
            {
              role: "assistant",
              content: response.content,
              agentName: "tweet_sizzler",
            } as UserOrAssistantMessage,
          ]);

          setTxHash("");
          setCallbackSent(false);
          setShowSpinner(false);
        })
        .catch((error) => {
          console.log(`Error sending swap status: ${error}`);
          setTxHash("");
          setCallbackSent(false);
          setShowSpinner(false);
          onBackendError();
        });
    }
  }, [
    confirmatons,
    callbackSent,
    chainId,
    selectedAgent,
    address,
    messagesData,
    onBackendError,
  ]);

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
            sendSwapStatus(
              getHttpClient(selectedAgent),
              chainId,
              address?.toLowerCase() || "0x",
              SWAP_STATUS.INIT,
              hash,
              0
            )
              .then((response: ChatMessage) => {
                setMessagesData([...messagesData, response]);
              })
              .catch((error) => {
                console.log(`Error sending swap status: ${error}`);
                onBackendError();
              });
          },
          onError: (error) => {
            console.log(`Error sending transaction: ${error}`);
            sendSwapStatus(
              getHttpClient(selectedAgent),
              chainId,
              address?.toLowerCase() || "0x",
              SWAP_STATUS.FAIL,
              "",
              0
            )
              .then((response: ChatMessage) => {
                setMessagesData([...messagesData, response]);
              })
              .catch((error) => {
                console.log(`Error sending swap status: ${error}`);
                onBackendError();
              });
          },
        }
      );
    },
    [
      address,
      chainId,
      messagesData,
      onBackendError,
      selectedAgent,
      sendTransaction,
    ]
  );

  return (
    <Box width="65%">
      <MessageList
        messages={messagesData}
        selectedAgent={selectedAgent}
        onCancelSwap={onCancelSwap}
        onSwapSubmit={handleSwapSubmit}
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
