import { Text } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import {
  ChatMessage,
  ImageMessageContent,
  CryptoDataMessageContent,
  AssistantMessage,
} from "@/services/types";
import {
  AgentType,
  BaseAgentActionType,
  isValidAgentType,
} from "@/services/types";

import { Tweet } from "@/components/Agents/Tweet/CustomMessages/TweetMessage";
import { TopTokensMessage } from "@/components/Agents/Dexscreener/CustomMessages/TopTokensMessage";
import CryptoChartMessage from "@/components/Agents/CryptoData/CryptoChartMessage";
import DCAMessage from "@/components/Agents/DCA/DCAMessage";
import BaseTransferMessage from "@/components/Agents/Base/TransferMessage";
import BaseSwapMessage from "@/components/Agents/Base/SwapMessage";
import OneInchSwapMessage from "@/components/Agents/Swaps/SwapMessage";

type MessageRenderer = {
  check: (message: ChatMessage) => boolean;
  render: (message: ChatMessage) => React.ReactNode;
};

const messageRenderers: MessageRenderer[] = [
  // Error message renderer
  {
    check: (message) => !!message.error_message,
    render: (message) => <Text color="red.500">{message.error_message}</Text>,
  },

  // Imagen agent renderer
  {
    check: (message) => message.agentName === AgentType.IMAGEN,
    render: (message) => {
      const imageContent = (message as AssistantMessage)
        .content as ImageMessageContent;
      if (!imageContent.success) {
        return (
          <Text color="red.500">
            {imageContent.error || "Failed to generate image"}
          </Text>
        );
      }
      return (
        <ReactMarkdown>{`Successfully generated image with ${imageContent.service}`}</ReactMarkdown>
      );
    },
  },

  // Crypto data agent renderer
  {
    check: (message) => message.agentName === AgentType.CRYPTO_DATA,
    render: (message) => {
      const assistantMessage = message as AssistantMessage;
      return (
        <CryptoChartMessage
          content={assistantMessage.content as CryptoDataMessageContent}
          metadata={assistantMessage.metadata}
        />
      );
    },
  },

  // Base agent renderers
  {
    check: (message) =>
      message.agentName === AgentType.BASE_AGENT &&
      message.action_type === BaseAgentActionType.TRANSFER,
    render: (message) => (
      <BaseTransferMessage
        content={message.content}
        metadata={message.metadata}
      />
    ),
  },
  {
    check: (message) =>
      message.agentName === AgentType.BASE_AGENT &&
      message.action_type === BaseAgentActionType.SWAP,
    render: (message) => (
      <BaseSwapMessage content={message.content} metadata={message.metadata} />
    ),
  },

  // Token swap agent renderer
  {
    check: (message) => message.agentName === AgentType.TOKEN_SWAP,
    render: (message) => (
      <OneInchSwapMessage
        content={message.content}
        metadata={message.metadata || {}}
      />
    ),
  },

  // Dexscreener agent renderer
  {
    check: (message) => message.agentName === AgentType.DEXSCREENER,
    render: (message) => (
      <TopTokensMessage metadata={(message as AssistantMessage).metadata} />
    ),
  },

  // DCA agent renderer
  {
    check: (message) => message.agentName === AgentType.DCA_AGENT,
    render: (message) => (
      <DCAMessage
        content={message.content}
        metadata={(message as AssistantMessage).metadata}
      />
    ),
  },

  // Tweet sizzler agent renderer
  {
    check: (message) =>
      typeof message.content === "string" &&
      message.agentName === AgentType.TWEET_SIZZLER,
    render: (message) => <Tweet initialContent={message.content as string} />,
  },

  // Default string content renderer
  {
    check: (message) => typeof message.content === "string",
    render: (message) => (
      <ReactMarkdown>{message.content as string}</ReactMarkdown>
    ),
  },

  // Fallback renderer
  {
    check: () => true,
    render: (message) => <Text>{JSON.stringify(message.content)}</Text>,
  },
];

/**
 * Renders a chat message using the appropriate renderer based on the message type and agent.
 *
 * @param message The chat message to render
 * @returns The rendered React node, or null if no renderer is found
 */
export const renderMessage = (message: ChatMessage): React.ReactNode => {
  // Validate agent type if present
  if (message.agentName && !isValidAgentType(message.agentName)) {
    console.warn(`Invalid agent type: ${message.agentName}`);
  }

  const renderer = messageRenderers.find((r) => r.check(message));
  return renderer ? renderer.render(message) : null;
};
