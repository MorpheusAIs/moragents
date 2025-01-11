// Widgets.tsx
import React, { FC } from "react";
import { Box, IconButton, Text } from "@chakra-ui/react";
import { X } from "lucide-react";
import { ChatMessage } from "@/services/types";
import { ImageDisplay } from "@/components/Agents/Imagen/ImageDisplayMessage";
import TradingViewWidget from "./TradingViewWidget";
import DCAWidget from "./DCAWidget";
import BaseSwapWidget from "./BaseSwapWidget";
import BaseTransferWidget from "./BaseTransferWidget";
import OneInchSwapWidget from "./OneInchSwapWidget";
export const WIDGET_COMPATIBLE_AGENTS = [
  "imagen",
  "crypto data",
  "dca",
  "base",
  "token swap",
];

export const shouldOpenWidget = (message: ChatMessage) => {
  if (!message.agentName) return false;

  if (message.agentName === "base") {
    if (
      message.requires_action &&
      ["transfer", "swap"].includes(message.action_type || "")
    ) {
      return true;
    }
    return false;
  }

  if (message.agentName === "dca") {
    return message.requires_action;
  }

  if (message.agentName === "token swap") {
    return (
      message.requires_action && message.metadata?.src && message.metadata?.dst
    );
  }

  if (message.agentName === "crypto data") {
    return (
      WIDGET_COMPATIBLE_AGENTS.includes(message.agentName) &&
      message.metadata?.coinId
    );
  }

  return WIDGET_COMPATIBLE_AGENTS.includes(message.agentName);
};

interface WidgetsProps {
  activeWidget: ChatMessage | null;
  onClose: () => void;
}

export const Widgets: FC<WidgetsProps> = ({ activeWidget, onClose }) => {
  const renderWidget = () => {
    if (
      activeWidget?.role === "assistant" &&
      activeWidget.agentName === "imagen" &&
      activeWidget.metadata?.image
    ) {
      console.log("Imagen widget metadata:", activeWidget.metadata);
      return (
        <Box p={4}>
          <ImageDisplay imageMetadata={activeWidget.metadata} />
        </Box>
      );
    }

    if (
      activeWidget?.role === "assistant" &&
      activeWidget.agentName === "crypto data"
    ) {
      if (!activeWidget.metadata?.coinId) return null;
      return (
        <Box
          h="full"
          w="full"
          display="flex"
          flexDirection="column"
          flexGrow={1}
        >
          <TradingViewWidget
            symbol={`${activeWidget.metadata.coinId.toUpperCase()}`}
          />
        </Box>
      );
    }

    if (
      activeWidget?.role === "assistant" &&
      activeWidget.agentName === "dca"
    ) {
      return (
        <Box
          h="full"
          w="full"
          display="flex"
          flexDirection="column"
          flexGrow={1}
        >
          <DCAWidget />
        </Box>
      );
    }

    if (
      activeWidget?.role === "assistant" &&
      activeWidget.agentName === "base" &&
      activeWidget.requires_action
    ) {
      if (
        !activeWidget.action_type ||
        !["transfer", "swap"].includes(activeWidget.action_type)
      ) {
        return null;
      }

      return (
        <Box
          h="full"
          w="full"
          display="flex"
          flexDirection="column"
          flexGrow={1}
        >
          {activeWidget.action_type === "transfer" ? (
            <BaseTransferWidget />
          ) : (
            <BaseSwapWidget />
          )}
        </Box>
      );
    }

    if (
      activeWidget?.role === "assistant" &&
      activeWidget.agentName === "token swap" &&
      activeWidget.requires_action &&
      activeWidget.action_type === "swap" &&
      activeWidget.metadata
    ) {
      return (
        <Box
          h="full"
          w="full"
          display="flex"
          flexDirection="column"
          flexGrow={1}
        >
          <OneInchSwapWidget metadata={activeWidget.metadata} />
        </Box>
      );
    }

    return null;
  };

  return (
    <Box
      w="full"
      h="100%"
      bg="#020804"
      borderRadius="md"
      overflow="auto"
      position="relative"
      mt={16}
      display="flex"
      flexDirection="column"
      alignItems="center"
      flexGrow={1}
    >
      <Text
        fontSize="2xl"
        fontWeight="bold"
        color="white"
        mt={4}
        mb={8}
        textAlign="center"
        flexShrink={0}
      >
        Agent Widgets
      </Text>
      <IconButton
        aria-label="Close widgets"
        icon={<X />}
        onClick={onClose}
        position="absolute"
        top={2}
        right={4}
        bg="white"
        _hover={{ bg: "gray.300" }}
        zIndex={1}
        flexShrink={0}
      />
      <Box w="full" h="100%" display="flex" flexDirection="column" flexGrow={1}>
        {renderWidget()}
      </Box>
    </Box>
  );
};
