import React, { FC, useState } from "react";
import {
  Grid,
  GridItem,
  Text,
  Textarea,
  Button,
  Flex,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@chakra-ui/react";
import { ChatMessage, SwapMessagePayload } from "../../services/backendClient";
import { Avatar } from "../Avatar";
import { availableAgents } from "../../config";
import { SwapMessage } from "../SwapMessage";
import { UserOrAssistantMessage } from "../../services/backendClient";
import { FaPaperPlane, FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import { postTweet, getHttpClient } from "../../services/backendClient";
import styles from "./index.module.css";

type MessageItemProps = {
  message: ChatMessage;
  selectedAgent: string;
  onCancelSwap: (fromAction: number) => void;
  onSwapSubmit: (swapTx: any) => void;
  isLastSwapMessage: boolean;
};

export const MessageItem: FC<MessageItemProps> = ({
  message,
  selectedAgent,
  onCancelSwap,
  onSwapSubmit,
  isLastSwapMessage,
}) => {
  const [tweetContent, setTweetContent] = useState(
    (message as UserOrAssistantMessage).content || ""
  );
  const [isTweeting, setIsTweeting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleTweet = async () => {
    setIsTweeting(true);
    const backendClient = getHttpClient(selectedAgent);

    try {
      await postTweet(backendClient, tweetContent);
      setIsSuccess(true);
      setFeedbackMessage("Tweet sent successfully!");
    } catch (error) {
      console.error("Error sending tweet:", error);
      setIsSuccess(false);
      setFeedbackMessage("Failed to send tweet. Please try again.");
    } finally {
      setIsTweeting(false);
      onOpen();
    }
  };

  return (
    <>
      <Grid
        templateAreas={`
          "avatar name"
          "avatar message"
        `}
        templateColumns={"0fr 3fr"}
        className={styles.messageGrid}
      >
        <GridItem area="avatar">
          <Avatar
            isAgent={message.role !== "user"}
            agentName={
              availableAgents[selectedAgent]?.name || "Undefined Agent"
            }
          />
        </GridItem>
        <GridItem area="name">
          <Text className={styles.nameText}>
            {message.role === "user"
              ? "Me"
              : availableAgents[selectedAgent]?.name || "Undefined Agent"}
          </Text>
        </GridItem>
        <GridItem area="message">
          {typeof message.content === "string" ? (
            (message as UserOrAssistantMessage).agentName ===
            "tweet sizzler agent" ? (
              <Flex direction="column" align="center">
                <Textarea
                  value={tweetContent}
                  onChange={(e) => setTweetContent(e.target.value)}
                  className={styles.textarea}
                />
                <Button
                  leftIcon={<FaPaperPlane />}
                  onClick={handleTweet}
                  isLoading={isTweeting}
                  loadingText="Tweeting..."
                  colorScheme="twitter"
                  size="sm"
                  className={styles.tweetButton}
                >
                  Tweet
                </Button>
              </Flex>
            ) : (
              <Text className={styles.messageText}>{message.content}</Text>
            )
          ) : (
            <SwapMessage
              isActive={isLastSwapMessage}
              onCancelSwap={onCancelSwap}
              selectedAgent={selectedAgent}
              fromMessage={message.content as SwapMessagePayload}
              onSubmitSwap={onSwapSubmit}
            />
          )}
        </GridItem>
      </Grid>

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
    </>
  );
};
