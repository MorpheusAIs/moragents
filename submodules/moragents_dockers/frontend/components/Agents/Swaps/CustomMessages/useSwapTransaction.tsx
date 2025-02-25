import { useState, useCallback } from "react";
import { useAccount, useChainId, useSendTransaction } from "wagmi";
import { sendSwapStatus } from "@/services/apiHooks";
import { getHttpClient, SWAP_STATUS } from "@/services/constants";

type SwapTx = {
  dstAmount: string;
  tx: {
    data: string;
    from: string;
    gas: number;
    gasPrice: string;
    to: string;
    value: string;
  };
};

export const useSwapTransaction = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [txHash, setTxHash] = useState("");
  const { address } = useAccount();
  const chainId = useChainId();
  const { sendTransaction } = useSendTransaction();

  const handleSwap = useCallback(
    async (swapTx: SwapTx) => {
      if (!address) return;

      setIsLoading(true);
      setTxHash("");

      try {
        // Convert value to Wei (multiply by 10^18) before converting to BigInt
        const valueInWei = Math.floor(
          Number(swapTx.tx.value) * 1e18
        ).toString();

        sendTransaction(
          {
            account: address,
            data: (swapTx.tx.data || "0x") as `0x${string}`,
            to: (swapTx.tx.to || "0x") as `0x${string}`,
            value: BigInt(valueInWei),
          },
          {
            onSuccess: async (hash) => {
              setTxHash(hash);
              await sendSwapStatus(
                getHttpClient(),
                chainId,
                address.toLowerCase(),
                SWAP_STATUS.INIT,
                hash,
                0
              );
            },
            onError: async (error) => {
              console.error(`Error sending transaction: ${error}`);
              await sendSwapStatus(
                getHttpClient(),
                chainId,
                address.toLowerCase(),
                SWAP_STATUS.FAIL,
                "",
                0
              );
              setIsLoading(false);
            },
            onSettled: () => setIsLoading(false),
          }
        );
      } catch (error) {
        setIsLoading(false);
        console.error("Swap failed:", error);
      }
    },
    [address, chainId, sendTransaction]
  );

  const handleCancel = useCallback(
    async (fromAction: number) => {
      if (!address) return;

      try {
        await sendSwapStatus(
          getHttpClient(),
          chainId,
          address.toLowerCase(),
          SWAP_STATUS.CANCELLED,
          "",
          fromAction
        );
      } catch (error) {
        console.error(`Failed to cancel swap: ${error}`);
      }
    },
    [address, chainId]
  );

  return {
    handleSwap,
    handleCancel,
    isLoading,
    txHash,
  };
};
