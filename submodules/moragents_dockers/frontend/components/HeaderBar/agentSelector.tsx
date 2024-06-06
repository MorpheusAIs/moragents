import { Box, CheckboxIcon, HStack, Icon, Spacer, Text, VStack } from '@chakra-ui/react';
import React, { FC, ComponentPropsWithoutRef, useState } from 'react';
import { useOutsideClick } from '@chakra-ui/react';
import { CheckIcon, ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons'
import { availableAgents } from '../../config';

interface AgentSelectorProps extends ComponentPropsWithoutRef<'div'> {
    onSelectedAgent: (agent: string) => void;
    selectedAgent?: string;
}

const AgentSelectorItem: FC<{ selected: boolean, agent: string, agentDescription: string, showDelimiter: boolean, onSelectAgent: (agent: string) => void }> = ({ selected, agent, agentDescription, showDelimiter = true, onSelectAgent }) => {
    const handleAgentSelection = () => {
        onSelectAgent(agent);
    }

    return (
        <Box sx={{
            backgroundColor: '#1C201D',
            textColor: 'gray.100',
            padding: '10px 8px',
            cursor: 'pointer',
            gap: '10px',
            ':hover': {
                backgroundColor: '#1C201D',
            },
            textAlign: 'left',
            borderBottom: showDelimiter ? '1px solid rgba(103, 107, 104, 0.12)' : 'none',
        }}
            onClick={(e) => {
                console.log('Clicked agent:', agent);
                handleAgentSelection();
            }}
        >
            <VStack sx={{
                textAlign: 'left',
            }}
            >
                <HStack width={'full'} alignItems="center" justifyContent={'space-between'}>
                    <Text align={'left'}
                        sx={{
                            fontWeight: 600,
                        }}
                    >{availableAgents[agent].name}</Text>
                    <Spacer />
                    {selected && <CheckIcon sx={{
                        fontWeight: 400,
                    }} />}
                </HStack>
                <HStack width={'full'}>
                    <Text sx={{
                        fontSize: '12px',
                        fontWeight: 400,
                    }}>{agentDescription || ''}</Text>
                </HStack>
            </VStack>
        </Box>
    );
}

export const AgentSelector: FC<AgentSelectorProps> = ({ onSelectedAgent, selectedAgent }: AgentSelectorProps) => {
    const [show, setShow] = React.useState(false);

    const ref = React.useRef<HTMLDivElement>(null);

    const handleAgentSelected = (agent: string) => {
        setShow(false);
        onSelectedAgent(agent);
    }

    useOutsideClick({
        ref: ref,
        handler: () => {
            setShow(false);
        }

    })

    return (
        <>
            <Box sx={{
                backgroundColor: 'transparent',
                borderRadius: '5px',
                border: '1px solid #9A9C9B',
                padding: '10px 10px 10px 10px',
                cursor: 'pointer',
                minWidth: '260px',
                textColor: '#9A9C9B',
                userSelect: 'none',
            }} onClick={() => {
                setShow(show ? false : true)
            }}>
                <HStack>
                    <Text align={'left'}>
                        {availableAgents[(selectedAgent || 'none')]?.name || 'Select Agent'}
                    </Text>
                    <Spacer />
                    {show ? <ChevronUpIcon /> : <ChevronDownIcon />}
                </HStack>
            </Box>
            {show && <Box ref={ref} sx={{
                position: 'absolute',
                backgroundColor: '#1C201D',
                padding: '4px 8px',
                boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.25)',
                gap: '8px',
                zIndex: 1,
                textAlign: 'left',
                width: '15vw',
            }}>
                {availableAgents && Object.keys(availableAgents).map((agent, index) => {
                    return (
                        <AgentSelectorItem agent={agent}
                            key={`agent-${agent}`}
                            selected={selectedAgent === agent}
                            agentDescription={availableAgents[agent].description}
                            showDelimiter={index < Object.keys(availableAgents).length - 1}
                            onSelectAgent={(agent) => {
                                console.log('Selected agent:', agent);
                                handleAgentSelected(agent);
                            }}
                        />
                    );
                })}
            </Box>
            }

        </>
    );
}