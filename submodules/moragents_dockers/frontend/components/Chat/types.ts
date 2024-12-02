import { ChatMessage } from "@/services/types";

export type ChatProps = {
  onSubmitMessage: (message: string, file: File | null) => Promise<boolean>;
  onCancelSwap: (fromAction: number) => void;
  messages: ChatMessage[];
  selectedAgent: string;
  onBackendError: () => void;
};

export type SwapTransaction = {
  tx: {
    data: string;
    to: string;
    value: string;
  };
};
