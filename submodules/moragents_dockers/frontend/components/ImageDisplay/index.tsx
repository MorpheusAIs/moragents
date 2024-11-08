import React, { FC } from "react";
import { Box, Flex, Image, Spinner, Text } from "@chakra-ui/react";
import styles from "./index.module.css";

type ImageDisplayProps = {
  content: {
    success: boolean;
    service?: string;
    image?: string;
    error?: string;
  };
};

export const ImageDisplay: FC<ImageDisplayProps> = ({ content }) => {
  if (!content.success) {
    return (
      <Box className={styles.errorContainer}>
        <Text color="red.500">
          {content.error || "Failed to generate image"}
        </Text>
      </Box>
    );
  }

  if (!content.image) {
    return (
      <Flex className={styles.loadingContainer}>
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  return (
    <Box className={styles.imageContainer}>
      <Image
        src={`data:image/png;base64,${content.image}`}
        alt="Generated image"
        className={styles.generatedImage}
      />
      <Text className={styles.serviceTag}>
        Generated with {content.service}
      </Text>
    </Box>
  );
};
