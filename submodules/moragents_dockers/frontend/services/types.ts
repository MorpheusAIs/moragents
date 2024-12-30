export type ChatMessageBase = {
  role: string;
  content: string | any;
  agentName?: string;
  error_message?: string;
  metadata?: Record<string, any>;
  requires_action?: boolean;
  action_type?: string;
  timestamp?: number;
};

export type UserMessage = ChatMessageBase & {
  role: "user";
  content: string;
};

export type AssistantMessage = ChatMessageBase & {
  role: "assistant";
  content:
    | string
    | ImageMessageContent
    | CryptoDataMessageContent
    | BaseMessageContent
    | SwapMessagePayload
    | ClaimMessagePayload;
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

export type ImageMessageContent = {
  success: boolean;
  service: string;
  image: string;
  error?: string;
};

export type CryptoDataMessageContent = {
  data: string;
  coinId: string;
};

export type BaseMessageContent = {
  message: string;
  actionType?: string;
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

export type ChatMessage = UserMessage | AssistantMessage;

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
