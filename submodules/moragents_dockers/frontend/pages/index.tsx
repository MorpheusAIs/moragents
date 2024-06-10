import { ConnectButton } from '@rainbow-me/rainbowkit';
import type { NextPage } from 'next';
import { Flex, Grid, GridItem } from '@chakra-ui/react';
import { LeftSidebar } from '../components/LeftSidebar';
import { Chat } from '../components/Chat';
import { writeMessage, getHttpClient, ChatMessage, getMessagesHistory, sendSwapStatus, SWAP_STATUS, uploadFile } from '../services/backendClient';
import { useEffect, useMemo, useState } from 'react';
import { useAccount, useChainId, useWalletClient } from 'wagmi';
import { HeaderBar } from '../components/HeaderBar';
import { availableAgents } from '../config';
import { WalletRequiredModal } from '../components/WalletRequiredModal';
import { ErrorBackendModal } from '../components/ErrorBackendModal';
import { get } from 'http';

const Home: NextPage = () => {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const chainId = useChainId();
  const { address } = useAccount();
  const [selectedAgent, setSelectedAgent] = useState<string>('swap-agent'); // default is swap agent for now. TODO ask what should be the default agent.
  const [showBackendError, setShowBackendError] = useState<boolean>(false);


  useEffect(() => {
    getMessagesHistory(
      getHttpClient(selectedAgent),
    ).then((messages: ChatMessage[]) => {
      setChatHistory([...messages])
    }).catch((e) => {
      console.error(`Failed to get initial messages history. Error: ${e}`);
      setShowBackendError(true);
    });
  }, [selectedAgent]);

  const isWalletRequired = useMemo(() => {
    const agent = availableAgents[selectedAgent] || null;

    if (null !== agent && agent.requirements.connectedWallet) {
      return true;
    }

    return false;
  }, [selectedAgent]);

  return (
    <div style={{
      backgroundColor: '#020804',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <HeaderBar
        onAgentChanged={(agent) => {
          setSelectedAgent(agent);
        }}
        currentAgent={selectedAgent || ''}
      />
      <Grid templateAreas={`
        "sidebar chat"
      `}

        gridTemplateColumns={`1fr 3fr`}

      >
        <GridItem area={'sidebar'} pl={2} pr={2}>
          <LeftSidebar />
        </GridItem>

        <GridItem pl={2} pr={2} area={'chat'}
          sx={{
          }}
        >
          <Chat selectedAgent={selectedAgent} messages={chatHistory}
            onCancelSwap={async (fromAction: number) => {
              // 0 is swap, 1 is approve

              if (!address) {
                return;
              }

              try {
                await sendSwapStatus(getHttpClient(selectedAgent), chainId, address, SWAP_STATUS.CANCELLED, '', fromAction);
              } catch (e) {
                console.error(`Failed to cancel swap . Error: ${e}`);
                setShowBackendError(true);

              } finally {
                try {
                  const _updatedMessages = await getMessagesHistory(
                    getHttpClient(selectedAgent),
                  )

                  setChatHistory([..._updatedMessages]);
                } catch (e) {
                  console.error(`Failed to get messages history after send swap status. Error: ${e}`);
                  setShowBackendError(true);
                }
              }



            }}
            onSubmitMessage={async (message: string, file: File | null): Promise<boolean> => {

              const agent = availableAgents[selectedAgent] || null;

              if (null !== agent && agent.requirements.connectedWallet) {
                if (!address) {
                  return true;
                }
              }

              setChatHistory([...chatHistory, {
                role: 'user',
                content: message
              } as ChatMessage]);
              let _newHistory = [];
              try {
                if (!file) {
                  _newHistory = await writeMessage(chatHistory, message, getHttpClient(selectedAgent), chainId, address || '');

                } else {
                  await uploadFile(
                    getHttpClient(selectedAgent),
                    file,
                  )

                  _newHistory = await getMessagesHistory(
                    getHttpClient(selectedAgent),
                  )
                }
                setChatHistory([..._newHistory])
              } catch (e) {
                console.error(`Failed to send message. Error: ${e}`);
                setShowBackendError(true);
              }

              return true;
            }}
            onBackendError={() => {
              setShowBackendError(true);
            }}
          />
        </GridItem>
        {/* <GridItem area={'rightbar'} pl={2} pr={2}>

        </GridItem> */}

      </Grid>

      {/* <Flex height="100vh" sx={{
        backgroundColor: '#020804'
      }}>

        <LeftSidebar />
        <Flex flex="1" flexDirection="column" p={4}>
          <Chat selectedAgent={selectedAgent} messages={chatHistory} onSubmitMessage={async (message: string) => {

            if (!address) {
              return;
            }

            const _newHistory = await writeMessage(chatHistory, message, getHttpClient(selectedAgent), chainId, address);

            setChatHistory([..._newHistory])
          }} />
        </Flex>
      </Flex> */}


      <WalletRequiredModal agentRequiresWallet={isWalletRequired} />
      <ErrorBackendModal show={showBackendError} />
    </div>
  );
};

export default Home;
