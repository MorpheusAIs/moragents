import type { NextPage } from "next";
import { Box, Flex, useBreakpointValue } from "@chakra-ui/react";
import { LeftSidebar } from "@/components/LeftSidebar";
import { Chat } from "@/components/Chat";
import {
  writeMessage,
  getMessagesHistory,
  deleteConversation,
  addMessageToHistory,
} from "@/services/chat_management/sessions";
import { sendSwapStatus, uploadFile } from "@/services/apiHooks";
import { getHttpClient, SWAP_STATUS } from "@/services/constants";
import { ChatMessage } from "@/services/types";
import { useEffect, useState } from "react";
import { useAccount, useChainId } from "wagmi";
import { HeaderBar } from "@/components/HeaderBar";

const Home: NextPage = () => {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [currentConversationId, setCurrentConversationId] =
    useState<string>("default");
  const chainId = useChainId();
  const { address } = useAccount();
  const [showBackendError, setShowBackendError] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const isMobile = useBreakpointValue({ base: true, md: false });

  useEffect(() => {
    if (!isMobile) {
      setIsSidebarOpen(true);
    }
  }, [isMobile]);

  // Load messages whenever the conversation ID changes
  useEffect(() => {
    const messages = getMessagesHistory(currentConversationId);
    setChatHistory(messages);
  }, [currentConversationId]);

  const handleSubmitMessage = async (message: string, file: File | null) => {
    try {
      if (!file) {
        // Handle text message
        const newHistory = await writeMessage(
          message,
          getHttpClient(),
          chainId,
          address || "",
          currentConversationId
        );
        setChatHistory(newHistory);
      } else {
        // Handle file upload
        const response = await uploadFile(getHttpClient(), file);

        // Add file upload message to local storage
        if (response.data.message) {
          addMessageToHistory(response.data.message, currentConversationId);
          setChatHistory(getMessagesHistory(currentConversationId));
        }
      }
    } catch (e) {
      console.error(`Failed to send message. Error: ${e}`);
      setShowBackendError(true);
    }

    return true;
  };

  const handleDeleteConversation = async (conversationId: string) => {
    try {
      deleteConversation(conversationId);
      if (conversationId === currentConversationId) {
        setCurrentConversationId("default");
      }
    } catch (e) {
      console.error(`Failed to delete conversation. Error: ${e}`);
      setShowBackendError(true);
    }
  };

  const handleCancelSwap = async (fromAction: number) => {
    if (!address) return;

    try {
      const response = await sendSwapStatus(
        getHttpClient(),
        chainId,
        address,
        SWAP_STATUS.CANCELLED,
        "",
        fromAction
      );

      // Add cancel message to local storage
      if (response) {
        addMessageToHistory(response, currentConversationId);
        setChatHistory(getMessagesHistory(currentConversationId));
      }
    } catch (e) {
      console.error(`Failed to cancel swap or update messages. Error: ${e}`);
      setShowBackendError(true);
    }
  };

  return (
    <Box
      sx={{
        backgroundColor: "#000",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        width: "100%",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <HeaderBar />
      <Flex flex="1" overflow="hidden" position="relative">
        <Box
          position={isMobile ? "absolute" : "relative"}
          left={0}
          top={0}
          height="100%"
          zIndex={2}
          transform={
            isMobile ? `translateX(${isSidebarOpen ? "0" : "-100%"})` : "none"
          }
          transition="transform 0.3s ease"
        >
          <LeftSidebar
            isSidebarOpen={isSidebarOpen}
            onToggleSidebar={setIsSidebarOpen}
            currentConversationId={currentConversationId}
            setCurrentConversationId={setCurrentConversationId}
            onConversationSelect={setCurrentConversationId}
            onDeleteConversation={handleDeleteConversation}
          />
        </Box>

        <Box
          flex="1"
          overflow="hidden"
          ml={isMobile ? 0 : isSidebarOpen ? "240px" : 0}
          transition="margin 0.3s ease"
        >
          <Chat
            messages={chatHistory}
            onCancelSwap={handleCancelSwap}
            onSubmitMessage={handleSubmitMessage}
            onBackendError={() => setShowBackendError(true)}
            isSidebarOpen={isSidebarOpen}
            setIsSidebarOpen={setIsSidebarOpen}
          />
        </Box>
      </Flex>
    </Box>
  );
};

export default Home;
