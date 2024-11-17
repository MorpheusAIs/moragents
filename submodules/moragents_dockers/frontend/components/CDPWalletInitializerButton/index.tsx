import React, { useState } from 'react';
import {
  Button,
  Flex,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Text,
  Box,
} from "@chakra-ui/react";
import { FaWallet, FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import { initializeCDPWallet, getHttpClient } from '../../services/backendClient';

const CDPWalletInitializerButton = () => {

  const [isInitializing, setIsInitializing] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleInitializeWallet = async () => {
    setIsInitializing(true);
    const backendClient = getHttpClient();
    
    try {

      await initializeCDPWallet(backendClient);
      
      setIsSuccess(true);
      setFeedbackMessage("Wallet initialized successfully!");
    } catch (error) {
      console.error("Error initializing wallet:", error);
      setIsSuccess(false);
      setFeedbackMessage("Failed to initialize wallet. Please try again.");
    } finally {
      setIsInitializing(false);
      onOpen();
    }
  };

  return (
    <Flex direction="column" align="center" maxW="md" mx="auto" p={4}>
      <Button
        leftIcon={<FaWallet />}
        onClick={handleInitializeWallet}
        isLoading={isInitializing}
        loadingText="Initializing..."
        colorScheme="blue"
        size="lg"
        width="full"
        height="48px"
      >
        Initialize CDP Wallet
      </Button>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isSuccess ? "Success" : "Error"}</ModalHeader>
          <ModalBody>
            <Flex align="center">
              {isSuccess ? (
                <FaCheckCircle color="green" size={24} />
              ) : (
                <FaTimesCircle color="red" size={24} />
              )}
              <Text ml={3}>{feedbackMessage}</Text>
            </Flex>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme={isSuccess ? "green" : "red"}
              mr={3}
              onClick={onClose}
            >
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Flex>
  );
};

export default CDPWalletInitializerButton;