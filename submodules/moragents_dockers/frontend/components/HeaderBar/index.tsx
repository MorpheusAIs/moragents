import React, { FC, ComponentPropsWithoutRef } from 'react';
import Image from 'next/image';
import { Box, HStack, Spacer } from '@chakra-ui/react';
import { AgentSelector } from './agentSelector';
import { ConnectButton } from '@rainbow-me/rainbowkit';

export interface HeaderBarProps extends ComponentPropsWithoutRef<'div'> {
    onAgentChanged(agent: string): void;
    currentAgent: string;
}

export const HeaderBar: FC<HeaderBarProps> = (props) => {
    return (
        <Box bgColor={'header'} sx={{
            // height: '6.25vh',
            padding: '10px 10px 10px 10px',
            borderBottom: '1px solid #313137',
            zIndex: 1401,
        }}
        >
            <HStack sx={{

            }}>
                <Box sx={{
                    mr: '200px',

                }}>
                    <Image src='/assets/logo.svg' alt="logo" width={60} height={30} />
                </Box>

                <Box>
                    <AgentSelector onSelectedAgent={(agent) => {
                        props.onAgentChanged(agent);
                    }}
                        selectedAgent={props.currentAgent}
                    />
                </Box>
                <Spacer />
                <Box>
                    <ConnectButton />
                </Box>
            </HStack>
        </Box >
    );
};