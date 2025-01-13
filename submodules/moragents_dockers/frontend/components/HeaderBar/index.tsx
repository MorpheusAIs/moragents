import React, { FC, useState } from "react";
import Image from "next/image";
import { Box, HStack, Spacer, Button, ButtonGroup } from "@chakra-ui/react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { CDPWallets } from "@/components/CDPWallets";
import classes from "./index.module.css";

export const HeaderBar: FC = () => {
  const [walletType, setWalletType] = useState<"cdp" | "metamask">("cdp");

  return (
    <Box className={classes.headerBar}>
      <HStack spacing={4} width="100%" px={4}>
        <Box className={classes.logo} flexShrink={0}>
          <Image src="/assets/logo.svg" alt="logo" width={60} height={30} />
        </Box>
        <Spacer />
        <HStack spacing={4} flexShrink={0}>
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
