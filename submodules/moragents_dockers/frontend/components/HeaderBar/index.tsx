import React, { FC, useState } from "react";
import Image from "next/image";
import { Box, HStack, Spacer, Button, ButtonGroup } from "@chakra-ui/react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { SettingsButton } from "@/components/Settings";
import { CDPWallets } from "./CDPWallets";
import { Workflows } from "./Workflows";
import classes from "./index.module.css";
import { clearMessagesHistory } from "@/services/apiHooks";
import { getHttpClient } from "@/services/constants";
import { useRouter } from "next/router";

export const HeaderBar: FC = () => {
  const backendClient = getHttpClient();
  const router = useRouter();
  const [walletType, setWalletType] = useState<"cdp" | "metamask">("cdp");

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
          <Workflows />
          <SettingsButton />
          {walletType === "cdp" ? <CDPWallets /> : <ConnectButton />}

          {/* Wallet Selection */}
          <ButtonGroup isAttached>
            <Button
              onClick={() => setWalletType("cdp")}
              variant={walletType === "cdp" ? "greenCustom" : "ghost"}
              color={walletType === "cdp" ? "black" : "white"}
              sx={{
                "&:hover": {
                  transform: "none",
                  backgroundColor: "#90EE90",
                },
                backgroundColor: walletType === "cdp" ? undefined : "gray.700",
              }}
            >
              CDP Managed Wallets
            </Button>
            <Button
              onClick={() => setWalletType("metamask")}
              variant={walletType === "metamask" ? "greenCustom" : "ghost"}
              color={walletType === "metamask" ? "black" : "white"}
              sx={{
                "&:hover": {
                  transform: "none",
                  backgroundColor: "#90EE90",
                },
                backgroundColor:
                  walletType === "metamask" ? undefined : "gray.700",
              }}
            >
              Metamask
            </Button>
          </ButtonGroup>
        </HStack>
      </HStack>
    </Box>
  );
};
