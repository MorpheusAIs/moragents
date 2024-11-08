import React, { FC } from "react";
import { Grid, GridItem, Text, Box } from "@chakra-ui/react";
import { Avatar } from "../Avatar";
import { Loader } from "../Loader";
import { availableAgents } from "../../config";

type LoadingIndicatorProps = {
  selectedAgent: string;
};

export const LoadingIndicator: FC<LoadingIndicatorProps> = ({
  selectedAgent,
}) => {
  return (
    <Grid
      templateAreas={`
        "avatar name"
        "avatar message"
      `}
      templateColumns={"0fr 3fr"}
      bg={"#020804"}
      color={"white"}
      borderRadius={4}
      mb={2}
      gap={2}
    >
      <GridItem area="avatar">
        <Avatar
          isAgent={true}
          agentName={availableAgents[selectedAgent]?.name || "Undefined Agent"}
        />
      </GridItem>
      <GridItem area="name">
        <Text
          sx={{
            fontSize: "16px",
            fontWeight: "bold",
            lineHeight: "125%",
            mt: 1,
            ml: 2,
          }}
        >
          {availableAgents[selectedAgent]?.name || "Undefined Agent"}
        </Text>
      </GridItem>
      <GridItem area="message">
        <Box sx={{ fontSize: "16px", lineHeight: "125%", mt: 4, mb: 5, ml: 2 }}>
          <Loader />
        </Box>
      </GridItem>
    </Grid>
  );
};
