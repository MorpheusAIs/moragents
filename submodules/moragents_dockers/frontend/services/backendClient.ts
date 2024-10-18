import axios, { Axios } from "axios";

export type ChatMessageBase = {
  role: "user" | "assistant" | "swap" | "claim";
};

export type UserOrAssistantMessage = ChatMessageBase & {
  role: "user" | "assistant";
  content: string;
  agentName?: string;
};

export const SWAP_STATUS = {
  CANCELLED: "cancelled",
  SUCCESS: "success",
  FAIL: "failed",
  INIT: "initiated",
};

export const CLAIM_STATUS = {
  SUCCESS: "success",
  FAIL: "failed",
  INIT: "initiated",
};

export type SwapTxPayloadType = {
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

export type ApproveTxPayloadType = {
  data: string;
  gasPrice: string;
  to: string;
  value: string;
};

export type SwapMessagePayload = {
  amount: string;
  dst: string;
  dst_address: string;
  dst_amount: string | number;
  quote: string;
  src: string;
  src_address: string;
  src_amount: string | number;
};

export type SwapMessage = ChatMessageBase & {
  role: "swap";
  content: SwapMessagePayload;
};

export type SystemMessage = ChatMessageBase & {
  role: "system";
  content: string;
};

export type ClaimTransactionPayload = {
  to: string;
  data: string;
  value: string;
  gas: string;
  chainId: string;
};

export type ClaimMessagePayload = {
  content: {
    transactions: {
      pool: number;
      transaction: ClaimTransactionPayload;
    }[];
    claim_tx_cb: string;
  };
  role: "claim";
};

export type ClaimMessage = ChatMessageBase & {
  role: "claim";
  content: ClaimMessagePayload;
};

// Update the ChatMessage type to include ClaimMessage
export type ChatMessage =
  | UserOrAssistantMessage
  | SwapMessage
  | SystemMessage
  | ClaimMessage;

export type ChatsListItem = {
  index: number; //  index at chats array
  title: string; // title of the chat (first message content)
};

export const getHttpClient = () => {
  return axios.create({
    baseURL: "http://localhost:8080",
  });
};

export const getChats = async () => {
  // now chats will be stored at local storage

  const chats = localStorage.getItem("chats");
  if (chats) {
    return JSON.parse(chats);
  }

  return [];
};

//

export const getAllowance = async (
  backendClient: Axios,
  chainId: number,
  tokenAddress: string,
  walletAddress: string
) => {
  return await backendClient.post("/allowance", {
    chain_id: chainId,
    tokenAddress: tokenAddress,
    walletAddress: walletAddress,
  });
};

export const getApprovalTxPayload = async (
  backendClient: Axios,
  chainId: number,
  tokenAddress: string,
  amount: number,
  decimals: number
) => {
  return await backendClient.post("/approve", {
    chain_id: chainId,
    tokenAddress: tokenAddress,
    amount: BigInt(amount * 10 ** decimals).toString(),
  });
};

export const uploadFile = async (backendClient: Axios, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  console.log("Uploading file:", file);
  return await backendClient.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const getSwapTxPayload = async (
  backendClient: Axios,
  token0: string,
  token1: string,
  walletAddress: string,
  amount: number,
  slippage: number,
  chainId: number,
  decimals: number
): Promise<SwapTxPayloadType> => {
  return (
    await backendClient.post("/swap", {
      src: token0,
      dst: token1,
      walletAddress: walletAddress,
      amount: BigInt(amount * 10 ** decimals).toString(),
      slippage: slippage,
      chain_id: chainId,
    })
  ).data;
};

export const sendSwapStatus = async (
  backendClient: Axios,
  chainId: number,
  walletAddress: string,
  swapStatus: string,
  txHash?: string,
  swapType?: number
): Promise<ChatMessage> => {
  const responseBody = await backendClient.post("/tx_status", {
    chain_id: chainId,
    wallet_address: walletAddress,
    status: swapStatus,
    tx_hash: txHash || "",
    tx_type: swapType === 0 ? "swap" : "approve", // 0 is swap, 1 is approve
  });

  return {
    role: responseBody.data.role,
    content: responseBody.data.content,
  } as ChatMessage;
};

export const getMessagesHistory = async (
  backendClient: Axios
): Promise<ChatMessage[]> => {
  const responseBody = await backendClient.get("/messages");

  return responseBody.data.messages.map((message: any) => {
    return {
      role: message.role,
      content: message.content,
      agentName: message.agentName,
    } as ChatMessage;
  });
};

export const clearMessagesHistory = async (
  backendClient: Axios
): Promise<void> => {
  try {
    await backendClient.get("/clear_messages");
  } catch (error) {
    console.error("Failed to clear message history:", error);
    throw error;
  }
};

export const writeMessage = async (
  history: ChatMessage[],
  message: string,
  backendClient: Axios,
  chainId: number,
  address: string
) => {
  const newMessage: ChatMessage = {
    role: "user",
    content: message,
  };

  history.push(newMessage);
  let resp;
  try {
    resp = await backendClient.post("/chat", {
      prompt: {
        role: "user",
        content: message,
      },
      chain_id: String(chainId),
      wallet_address: address,
    });
  } catch (e) {
    console.error(e);

    // resp = {
    //     data: {
    //         content: "Sorry, I'm not available right now. Please try again later."
    //     }
    // };
  } finally {
    console.log("Finally write message");
    // history.push({
    //     role: 'assistant',
    //     content: resp?.data.content || "Unknown error occurred."
    // });
  }

  return await getMessagesHistory(backendClient);
};

export const postTweet = async (
  backendClient: Axios,
  content: string
): Promise<void> => {
  const apiKey = localStorage.getItem("apiKey");
  const apiSecret = localStorage.getItem("apiSecret");
  const accessToken = localStorage.getItem("accessToken");
  const accessTokenSecret = localStorage.getItem("accessTokenSecret");
  const bearerToken = localStorage.getItem("bearerToken");

  if (
    !apiKey ||
    !apiSecret ||
    !accessToken ||
    !accessTokenSecret ||
    !bearerToken
  ) {
    throw new Error(
      "X API credentials not found. Please set them in the settings."
    );
  }

  try {
    await backendClient.post("/post_tweet", {
      post_content: content,
      api_key: apiKey,
      api_secret: apiSecret,
      access_token: accessToken,
      access_token_secret: accessTokenSecret,
      bearer_token: bearerToken,
    });
  } catch (error) {
    console.error("Error posting tweet:", error);
    throw error;
  }
};

export const regenerateTweet = async (
  backendClient: Axios
): Promise<string> => {
  try {
    const response = await backendClient.post("/regenerate_tweet");
    return response.data;
  } catch (error) {
    console.error("Error regenerating tweet:", error);
    throw error;
  }
};

export const getClaimTxPayload = async (
  backendClient: Axios,
  transactions: ClaimTransactionPayload[]
): Promise<ClaimTransactionPayload[]> => {
  const response = await backendClient.post("/claim", { transactions });
  return response.data.transactions;
};

export const sendClaimStatus = async (
  backendClient: Axios,
  chainId: number,
  walletAddress: string,
  claimStatus: string,
  txHash?: string
): Promise<ChatMessage> => {
  const responseBody = await backendClient.post("/tx_status", {
    chain_id: chainId,
    wallet_address: walletAddress,
    status: claimStatus,
    tx_hash: txHash || "",
    tx_type: "claim",
  });

  return {
    role: responseBody.data.role,
    content: responseBody.data.content,
  } as ChatMessage;
};
