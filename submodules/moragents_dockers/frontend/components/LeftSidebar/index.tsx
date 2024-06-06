import React, { FC } from 'react';
import {
    Box,
    VStack,
    Text,
    Link
} from "@chakra-ui/react";
import { ConnectButton } from '@rainbow-me/rainbowkit';


export type LeftSidebarProps = {

};

export const LeftSidebar: FC<LeftSidebarProps> = () => {
    return (
        <Box bg="#020804" p={4}>
            <VStack align="stretch" height="85%">

                {/* Dynamic chat list can be added here */}
            </VStack>
        </Box>
    );
}