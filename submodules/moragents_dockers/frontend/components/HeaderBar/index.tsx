import React, { FC } from "react";
import Image from "next/image";
import { Box, HStack, Spacer } from "@chakra-ui/react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import classes from "./index.module.css";

export const HeaderBar: FC = () => {
  return (
    <Box className={classes.headerBar}>
      <HStack spacing={4} width="100%" px={4}>
        <Box className={classes.logo} flexShrink={0}>
          <Image src="/assets/logo.svg" alt="logo" width={60} height={30} />
        </Box>
        <Spacer />
        <Box className={classes.connectButtonWrapper}>
          <ConnectButton />
        </Box>
      </HStack>
    </Box>
  );
};
