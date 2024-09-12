import React, { FC, useState, useEffect } from "react";
import {
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
  Text,
  Box,
} from "@chakra-ui/react";
import { FaPaperPlane, FaCheckCircle, FaTimesCircle } from "react-icons/fa";
import { postTweet, getHttpClient } from "../../services/backendClient";
import styles from "./index.module.css";

type TweetProps = {
  initialContent: string;
  selectedAgent: string;
};

const MAX_TWEET_LENGTH = 280;

export const Tweet: FC<TweetProps> = ({ initialContent, selectedAgent }) => {
  const [tweetContent, setTweetContent] = useState(initialContent);
  const [isTweeting, setIsTweeting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [charactersLeft, setCharactersLeft] = useState(
    MAX_TWEET_LENGTH - initialContent.length
  );

  useEffect(() => {
    setCharactersLeft(MAX_TWEET_LENGTH - tweetContent.length);
  }, [tweetContent]);

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
      <Flex direction="column" align="center">
        <Textarea
          value={tweetContent}
          onChange={(e) => setTweetContent(e.target.value)}
          className={styles.textarea}
          maxLength={MAX_TWEET_LENGTH}
        />
        <Flex
          justifyContent="space-between"
          alignItems="center"
          width="100%"
          mt={1}
          mb={2}
        >
          <Box>
            <Text
              fontSize="sm"
              className={styles.charactersLeft}
              color={charactersLeft < 0 ? "red.500" : "gray.500"}
            >
              {charactersLeft} characters left
            </Text>
          </Box>
          <Button
            leftIcon={<FaPaperPlane />}
            onClick={handleTweet}
            isLoading={isTweeting}
            loadingText="Tweeting..."
            colorScheme="twitter"
            size="sm"
            className={styles.tweetButton}
            isDisabled={charactersLeft < 0 || tweetContent.length === 0}
          >
            Tweet
          </Button>
        </Flex>
      </Flex>

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
