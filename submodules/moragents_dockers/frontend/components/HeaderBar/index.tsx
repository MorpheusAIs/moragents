import React, { FC, ComponentPropsWithoutRef } from 'react';
import Image from 'next/image';
import { Box, HStack, Spacer } from '@chakra-ui/react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { availableAgents } from '../../config';

export interface HeaderBarProps extends ComponentPropsWithoutRef<'div'> {
    onAgentChanged(agent: string): void;
    currentAgent: string;
}

export const HeaderBar: FC<HeaderBarProps> = (props) => {
    const defaultAgent = 'swap-agent'; // Set your default agent here
    const selectedAgent = availableAgents[defaultAgent];

    return (
        <Box bgColor={'header'} sx={{
            padding: '10px 10px 10px 10px',
            borderBottom: '1px solid #313137',
            zIndex: 1401,
        }}>
            <HStack>
                <Box sx={{ mr: '200px' }}>
                    <Image src='/assets/logo.svg' alt="logo" width={60} height={30} />
                </Box>
                <Box>
                    <Spacer />
                </Box>
                <Spacer />
                <Box>
                    <ConnectButton />
                </Box>
            </HStack>
        </Box>
    );
};