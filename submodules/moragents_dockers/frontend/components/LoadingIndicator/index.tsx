import React, { FC } from "react";
import { Grid, GridItem, Text, Box } from "@chakra-ui/react";
import { Avatar } from "../Avatar";
import { Loader } from "../Loader";
import { availableAgents } from "../../config";
import styles from "./index.module.css";

type LoadingIndicatorProps = {
  selectedAgent: string;
};

export const LoadingIndicator: FC<LoadingIndicatorProps> = ({
  selectedAgent,
}) => {
  const agentName =
    availableAgents[selectedAgent]?.name || "Finding the best agent";

  return (
    <Grid
      templateAreas={`"avatar name" "avatar message"`}
      templateColumns="0fr 3fr"
      className={styles.messageGrid}
    >
      <GridItem area="avatar">
        <Avatar isAgent={true} agentName={agentName} />
      </GridItem>
      <GridItem area="name">
        <Text className={styles.nameText}>{agentName}</Text>
      </GridItem>
      <GridItem area="message">
        <Box className={styles.messageText}>
          <Loader />
        </Box>
      </GridItem>
    </Grid>
  );
};

export default LoadingIndicator;
