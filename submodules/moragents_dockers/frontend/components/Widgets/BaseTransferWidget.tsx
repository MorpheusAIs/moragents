import React, { useState } from "react";
import {
  VStack,
  Box,
  Text,
  Select,
  Button,
  useColorModeValue,
  Heading,
  FormControl,
  FormLabel,
  Container,
  useToast,
  Input,
} from "@chakra-ui/react";
import { BASE_AVAILABLE_TOKENS } from "@/services/constants";

interface TransferConfig {
  token: string;
  amount: string;
  destinationAddress: string;
}

const BaseTransferWidget: React.FC = () => {
  const toast = useToast();
  const borderColor = useColorModeValue("gray.200", "gray.700");

  const [config, setConfig] = useState<TransferConfig>({
    token: "usdc",
    amount: "",
    destinationAddress: "",
  });

  const handleTransfer = async () => {
    // Validate destination address
    if (!config.destinationAddress) {
      toast({
        title: "Invalid Configuration",
        description: "Destination address is required",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Convert the string amount to a float only here
    const parsedAmount = parseFloat(config.amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Please enter a valid number greater than 0",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Attempt the transfer
    try {
      const response = await fetch("http://localhost:8080/base/transfer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          asset: config.token,
          amount: parsedAmount,
          destinationAddress: config.destinationAddress,
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        toast({
          title: "Transfer Successful",
          description: data.message,
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      toast({
        title: "Transfer Failed",
        description:
          error instanceof Error ? error.message : "Unknown error occurred",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Container maxW="container.md">
      <VStack align="stretch" spacing={6}>
        <Box textAlign="center">
          <Heading size="md" mb={3} color="white">
            Base Network Token Transfer
          </Heading>
          <Text fontSize="sm" color="white">
            Transfer tokens directly on the Base Network
          </Text>
        </Box>

        <VStack
          align="stretch"
          spacing={4}
          p={6}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="md"
        >
          <FormControl>
            <FormLabel color="white">Token</FormLabel>
            <Select
              value={config.token}
              onChange={(e) => setConfig({ ...config, token: e.target.value })}
              color="white"
              sx={{
                "& > option": {
                  color: "black",
                },
              }}
            >
              {BASE_AVAILABLE_TOKENS.map((token) => (
                <option key={token.symbol} value={token.symbol}>
                  {token.symbol} - {token.name}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl>
            <FormLabel color="white">Amount</FormLabel>
            <Input
              type="number"
              step="any"
              min="0"
              color="white"
              value={config.amount}
              onChange={(e) =>
                setConfig({
                  ...config,
                  amount: e.target.value,
                })
              }
            />
            <Text fontSize="sm" color="gray.400" mt={1}>
              Amount of {config.token} to transfer
            </Text>
          </FormControl>

          <FormControl>
            <FormLabel color="white">Destination Address</FormLabel>
            <Input
              value={config.destinationAddress}
              onChange={(e) =>
                setConfig({ ...config, destinationAddress: e.target.value })
              }
              placeholder="Enter destination address"
              color="white"
            />
          </FormControl>
        </VStack>

        <Button
          colorScheme="green"
          onClick={handleTransfer}
          size="md"
          width="100%"
        >
          Transfer Tokens
        </Button>
      </VStack>
    </Container>
  );
};

export default BaseTransferWidget;
