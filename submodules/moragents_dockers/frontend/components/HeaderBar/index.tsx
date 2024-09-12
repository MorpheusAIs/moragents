import React, { FC, ComponentPropsWithoutRef } from "react";
import Image from "next/image";
import { Box, HStack, Spacer } from "@chakra-ui/react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import SettingsButton from "../Settings";
import classes from "./index.module.css";

export interface HeaderBarProps extends ComponentPropsWithoutRef<"div"> {
  onAgentChanged(agent: string): void;
  currentAgent: string;
}

export const HeaderBar: FC<HeaderBarProps> = (props) => {
  return (
    <Box className={classes.headerBar}>
      <HStack>
        <Box className={classes.logo}>
          <Image src="/assets/logo.svg" alt="logo" width={60} height={30} />
        </Box>
        <Spacer />
        <Box className={classes.buttonContainer}>
          <SettingsButton />
          <ConnectButton />
        </Box>
      </HStack>
    </Box>
  );
};
