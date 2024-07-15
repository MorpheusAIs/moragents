import React, { FC, useCallback, useEffect, useMemo, useState } from "react";
import { Box, Flex, Input, Button, Text, HStack, InputGroup, InputRightAddon, IconButton, Icon, Grid, GridItem, InputLeftAddon } from "@chakra-ui/react";
import { Avatar } from "../Avatar";
import { ChatMessage, SwapTxPayloadType, ApproveTxPayloadType, SwapMessagePayload, sendSwapStatus, getHttpClient, UserOrAssistantMessage, SWAP_STATUS } from "../../services/backendClient";
import { SwapForm } from "../SwapForm";
import { useAccount, useCall, useChainId, useSendTransaction, useTransactionConfirmations } from "wagmi";
import { availableAgents } from "../../config";
import { SendIcon } from "../CustomIcon/SendIcon";
import { Loader } from "../Loader";
import { on } from "events";
import { AttachmentIcon } from "@chakra-ui/icons";

export type ChatProps = {
    onSubmitMessage: (message: string, file: File | null) => Promise<boolean>;
    onCancelSwap: (fromAction: number) => void;
    messages: ChatMessage[];
    selectedAgent: string;
    onBackendError: () => void;
};

export const Chat: FC<ChatProps> = ({
    onSubmitMessage,
    onCancelSwap,
    messages,
    selectedAgent,
    onBackendError,
}) => {
    const [message, setMessage] = useState('');
    const [messagesData, setMessagesData] = useState<ChatMessage[]>(messages);
    const [countSwapsMessages, setCountSwapsMessages] = useState<number>(0);


    const [file, setFile] = useState<File | null>(null);

    const { address } = useAccount();
    const chainId = useChainId();


    useEffect(() => {
        setMessagesData([...messages]);

        const swapsMessages = messages.filter((message) => message.role === 'swap');

        setCountSwapsMessages(swapsMessages.length);
    }, [messages]);

    const [txHash, setTxHash] = useState<string>(``);
    const [approveTxHash, setApproveTxHash] = useState<string>(``);
    const [callbackSent, setCallbackSent] = useState<boolean>(false);
    const [showSpinner, setShowSpinner] = useState<boolean>(false);

    const confirmatons = useTransactionConfirmations({
        hash: (txHash || '0x') as `0x${string}`,
    });

    const approveConfirmations = useTransactionConfirmations({
        hash: (approveTxHash || '0x') as `0x${string}`,
    });

    const agentSupportsFileUploads = useMemo(() => {
        return availableAgents[selectedAgent]?.supportsFiles || false;
    }, [selectedAgent]);

    useEffect(() => {
        if (null === file) return;


        setMessage(`File selected: ${file.name}, click send button to upload it.`);
    }, [file]);

    useEffect(() => {
        if (approveTxHash === '') {
            return;
        }

        if (approveTxHash !== '' && approveConfirmations.data && approveConfirmations.data >= 1) {
            sendSwapStatus(
                getHttpClient(selectedAgent),
                chainId,
                address?.toLowerCase() || '0x',
                SWAP_STATUS.SUCCESS,
                approveTxHash,
                1
            ).then((response: ChatMessage) => {
                setMessagesData([...messagesData, {
                    role: 'assistant',
                    content: response.content,
                } as UserOrAssistantMessage]);

                setApproveTxHash('');
            }).catch((error) => {
                setApproveTxHash('');
                console.log(`Error sending approve status: ${error}`);

                onBackendError();
            });
        }

    }, [approveTxHash, approveConfirmations, selectedAgent, chainId, address, messagesData, onBackendError]);

    useEffect(() => {
        if (!callbackSent && confirmatons.data && confirmatons.data >= 1) {
            setCallbackSent(true);
            setShowSpinner(true);
            sendSwapStatus(
                getHttpClient(selectedAgent),
                chainId,
                address?.toLowerCase() || '0x',
                SWAP_STATUS.SUCCESS,
                txHash,
                0
            ).then((response: ChatMessage) => {
                setMessagesData([...messagesData, {
                    role: 'assistant',
                    content: response.content,
                } as UserOrAssistantMessage]);

                setTxHash('');
                setCallbackSent(false);
                setShowSpinner(false);
            }).catch((error) => {
                console.log(`Error sending swap status: ${error}`);
                setTxHash('');
                setCallbackSent(false);
                setShowSpinner(false);
                onBackendError();
            });
        }
    }, [confirmatons, callbackSent, chainId, selectedAgent, address, messagesData, onBackendError]);

    const { sendTransaction } = useSendTransaction();

    const isMostRecentSwapMessage = useCallback((message: ChatMessage) => {
        const swapsMessages = messagesData.filter((message) => message.role === 'swap');
        // const msgIndex = messagesData.findIndex((msg) => msg.content === message.content);

        // if (msgIndex !== messagesData.length - 1) {
        //     return false;
        // }

        if (message.role === 'swap') {
            const isLastMessage = messagesData[messagesData.length - 1]?.content === message.content;

            if (!isLastMessage) {
                const anotherSwapMessagesExists = swapsMessages.length > 1;

                if (!anotherSwapMessagesExists) {
                    return true;
                }
            }
        }

        return swapsMessages[swapsMessages.length - 1] === message;
    }, [messagesData]);

    const handleSubmit = async () => {
        if (!message) {
            return;
        }

        setShowSpinner(true);

        await onSubmitMessage(message, file);
        setMessage('');
        setFile(null); // Clear the file state after upload
        setShowSpinner(false);
    }

    return (
        <div style={{
            width: '65%'
        }}>
            <Box flex="1" bg="#020804" p={4} sx={{

                overflowY: 'scroll',
                overflowX: 'hidden',
                height: 'calc(100vh - 200px)',
                '::-webkit-scrollbar': {
                    width: '8px',
                    backgroundColor: 'transparent',
                },
                '::-webkit-scrollbar-thumb': {
                    backgroundColor: '#111613',
                    borderRadius: '4px',
                },
                ... ((availableAgents[selectedAgent]?.requirements.connectedWallet && !address) ? {
                    pointerEvents: 'none',

                } : {})
            }}>
                {messagesData.map((message: ChatMessage, index) => (
                    <Grid
                        templateAreas={`
                        "avatar name"
                        "avatar message"
                    `}
                        templateColumns={'0fr 3fr'}
                        key={index} bg={'#020804'}
                        color={'white'}
                        borderRadius={4}
                        mb={2}
                        gap={2}
                    >
                        <GridItem area="avatar">
                            <Avatar isAgent={message.role !== 'user'} agentName={availableAgents[selectedAgent]?.name || 'Undefined Agent'} />
                        </GridItem>
                        <GridItem area="name">
                            <Text sx={{
                                fontSize: '16px',
                                fontWeight: 'bold',
                                lineHeight: '125%',
                                mt: 1,
                                ml: 2

                            }}>{message.role === 'user' ? 'Me' : availableAgents[selectedAgent]?.name || 'Undefined Agent'}</Text>
                        </GridItem>

                        <GridItem area={'message'}>

                            {
                                typeof message.content === 'string' ?
                                    <Text
                                        sx={{
                                            fontSize: '16px',
                                            lineHeight: '125%',
                                            mt: 4,
                                            mb: 5,
                                            ml: 2,
                                        }}
                                    >{message.content}</Text> : <SwapForm
                                        isActive={isMostRecentSwapMessage(message)}
                                        onCancelSwap={onCancelSwap}
                                        selectedAgent={selectedAgent}
                                        fromMessage={message.content as unknown as SwapMessagePayload}
                                        onSubmitApprove={(approveTx) => {
                                            setTxHash('');
                                            sendTransaction({
                                                account: address,
                                                data: (approveTx?.data || '0x') as `0x${string}`,
                                                to: (approveTx?.to || '0x') as `0x${string}`,
                                            }, {
                                                onSuccess: (hash) => {
                                                    sendSwapStatus(
                                                        getHttpClient(selectedAgent),
                                                        chainId,
                                                        address?.toLowerCase() || '0x',
                                                        SWAP_STATUS.INIT,
                                                        hash,
                                                        1
                                                    ).then((response: ChatMessage) => {
                                                        setMessagesData([...messagesData, {
                                                            role: 'assistant',
                                                            content: response.content,
                                                        } as UserOrAssistantMessage]);
                                                    }).catch((error) => {
                                                        console.log(`Error sending swap status: ${error}`);
                                                        onBackendError();
                                                    });
                                                    setApproveTxHash(hash);

                                                },
                                                onError: (error) => {
                                                    console.log(`Error sending transaction: ${error}`);
                                                    sendSwapStatus(
                                                        getHttpClient(selectedAgent),
                                                        chainId,
                                                        address?.toLowerCase() || '0x',
                                                        SWAP_STATUS.FAIL,
                                                        '',
                                                        1
                                                    ).then((response: ChatMessage) => {
                                                        setMessagesData([...messagesData, {
                                                            role: 'assistant',
                                                            content: response.content,
                                                        } as UserOrAssistantMessage]);
                                                    }).catch((error) => {
                                                        console.log(`Error sending swap status: ${error}`);
                                                        onBackendError();
                                                    });
                                                }
                                            });
                                        }}
                                        onSubmitSwap={(swapTx) => {
                                            setTxHash('');
                                            sendTransaction({
                                                account: address,
                                                data: (swapTx?.tx.data || '0x') as `0x${string}`,
                                                to: (swapTx?.tx.to || '0x') as `0x${string}`,
                                                value: BigInt(swapTx?.tx.value || "0"),
                                            }, {
                                                onSuccess: (hash) => {
                                                    setTxHash(hash);

                                                    sendSwapStatus(
                                                        getHttpClient(selectedAgent),
                                                        chainId,
                                                        address?.toLowerCase() || '0x',
                                                        SWAP_STATUS.INIT,
                                                        hash,
                                                        0
                                                    ).then((response: ChatMessage) => {
                                                        setMessagesData([...messagesData, {
                                                            role: 'assistant',
                                                            content: response.content,
                                                        } as UserOrAssistantMessage]);
                                                    }).catch((error) => {
                                                        console.log(`Error sending swap status: ${error}`);
                                                        onBackendError();
                                                    });
                                                },
                                                onError: (error) => {
                                                    console.log(`Error sending transaction: ${error}`);
                                                    sendSwapStatus(
                                                        getHttpClient(selectedAgent),
                                                        chainId,
                                                        address?.toLowerCase() || '0x',
                                                        SWAP_STATUS.FAIL,
                                                        '',
                                                        0
                                                    ).then((response: ChatMessage) => {
                                                        setMessagesData([...messagesData, {
                                                            role: 'assistant',
                                                            content: response.content,
                                                        } as UserOrAssistantMessage]);
                                                    }).catch((error) => {
                                                        console.log(`Error sending swap status: ${error}`);
                                                        onBackendError();
                                                    });
                                                }
                                            });
                                        }}
                                    />
                            }
                        </GridItem>
                    </Grid>
                ))}

                {showSpinner && <Grid
                    templateAreas={`
                        "avatar name"
                        "avatar message"
                    `}
                    templateColumns={'0fr 3fr'}
                    bg={'#020804'}
                    color={'white'}
                    borderRadius={4}
                    mb={2}
                    gap={2}
                >
                    <GridItem area="avatar">
                        <Avatar isAgent={true} agentName={availableAgents[selectedAgent]?.name || 'Undefined Agent'} />
                    </GridItem>
                    <GridItem area="name">
                        <Text sx={{
                            fontSize: '16px',
                            fontWeight: 'bold',
                            lineHeight: '125%',
                            mt: 1,
                            ml: 2

                        }}>{availableAgents[selectedAgent]?.name || 'Undefined Agent'}</Text>
                    </GridItem>

                    <GridItem area={'message'}>
                        <Box sx={{
                            fontSize: '16px',
                            lineHeight: '125%',
                            mt: 4,
                            mb: 5,
                            ml: 2,
                        }}>
                            <Loader />
                        </Box>
                    </GridItem>
                </Grid>}
            </Box>

            <Flex mt={4} sx={{
                pl: 6,
                pr: 6
            }}>
                <InputGroup sx={{
                    pt: 2,
                    pb: 2,
                    borderRadius: '8px',
                    backgroundColor: '#353936',
                }}>
                    {agentSupportsFileUploads && (
                        <InputLeftAddon
                            sx={{
                                backgroundColor: 'transparent',
                                border: 'none',
                                color: '#59F886',
                                cursor: 'pointer',
                            }}
                            onClick={() => {
                                const input = document.querySelector('input[type="file"]');

                                if (input) {
                                    // @ts-ignore
                                    input?.click();
                                }
                            }}
                        >
                            <input
                                style={{
                                    display: 'none',
                                }}
                                type="file"
                                accept=".pdf"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];

                                    if (!file) {
                                        return;
                                    }

                                    setFile(file);
                                }}
                            />
                            <AttachmentIcon sx={{
                                color: file !== null ? '#6C6C6C' : 'innerhit',
                            }} />
                        </InputLeftAddon>
                    )}
                    <Input
                        onKeyDown={(e) => {
                            if (showSpinner || messagesData[messagesData.length - 1]?.role === 'swap') {
                                return;
                            }

                            if (e.altKey && e.key === 'Enter') {
                                setMessage(message + '\n');
                            } else if (e.key === 'Enter') {
                                handleSubmit();
                            }
                        }}
                        sx={{
                            border: 'none',
                            color: 'white',
                            '&:focus': {
                                borderColor: 'none !important',
                                boxShadow: 'none !important',
                            }
                        }}
                        disabled={file !== null || messagesData[messagesData.length - 1]?.role === 'swap' || showSpinner}
                        value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Type your message here..." />
                    <InputRightAddon

                        sx={{
                            backgroundColor: 'transparent',
                            border: 'none',
                            pointerEvents: showSpinner ? 'none' : 'auto',
                        }}>
                        <IconButton
                            sx={{
                                backgroundColor: 'transparent',
                                fontSize: '24px',
                                color: '#59F886',
                                "&:hover": {
                                    backgroundColor: 'transparent',
                                },
                            }}
                            disabled={showSpinner}
                            aria-label="Send" onClick={handleSubmit} icon={
                                <SendIcon width="24px" height="24px" />
                            } />
                    </InputRightAddon>
                </InputGroup>
            </Flex>
        </div>
    );
}