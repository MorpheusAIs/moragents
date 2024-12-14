import React, { FC } from "react";
import { Grid, GridItem, Text, Box } from "@chakra-ui/react";
import { Avatar } from "../Avatar";
import { Loader } from "../Loader";
import styles from "./index.module.css";

export const LoadingIndicator: FC = () => {
  return (
    <Grid
      templateAreas={`"avatar name" "avatar message"`}
      templateColumns="0fr 3fr"
      className={styles.messageGrid}
    >
      <GridItem area="avatar">
        <Avatar isAgent={true} agentName="Finding the best agent" />
      </GridItem>
      <GridItem area="name">
        <Text className={styles.nameText}>Finding the best agent</Text>
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
