export type ChatMessageBase = {
  role: "user" | "assistant" | "swap" | "claim";
  agentName: string;
};

export type UserOrAssistantMessage = ChatMessageBase & {
  role: "user" | "assistant";
  content: string;
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

export type ImageMessageContent = {
  success: boolean;
  service: string;
  image: string;
  error?: string;
};

export type ImageMessage = ChatMessageBase & {
  role: "image";
  content: ImageMessageContent;
};

export type CryptoDataMessageContent = {
  data: string;
  coinId: string;
};

export type CryptoDataMessage = ChatMessageBase & {
  role: "crypto_data";
  content: CryptoDataMessageContent;
};

export type BaseMessageContent = {
  message: string;
  actionType?: string;
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

export type ChatMessage =
  | UserOrAssistantMessage
  | SwapMessage
  | SystemMessage
  | ClaimMessage
  | ImageMessage;

export type ChatsListItem = {
  index: number;
  title: string;
};

export interface XApiKeys {
  api_key: string;
  api_secret: string;
  access_token: string;
  access_token_secret: string;
  bearer_token: string;
}

export interface CoinbaseApiKeys {
  cdp_api_key: string;
  cdp_api_secret: string;
}
