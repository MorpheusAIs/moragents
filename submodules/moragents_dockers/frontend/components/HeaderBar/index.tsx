import React, { FC, ComponentPropsWithoutRef } from "react";
import Image from "next/image";
import { Box, HStack, Spacer, Button } from "@chakra-ui/react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { SettingsButton } from "../Settings";
import classes from "./index.module.css";
import {
  getHttpClient,
  clearMessagesHistory,
} from "../../services/backendClient";
import { useRouter } from "next/router";

export interface HeaderBarProps extends ComponentPropsWithoutRef<"div"> {
  onAgentChanged(agent: string): void;
  currentAgent: string;
}

export const HeaderBar: FC<HeaderBarProps> = (props) => {
  const backendClient = getHttpClient();
  const router = useRouter();

  const handleClearChatHistory = async () => {
    try {
      await clearMessagesHistory(backendClient);
      router.reload();
    } catch (error) {
      console.error("Failed to clear chat history:", error);
    }
  };

  return (
    <Box className={classes.headerBar}>
      <HStack spacing={4} width="100%" px={4}>
        <Box className={classes.logo} flexShrink={0}>
          <Image src="/assets/logo.svg" alt="logo" width={60} height={30} />
        </Box>
        <Spacer />
        <HStack spacing={4} flexShrink={0}>
          <Button onClick={handleClearChatHistory}>Clear Chat History</Button>
          <Box>
            <SettingsButton />
          </Box>
          <Box>
            <ConnectButton />
          </Box>
        </HStack>
      </HStack>
    </Box>
  );
};
