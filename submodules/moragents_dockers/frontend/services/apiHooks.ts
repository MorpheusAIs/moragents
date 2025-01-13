import { Axios } from "axios";
import {
  ChatMessage,
  UserMessage,
  ClaimTransactionPayload,
  SwapTxPayloadType,
  XCredentials,
  CoinbaseCredentials,
  OneInchCredentials,
} from "./types";

export const getChats = async () => {
  const chats = localStorage.getItem("chats");
  if (chats) {
    return JSON.parse(chats);
  }
  return [];
};

export const getAllowance = async (
  backendClient: Axios,
  chainId: number,
  tokenAddress: string,
  walletAddress: string
) => {
  return await backendClient.post("/swap/allowance", {
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
  return await backendClient.post("/swap/approve", {
    chain_id: chainId,
    tokenAddress: tokenAddress,
    amount: BigInt(amount * 10 ** decimals).toString(),
  });
};

export const uploadFile = async (backendClient: Axios, file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  console.log("Uploading file:", file);
  return await backendClient.post("/rag/upload", formData, {
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
    await backendClient.post("/swap/swap", {
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
  try {
    const responseBody = await backendClient.post("/swap/tx_status", {
      status: swapStatus,
      tx_hash: txHash || "",
      tx_type: swapType === 0 ? "swap" : "approve",
      chain_id: chainId,
      wallet_address: walletAddress,
    });

    return {
      role: responseBody.data.role,
      content: responseBody.data.content,
      agentName: responseBody.data.agentName,
      error_message: responseBody.data.error_message,
      metadata: responseBody.data.metadata,
      requires_action: responseBody.data.requires_action,
      action_type: responseBody.data.action_type,
      timestamp: responseBody.data.timestamp,
    } as ChatMessage;
  } catch (error: unknown) {
    console.error("Failed to send swap status:", error);
    return {
      role: "assistant",
      content: "Failed to process transaction status update",
      error_message: error instanceof Error ? error.message : String(error),
      timestamp: Date.now(),
    } as ChatMessage;
  }
};

export const getMessagesHistory = async (
  backendClient: Axios,
  conversationId: string = "default"
): Promise<ChatMessage[]> => {
  const responseBody = await backendClient.get("/chat/messages", {
    params: {
      conversation_id: conversationId,
    },
  });

  return responseBody.data.messages.map((message: any) => {
    return {
      role: message.role,
      content: message.content,
      agentName: message.agentName,
      error_message: message.error_message,
      metadata: message.metadata,
      requires_action: message.requires_action,
      action_type: message.action_type,
      timestamp: message.timestamp,
    } as ChatMessage;
  });
};

export const clearMessagesHistory = async (
  backendClient: Axios,
  conversationId: string = "default"
): Promise<void> => {
  try {
    await backendClient.get("/chat/clear", {
      params: {
        conversation_id: conversationId,
      },
    });
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
  address: string,
  conversationId: string = "default"
) => {
  const newMessage: UserMessage = {
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
      conversation_id: conversationId,
    });
  } catch (e) {
    console.error(e);
  }

  return await getMessagesHistory(backendClient, conversationId);
};

export const createNewConversation = async (
  backendClient: Axios
): Promise<string> => {
  const response = await backendClient.post("/chat/conversations");
  return response.data.conversation_id;
};

export const deleteConversation = async (
  backendClient: Axios,
  conversationId: string
): Promise<void> => {
  await backendClient.delete(`/chat/conversations/${conversationId}`);
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
    await backendClient.post("/tweet/post", {
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
    const response = await backendClient.post("/tweet/regenerate");
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
  const response = await backendClient.post("/claim/claim", { transactions });
  return response.data.transactions;
};

export const sendClaimStatus = async (
  backendClient: Axios,
  chainId: number,
  walletAddress: string,
  claimStatus: string,
  txHash?: string
): Promise<ChatMessage> => {
  const responseBody = await backendClient.post("/claim/tx_status", {
    chain_id: chainId,
    wallet_address: walletAddress,
    status: claimStatus,
    tx_hash: txHash || "",
    tx_type: "claim",
  });

  return {
    role: responseBody.data.role,
    content: responseBody.data.content,
    agentName: responseBody.data.agentName,
    error_message: responseBody.data.error_message,
    metadata: responseBody.data.metadata,
    requires_action: responseBody.data.requires_action,
    action_type: responseBody.data.action_type,
    timestamp: responseBody.data.timestamp,
  } as ChatMessage;
};

export const getAvailableAgents = async (backendClient: Axios) => {
  try {
    const response = await backendClient.get("/agents/available");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch available agents:", error);
    throw error;
  }
};

export const setSelectedAgents = async (
  backendClient: Axios,
  agents: string[]
) => {
  try {
    const response = await backendClient.post("/agents/selected", {
      agents,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to set selected agents:", error);
    throw error;
  }
};

export const setXCredentials = async (
  backendClient: Axios,
  keys: XCredentials
): Promise<{ status: string; message: string }> => {
  try {
    const response = await backendClient.post("/keys/x", keys);
    return response.data;
  } catch (error) {
    console.error("Failed to set X API keys:", error);
    throw error;
  }
};

export const setCoinbaseCredentials = async (
  backendClient: Axios,
  keys: CoinbaseCredentials
): Promise<{ status: string; message: string }> => {
  try {
    const response = await backendClient.post("/keys/coinbase", keys);
    return response.data;
  } catch (error) {
    console.error("Failed to set Coinbase API keys:", error);
    throw error;
  }
};

export const setOneInchCredentials = async (
  backendClient: Axios,
  keys: OneInchCredentials
): Promise<{ status: string; message: string }> => {
  try {
    const response = await backendClient.post("/keys/1inch", {
      api_key: keys.api_key,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to set 1inch API keys:", error);
    throw error;
  }
};
